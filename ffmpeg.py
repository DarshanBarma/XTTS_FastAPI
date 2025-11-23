# ffmpeg.py
import os
import random
import subprocess
import time

VIDEO_DIR = "videos"
OUTPUT_DIR = "outputs"
AUDIO_FILE = "final.wav"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _pick_random_video() -> str:
    """
    Picks a random video file from VIDEO_DIR.
    """
    if not os.path.isdir(VIDEO_DIR):
        raise FileNotFoundError(f"Video directory '{VIDEO_DIR}' does not exist.")

    candidates = [
        f for f in os.listdir(VIDEO_DIR)
        if f.lower().endswith((".mp4", ".mov", ".mkv"))
    ]

    if not candidates:
        raise FileNotFoundError(f"No video files found in '{VIDEO_DIR}'.")

    chosen = random.choice(candidates)
    return os.path.join(VIDEO_DIR, chosen)


def _generate_subtitles(text: str, output_path: str) -> str:
    """
    Generate a simple SRT subtitle file from the given text.
    The subtitle will display for the entire duration of the video.
    Returns the path to the generated SRT file.
    """
    srt_content = f"""1
00:00:00,000 --> 00:10:00,000
{text}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    return output_path


def create_video_with_audio(text: str) -> str:
    """
    Combines final.wav audio with a random video from videos/ directory.
    Generates subtitles from the provided text and burns them into the video.
    The video is automatically cut to match the audio length.
    
    Args:
        text: The text to display as subtitles
        
    Returns:
        Path to the output video file
    """
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"Audio file '{AUDIO_FILE}' not found.")

    video_path = _pick_random_video()
    
    # Generate subtitles
    timestamp = int(time.time())
    srt_filename = f"subtitles_{timestamp}.srt"
    srt_path = os.path.join(OUTPUT_DIR, srt_filename)
    _generate_subtitles(text, srt_path)

    output_filename = f"final_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Build ffmpeg command with subtitles burned in
    # -shortest -> stop when the shortest stream ends (the audio),
    # so the video is automatically cut to match the audio length.
    cmd = [
        "ffmpeg",
        "-y",                # overwrite output
        "-i", video_path,    # input video
        "-i", AUDIO_FILE,    # input audio
        "-vf", f"subtitles={srt_path}",  # burn in subtitles
        "-map", "0:v:0",     # take video from first input
        "-map", "1:a:0",     # take audio from second input
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",         # cut video to match audio length
        output_path,
    ]

    print("Running ffmpeg command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Clean up subtitle file
    if os.path.exists(srt_path):
        os.remove(srt_path)

    print("Saved video:", output_path)
    return output_path
