import io
import os
import tempfile

import pyttsx3
import whisper
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/voice", tags=["voice"])

_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")
    return _whisper_model


class SpeakRequest(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Accept an audio file and return the transcribed text using Whisper."""
    try:
        suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        model = _get_whisper_model()
        result = model.transcribe(tmp_path)
        return {"text": result["text"].strip()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.post("/speak")
async def speak_text(request: SpeakRequest):
    """Convert text to speech using pyttsx3 and return the audio as a WAV stream."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name

        engine = pyttsx3.init()
        engine.save_to_file(request.text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=jarvis_speech.wav"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
