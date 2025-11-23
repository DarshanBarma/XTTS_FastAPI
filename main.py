from fastapi import FastAPI
from pydantic import BaseModel
from ffmpeg import create_video_with_audio
from xtts import generate_voice_clone

app = FastAPI()

class VoiceRequest(BaseModel):
    text: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate-voice/")
async def generate_voice(req: VoiceRequest):
    if(generate_voice_clone(req.text)):
        video_path = create_video_with_audio(req.text)
        return {"message": "Voice clone generated and saved as final.wav", "video": video_path}
    else:
        return {"message": "Failed to generate voice clone"}    