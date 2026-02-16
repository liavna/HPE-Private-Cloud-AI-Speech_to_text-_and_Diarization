# Speech-to-Text & Diarization UI

This project provides a Streamlit-based user interface for transcribing audio and displaying diarization results using an OpenAI-compatible backend (like HPE MLIS or Whisper).

## Features

- **Connect to Custom Backend:** Configure API URL and Token.
- **Model Selection:** Automatically fetch available models from the backend.
- **Language Support:** Select from multiple languages (Greek, English, etc.).
- **Diarization Display:** Visualization of speaker segments if supported by the backend.
- **Dockerized & Helm Ready:** Easy deployment to Kubernetes.

## Directory Structure

```
.
├── Chart.yaml              # Helm chart metadata
├── values.yaml             # Default values
├── templates/              # Kubernetes templates
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── virtualservice.yaml
│   └── ...
├── build.sh                # Docker build script
└── docker/                 # Docker source files
    └── speech-ui/
        ├── Dockerfile
        ├── src/
        └── requirements.txt
```

## Deployment

### Prerequisites

- Kubernetes cluster
- Helm installed
- Backend service (HPE MLIS / OpenAI Compatible) running and accessible from the cluster.

### Build Docker Image

Use the provided script to build and push the image, and update the Helm values automatically.

```bash
# Make executable
chmod +x build.sh

# Build with default tag "latest"
./build.sh

# Build with custom tag
./build.sh 1.0.0
```

### Install with Helm

1.  **Configure `values.yaml`**:
    Update the `env.API_BASE_URL` to point to your backend service.

    ```yaml
    env:
      API_BASE_URL: "http://your-backend-service:8000/v1"
    ```

2.  **Install/Upgrade**:

    ```bash
    helm upgrade --install speech-ui . \
      --namespace voice-agent \
      --create-namespace \
      --atomic \
      --wait \
      --timeout 10m
    ```

3.  **Access the UI**:

    If using EZUA/Istio, the UI will be available via the VirtualService endpoint (default: `voice-ui.${DOMAIN_NAME}`).

    Alternatively, port-forward locally:
    ```bash
    kubectl port-forward svc/speech-ui -n voice-agent 8501:8501
    ```
    Open `http://localhost:8501` in your browser.
