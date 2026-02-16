import streamlit as st
import requests

st.set_page_config(page_title="Speech.AI - Advanced Analysis", page_icon="🎙️", layout="wide")

# Session State Initialization
if 'stt_ep' not in st.session_state: st.session_state.stt_ep = ""
if 'llm_ep' not in st.session_state: st.session_state.llm_ep = ""
if 'token' not in st.session_state: st.session_state.token = ""
if 'stt_models' not in st.session_state: st.session_state.stt_models = []
if 'llm_models' not in st.session_state: st.session_state.llm_models = []

st.title("🎙️ Speech.AI - Transcription, Diarization & Summary")

def get_models(endpoint, token):
    if not endpoint or not token:
        return []
    try:
        # Remove trailing slash if present for cleaner concatenation
        base_url = endpoint.rstrip('/')
        # OpenAI compatible endpoint for models
        url = f"{base_url}/v1/models"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data:
                return [m['id'] for m in data['data']]
            else:
                return []
        else:
            st.warning(f"Failed to fetch models from {endpoint}: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to {endpoint}: {e}")
        return []

with st.sidebar:
    st.header("⚙️ System Settings")
    st.session_state.stt_ep = st.text_input("Whisper Endpoint", value=st.session_state.stt_ep)
    st.session_state.llm_ep = st.text_input("Qwen LLM Endpoint", value=st.session_state.llm_ep)
    st.session_state.token = st.text_input("MLIS Token", type="password", value=st.session_state.token)

    if st.button("Connect & Fetch Models"):
        with st.spinner("Fetching models..."):
            st.session_state.stt_models = get_models(st.session_state.stt_ep, st.session_state.token)
            st.session_state.llm_models = get_models(st.session_state.llm_ep, st.session_state.token)
            if st.session_state.stt_models:
                st.success(f"Found {len(st.session_state.stt_models)} STT models")
            if st.session_state.llm_models:
                st.success(f"Found {len(st.session_state.llm_models)} LLM models")

    # STT Model Selection
    stt_model_options = st.session_state.stt_models if st.session_state.stt_models else ["whisper-1"]
    selected_stt_model = st.selectbox("Select STT Model", stt_model_options)

    # LLM Model Selection
    llm_model_options = st.session_state.llm_models if st.session_state.llm_models else ["qwen3-30b-a3b.v2"]
    selected_llm_model = st.selectbox("Select LLM Model", llm_model_options)

    st.divider()
    language_options = {"Auto Detect": None, "Hebrew": "he", "English": "en"}
    selected_lang = st.selectbox("Speech Language", list(language_options.keys()))

    st.header("🔍 Processing Options")
    do_diarization = st.checkbox("Enable Diarization (Speaker ID)", value=True)
    do_summary = st.checkbox("Generate Summary", value=True)

audio_data = st.audio_input("Record Audio")

if audio_data and st.button("🚀 Process with Speech.AI"):
    if not all([st.session_state.stt_ep, st.session_state.llm_ep, st.session_state.token]):
        st.error("Please fill in all endpoints and token in the sidebar.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        with st.status("Processing Pipeline...", expanded=True) as status:
            # Step 1: Transcription
            st.write(f"Step 1: Transcribing with {selected_stt_model}...")
            files = {"file": ("audio.wav", audio_data, "audio/wav")}
            data = {"model": selected_stt_model, "response_format": "text"}
            if language_options[selected_lang]: data["language"] = language_options[selected_lang]

            try:
                stt_url = f"{st.session_state.stt_ep.rstrip('/')}/v1/audio/transcriptions"
                resp_stt = requests.post(stt_url, headers=headers, files=files, data=data)

                if resp_stt.status_code != 200:
                     st.error(f"STT Error: {resp_stt.text}")
                     st.stop()

                transcript = resp_stt.text
                final_output = transcript

                # Step 2: Diarization
                if do_diarization:
                    st.write(f"Step 2: Identifying speakers with {selected_llm_model}...")
                    prompt_diarize = f"Please take this transcript and add speaker labels based on context:\n\n{transcript}"
                    llm_url = f"{st.session_state.llm_ep.rstrip('/')}/v1/chat/completions"
                    payload = {
                        "model": selected_llm_model,
                        "messages": [{"role": "user", "content": prompt_diarize}]
                    }
                    resp_llm = requests.post(llm_url, headers=headers, json=payload)

                    if resp_llm.status_code == 200:
                         final_output = resp_llm.json()['choices'][0]['message']['content']
                    else:
                         st.error(f"Diarization Error: {resp_llm.text}")

                # Step 3: Summary
                summary_output = ""
                if do_summary:
                    st.write("Step 3: Generating summary...")
                    prompt_sum = f"Summarize the following conversation in 3-5 bullet points:\n\n{final_output}"
                    llm_url = f"{st.session_state.llm_ep.rstrip('/')}/v1/chat/completions"
                    payload = {
                        "model": selected_llm_model,
                        "messages": [{"role": "user", "content": prompt_sum}]
                    }
                    resp_sum = requests.post(llm_url, headers=headers, json=payload)

                    if resp_sum.status_code == 200:
                        summary_output = resp_sum.json()['choices'][0]['message']['content']
                    else:
                        st.error(f"Summary Error: {resp_sum.text}")

                status.update(label="Analysis Complete!", state="complete")

                if do_summary:
                    st.subheader("📝 Summary")
                    st.info(summary_output)

                st.subheader("📜 Full Transcript")
                st.text_area("Final Result", value=final_output, height=300)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
