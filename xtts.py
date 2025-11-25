from TTS.api import TTS
import torch
import os

def generate_voice_clone(text:str) -> bool:
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    try:
        # Validate text input
        if not text or text.strip() == "":
            print("Error: Text is empty or None")
            return False
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using device:", device)
        print(f"Generating voice for text: {text[:50]}...")  # Print first 50 chars

        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        tts.tts_to_file(
            text=text.strip(),
            file_path="final.wav",
            language="en", 
            speaker_wav="./voice_clones/sample.mp3",  # Changed from list to single string
        )
        return True
    except Exception as e:
        print("Error during voice generation:", e)
        return False   
