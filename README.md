# Speech-to-Text & Diarization UI

This project provides a Streamlit-based user interface for transcribing audio and displaying diarization results using an OpenAI-compatible backend (like HPE MLIS or Whisper).

## Features

- **Connect to Custom Backend:** Configure API URL and Token.
- **Model Selection:** Automatically fetch available models from the backend.
- **Language Support:** Select from multiple languages (Greek, English, etc.).
- **Diarization Display:** Visualization of speaker segments if supported by the backend.
- **Dockerized & Helm Ready:** Easy deployment to Kubernetes.

## Deployment

### Prerequisites

- Kubernetes cluster
- Helm installed
- Backend service (HPE MLIS / OpenAI Compatible) running and accessible from the cluster.

### Deploy with Helm

1.  **Configure `charts/speech-ui/values.yaml`**:
    Update the `env.API_BASE_URL` to point to your backend service.

    ```yaml
    env:
      API_BASE_URL: "http://your-backend-service:8000/v1"
    ```

2.  **Install the Chart**:

    ```bash
    helm install speech-ui ./charts/speech-ui
    ```

3.  **Access the UI**:

    If using `NodePort`, find the port:
    ```bash
    kubectl get svc speech-ui
    ```
    Or port-forward locally:
    ```bash
    kubectl port-forward svc/speech-ui 8501:8501
    ```
    Open `http://localhost:8501` in your browser.

## Local Development

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the mock server (optional, for testing):
    ```bash
    python src/mock_api.py
    ```

3.  Run the Streamlit app:
    ```bash
    streamlit run src/app.py
    ```
