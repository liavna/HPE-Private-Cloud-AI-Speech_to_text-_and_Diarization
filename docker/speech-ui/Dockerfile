FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY speech_ai_app.py .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "speech_ai_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
