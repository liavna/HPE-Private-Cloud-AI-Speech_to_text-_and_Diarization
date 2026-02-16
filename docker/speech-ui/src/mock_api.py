from fastapi import FastAPI, UploadFile, File, Form, Header
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import random

app = FastAPI()

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "openai"

class ModelList(BaseModel):
    object: str = "list"
    data: List[Model]

@app.get("/v1/models")
async def list_models(authorization: Optional[str] = Header(None)):
    print(f"Listing models with auth: {authorization}")
    return ModelList(data=[
        Model(id="whisper-1"),
        Model(id="whisper-large-v3"),
        Model(id="custom-diarization-model")
    ])

@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form(...),
    language: Optional[str] = Form(None),
    # Some implementations might accept diarization as a form field
    diarization: Optional[bool] = Form(False)
):
    print(f"Transcribing file: {file.filename}, Model: {model}, Lang: {language}, Diarization: {diarization}")

    # Mock text
    text = "This is a simulated transcription of the Greek audio file. Hello world from the mock server."
    if language == "el":
        text = "Αυτό είναι מדומה (mock) תמלול ביוונית. Γειά σου κόσμε."

    response = {
        "text": text
    }

    # If diarization is requested or implied by model name, add segments
    if diarization or "diarization" in model:
        response["segments"] = [
            {
                "id": 0,
                "seek": 0,
                "start": 0.0,
                "end": 2.0,
                "text": "Hello there.",
                "speaker": "SPEAKER_00"
            },
            {
                "id": 1,
                "seek": 200,
                "start": 2.0,
                "end": 4.5,
                "text": "General Kenobi!",
                "speaker": "SPEAKER_01"
            },
            {
                "id": 2,
                "seek": 450,
                "start": 4.5,
                "end": 7.0,
                "text": "How are you today?",
                "speaker": "SPEAKER_00"
            }
        ]

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
