import streamlit as st
import os
from openai import OpenAI

# Set page config
st.set_page_config(
    page_title="HPE Private Cloud AI - Speech to Text",
    page_icon="🎙️",
    layout="wide"
)

def main():
    st.title("🎙️ HPE Private Cloud AI - Speech to Text Client")
    st.markdown("""
    This application connects to your internal OpenAI-compatible Whisper endpoint for transcription.
    Configure the connection details in the sidebar.
    """)

    # Sidebar Configuration
    with st.sidebar:
        st.header("Connection Settings")

        # Default values from environment variables
        default_base_url = os.getenv("WHISPER_BASE_URL", "http://whisper-service:8000/v1")
        default_api_key = os.getenv("WHISPER_API_KEY", "dummy-key")
        default_model = os.getenv("WHISPER_MODEL", "whisper-1")

        base_url = st.text_input("API Base URL", value=default_base_url, help="e.g., http://<ip>:8000/v1")
        api_key = st.text_input("API Key", value=default_api_key, type="password")
        model_name = st.text_input("Model Name", value=default_model, help="The model identifier expected by the server.")

        st.divider()
        st.info(f"Connecting to: {base_url}")

    # Main Content Area
    col1, col2 = st.columns([1, 1])

    audio_file = None

    with col1:
        st.subheader("1. Input Audio")
        tab1, tab2 = st.tabs(["Upload File", "Microphone"])

        with tab1:
            uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a", "ogg", "flac"])
            if uploaded_file:
                audio_file = uploaded_file
                st.audio(uploaded_file, format="audio/wav")

        with tab2:
            # Requires streamlit >= 1.40.0 for st.audio_input? Actually st.audio_input is experimental/new.
            # If not available, fallback to file upload only or use a component.
            # Checking recent streamlit docs, st.audio_input exists in recent versions.
            # We'll try to use it.
            try:
                mic_input = st.audio_input("Record from Microphone")
                if mic_input:
                    audio_file = mic_input
            except AttributeError:
                st.warning("Your Streamlit version might be too old for native audio input. Please use file upload.")

    with col2:
        st.subheader("2. Transcription Result")

        if audio_file is not None:
            if st.button("Transcribe", type="primary"):
                if not base_url:
                    st.error("Please provide an API Base URL.")
                else:
                    with st.spinner("Transcribing..."):
                        try:
                            # Initialize OpenAI client
                            client = OpenAI(
                                base_url=base_url,
                                api_key=api_key
                            )

                            # Call the API
                            # We use verbose_json to get segments/timestamps if available
                            response = client.audio.transcriptions.create(
                                model=model_name,
                                file=audio_file,
                                response_format="verbose_json"
                            )

                            # Display text
                            st.success("Transcription Complete!")
                            st.text_area("Transcript", value=response.text, height=300)

                            # Display raw segments/JSON if available (useful for debugging or advanced use)
                            with st.expander("View Raw Response (JSON)"):
                                st.json(response.model_dump())

                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                            st.exception(e)
        else:
            st.info("Please upload or record audio to begin.")

if __name__ == "__main__":
    main()
