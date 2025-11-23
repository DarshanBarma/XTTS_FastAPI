from TTS.api import TTS
import torch
import os

def generate_voice_clone(text:str) -> bool:
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using device:", device)

        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        tts.tts_to_file(
            text=text,
            file_path="final.wav",
            language="en", 
            speaker_wav=["./voice_clones/sample.mp3"],
        )
        return True
    except Exception as e:
        print("Error during voice generation:", e)
        return False   
