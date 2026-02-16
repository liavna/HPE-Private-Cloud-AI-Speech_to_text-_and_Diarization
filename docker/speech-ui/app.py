import streamlit as st
import requests
import os
from openai import OpenAI
import tempfile
import soundfile as sf
import numpy as np

# Page Config
st.set_page_config(page_title="Voice Agent - Speech & Diarization", layout="wide")

# Sidebar Configuration
st.sidebar.title("Configuration")

endpoint_url = st.sidebar.text_input("HPE MLIS Endpoint URL", placeholder="https://api.example.com")
auth_token = st.sidebar.text_input("Auth Token", type="password")

if "models" not in st.session_state:
    st.session_state.models = []

if st.sidebar.button("Check Models"):
    if not endpoint_url:
        st.sidebar.error("Please enter an Endpoint URL")
    else:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            # Try /v1/models first (OpenAI standard)
            response = requests.get(f"{endpoint_url}/v1/models", headers=headers, timeout=10)
            if response.status_code != 200:
                # Try just /models
                response = requests.get(f"{endpoint_url}/models", headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Handle various response formats (OpenAI uses 'data' list)
                model_list = data.get("data", data) if isinstance(data, dict) else data
                st.session_state.models = [m["id"] for m in model_list if isinstance(m, dict) and "id" in m]
                st.sidebar.success(f"Found {len(st.session_state.models)} models")
            else:
                st.sidebar.error(f"Failed to fetch models: {response.status_code} - {response.text}")
        except Exception as e:
            st.sidebar.error(f"Error connecting: {str(e)}")

# Model Selection
whisper_models = [m for m in st.session_state.models if "whisper" in m.lower()]
qwen_models = [m for m in st.session_state.models if "qwen" in m.lower()]

selected_whisper = st.sidebar.selectbox("Select Whisper Model", whisper_models if whisper_models else ["whisper-large-v3"])
selected_qwen = st.sidebar.selectbox("Select Qwen Model", qwen_models if qwen_models else ["qwen2.5-30b-instruct"])

st.sidebar.markdown("---")
st.sidebar.info("Note: Diarization support depends on the backend capabilities.")


# Main Application
st.title("🎙️ Voice Agent: Speech-to-Text & Diarization")

input_mode = st.radio("Select Input Source", ["File Upload", "Microphone"], horizontal=True)

audio_file = None

if input_mode == "File Upload":
    uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a", "ogg"])
    if uploaded_file:
        audio_file = uploaded_file

elif input_mode == "Microphone":
    audio_buffer = st.audio_input("Record Audio")
    if audio_buffer:
        audio_file = audio_buffer

if audio_file and st.button("Transcribe & Analyze"):
    if not endpoint_url:
        st.error("Please configure the Endpoint URL in the sidebar.")
    else:
        client = OpenAI(
            base_url=f"{endpoint_url}/v1",
            api_key=auth_token if auth_token else "dummy",
        )

        with st.spinner("Transcribing..."):
            try:
                # Save to temp file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_file.read())
                    tmp_file_path = tmp_file.name

                # Transcription Request
                # Using standard OpenAI format. Some backends support 'diarization=True' or similar extensions.
                # We'll try to send standard request first.
                with open(tmp_file_path, "rb") as audio:
                    transcript_response = client.audio.transcriptions.create(
                        model=selected_whisper,
                        file=audio,
                        response_format="verbose_json" # Request detailed JSON for segments
                    )

                # Check for segments/diarization in response
                transcript_text = ""
                segments = []

                if hasattr(transcript_response, "text"):
                     transcript_text = transcript_response.text

                if hasattr(transcript_response, "segments"):
                    segments = transcript_response.segments
                elif isinstance(transcript_response, dict) and "segments" in transcript_response:
                    segments = transcript_response["segments"]

                # Display Transcript
                st.subheader("Transcript")

                # Simple Diarization Display (if segments exist)
                if segments:
                    formatted_transcript = ""
                    for seg in segments:
                        start = seg.get('start', 0)
                        end = seg.get('end', 0)
                        text = seg.get('text', '')
                        # Some endpoints return 'speaker' field if diarization is enabled/supported
                        speaker = seg.get('speaker', 'Speaker ?')
                        formatted_transcript += f"**[{start:.2f}s - {end:.2f}s] {speaker}:** {text}\n\n"

                    st.markdown(formatted_transcript)
                    full_text_for_analysis = formatted_transcript # Use speaker-tagged text for analysis if available
                else:
                    st.write(transcript_text)
                    full_text_for_analysis = transcript_text

                # Analysis (Qwen)
                if selected_qwen:
                    with st.spinner("Analyzing with Qwen..."):
                        analysis_response = client.chat.completions.create(
                            model=selected_qwen,
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant. Analyze the following transcript. Identify speakers if possible (based on context or provided labels) and summarize the key points."},
                                {"role": "user", "content": full_text_for_analysis}
                            ]
                        )
                        analysis_text = analysis_response.choices[0].message.content
                        st.subheader("Analysis")
                        st.markdown(analysis_text)

                # Cleanup
                os.unlink(tmp_file_path)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                     os.unlink(tmp_file_path)

st.markdown("---")
st.caption("Powered by Streamlit, Whisper, and Qwen via HPE MLIS")
