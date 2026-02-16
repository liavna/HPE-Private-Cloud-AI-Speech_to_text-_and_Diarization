import streamlit as st
import os
from openai import OpenAI
import pandas as pd
import json

# Set page config
st.set_page_config(page_title="Speech & Diarization UI", layout="wide")

st.title("🎙️ Speech to Text & Diarization")
st.markdown("Connect to your HPE MLIS or OpenAI-compatible backend to transcribe audio.")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("🔌 Connection Settings")

    # Defaults for easier local testing, can be overridden
    default_url = os.getenv("API_BASE_URL", "http://localhost:8000/v1")

    api_base = st.text_input("API Base URL", value=default_url, help="The URL of your Whisper/MLIS service (e.g. http://host:port/v1)")
    api_key = st.text_input("API Token", type="password", help="Your authentication token")

    if "client" not in st.session_state:
        st.session_state.client = None

    if "models" not in st.session_state:
        st.session_state.models = []

    connect_btn = st.button("Connect & Fetch Models")

    if connect_btn:
        if not api_base:
            st.error("Please enter an API URL.")
        else:
            try:
                # Initialize client
                # If no key provided, use a dummy one if allowed by backend, or empty string
                token = api_key if api_key else "dummy-token"
                client = OpenAI(base_url=api_base, api_key=token)

                # Test connection by listing models
                models_response = client.models.list()

                # Store in session state
                st.session_state.client = client
                st.session_state.models = [m.id for m in models_response.data]
                st.success(f"Connected! Found {len(st.session_state.models)} models.")

            except Exception as e:
                st.error(f"Connection failed: {e}")
                st.session_state.client = None
                st.session_state.models = []

    # Model Selector
    if st.session_state.models:
        selected_model = st.selectbox("Select Model", st.session_state.models, index=0)
    else:
        selected_model = st.text_input("Model Name (Manual)", value="whisper-1", help="Enter model name manually if connection failed or listing is not supported")

# --- Main Interface ---

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a", "ogg", "flac"])

with col2:
    st.subheader("Options")
    # Common languages for Whisper
    languages = {
        "Greek": "el",
        "English": "en",
        "Hebrew": "he",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Auto Detect": None
    }

    selected_lang_name = st.selectbox("Language", list(languages.keys()), index=0) # Default Greek
    selected_lang_code = languages[selected_lang_name]

    enable_diarization = st.checkbox("Enable Diarization", value=False, help="Identify different speakers")

# Process Button
if st.button("Transcribe", type="primary", disabled=(not uploaded_file)):
    if not st.session_state.client:
         # Try to initialize just-in-time if manually entered details
         token = api_key if api_key else "dummy-token"
         st.session_state.client = OpenAI(base_url=api_base, api_key=token)

    client = st.session_state.client

    with st.spinner("Processing audio... this may take a while depending on file size and hardware"):
        try:
            # Prepare arguments
            kwargs = {
                "model": selected_model,
                "file": uploaded_file,
            }
            if selected_lang_code:
                kwargs["language"] = selected_lang_code

            # If diarization is requested, we need to pass it.
            # Standard OpenAI python client puts extra args in the body if we pass extra_body
            if enable_diarization:
                kwargs["extra_body"] = {"diarization": True}

            # Call API
            # Use with_raw_response to access custom fields (like 'segments' for diarization) that might be stripped by the strict Pydantic model
            api_response = client.audio.transcriptions.with_raw_response.create(**kwargs)

            # Get the raw JSON data
            raw_data = json.loads(api_response.http_response.content)

            # Display Raw Text
            result_text = raw_data.get("text", "")
            st.subheader("📝 Transcription")
            st.text_area("Result", value=result_text, height=300)

            # Display Diarization (if available)
            if "segments" in raw_data and raw_data["segments"]:
                st.subheader("🗣️ Diarization / Segments")
                segments_data = raw_data["segments"]

                # Create a nice conversation view
                for seg in segments_data:
                    start = seg.get("start", 0)
                    end = seg.get("end", 0)
                    text = seg.get("text", "")
                    speaker = seg.get("speaker", "Unknown")

                    st.markdown(f"**{speaker}** `[{start:.1f}s - {end:.1f}s]`")
                    st.info(text)

                # Expandable raw data
                with st.expander("View Raw Segments Data"):
                    st.json(segments_data)
            elif enable_diarization:
                st.info("Diarization was enabled but no segment data was found in the response. Ensure your backend supports it.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
