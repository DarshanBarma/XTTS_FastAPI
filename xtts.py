from TTS.api import TTS
import torch
import os

def generate_voice_clone():
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    tts.tts_to_file(
        text="In the dark hallway, something was breathing right behind me.",
        file_path="final.wav",
        language="en", 
        speaker_wav=["./voice_clones/sample.mp3"],
    )

    print("Saved: final.wav")
