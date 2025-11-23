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


def mux_audio_with_random_video(
    audio_path: str,
    subtitles_path: Optional[str] = None,
) -> str:
    """
    Use ffmpeg to combine:
    - random video from VIDEO_DIR
    - provided audio (audio_path)
    - optional subtitles (.srt)

    The video is automatically cut to match the audio length using -shortest.
    Returns the output video path.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file '{audio_path}' not found.")

    video_path = _pick_random_video()

    timestamp = int(time.time())
    output_filename = f"final_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Build ffmpeg command
    # -shortest -> stop when the shortest stream ends (usually the audio),
    # so the video is automatically cut to match the audio length.
    if subtitles_path:
        if not os.path.exists(subtitles_path):
            raise FileNotFoundError(f"Subtitles file '{subtitles_path}' not found.")

        cmd = [
            "ffmpeg",
            "-y",                # overwrite output
            "-i", video_path,    # input video
            "-i", audio_path,    # input audio
            "-vf", f"subtitles={subtitles_path}",  # burn in subtitles
            "-map", "0:v:0",     # take video from first input
            "-map", "1:a:0",     # take audio from second input
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]

    print("Running ffmpeg command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    print("Saved video:", output_path)
    return output_path
