import os
import random
import subprocess
import time
import json
import re

VIDEO_DIR = "videos"
OUTPUT_DIR = "outputs"
AUDIO_FILE = "final.wav"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _pick_random_video() -> str:
    """Picks a random video file from VIDEO_DIR."""
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


def _get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def _generate_word_subtitles(text: str, audio_duration: float, output_path: str) -> str:
    """
    Generate SRT subtitle file with word-by-word timing.
    Words appear progressively based on audio duration.
    """
    # Split text into words and clean them
    words = text.split()
    if not words:
        words = [""]
    
    # Calculate time per word
    time_per_word = audio_duration / len(words)
    
    srt_content = []
    for i, word in enumerate(words):
        start_time = i * time_per_word
        end_time = (i + 1) * time_per_word
        
        # Format time as SRT timestamp (HH:MM:SS,mmm)
        start_str = _format_srt_time(start_time)
        end_str = _format_srt_time(end_time)
        
        srt_content.append(f"{i + 1}\n{start_str} --> {end_str}\n{word}\n")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))
    
    return output_path


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_video_with_audio(text: str, 
                           subtitle_style: str = "modern",
                           background_opacity: float = 0.4,
                           add_zoom: bool = True) -> str:
    """
    Creates a professional YouTube Shorts video with styled subtitles.
    
    Args:
        text: The text to display as subtitles
        subtitle_style: Style preset ('modern', 'bold', 'minimal')
        background_opacity: Video background opacity (0.0-1.0), lower = darker
        add_zoom: Whether to add slow zoom effect to background
        
    Returns:
        Path to the output video file
    """
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"Audio file '{AUDIO_FILE}' not found.")

    video_path = _pick_random_video()
    
    # Get audio duration for subtitle timing
    audio_duration = _get_audio_duration(AUDIO_FILE)
    print(f"Audio duration: {audio_duration:.2f} seconds")
    
    # Generate word-by-word subtitles
    timestamp = int(time.time())
    srt_filename = f"subtitles_{timestamp}.srt"
    srt_path = os.path.join(OUTPUT_DIR, srt_filename)
    _generate_word_subtitles(text, audio_duration, srt_path)

    output_filename = f"final_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Subtitle style configurations
    styles = {
        "modern": (
            "Alignment=10,"  # Center alignment
            "FontName=Arial Black,"
            "FontSize=22,"
            "Bold=1,"
            "PrimaryColour=&H00FFFFFF,"  # White
            "OutlineColour=&H00000000,"  # Black outline
            "Outline=3,"
            "Shadow=2,"
            "MarginV=80"  # Bottom margin
        ),
        "bold": (
            "Alignment=10,"
            "FontName=Impact,"
            "FontSize=28,"
            "Bold=1,"
            "PrimaryColour=&H00FFFF00,"  # Yellow
            "OutlineColour=&H00000000,"
            "Outline=4,"
            "Shadow=3,"
            "MarginV=80"
        ),
        "minimal": (
            "Alignment=10,"
            "FontName=Helvetica,"
            "FontSize=24,"
            "Bold=1,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=2,"
            "Shadow=1,"
            "MarginV=70"
        )
    }
    
    subtitle_force_style = styles.get(subtitle_style, styles["modern"])

    # Build complex filter for YouTube Shorts
    # 1. Scale and crop video to 9:16 aspect ratio (1080x1920)
    # 2. Add zoom effect if enabled
    # 3. Reduce opacity for background
    # 4. Burn subtitles with custom style
    
    zoom_filter = ""
    if add_zoom:
        # Slow zoom from 1.0x to 1.1x scale over duration
        zoom_filter = f"zoompan=z='min(zoom+0.0005,1.1)':d={int(audio_duration * 30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,"
    
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"{zoom_filter}"
        f"format=yuv420p,"
        f"eq=brightness=-{(1-background_opacity)*0.3}:contrast={(0.7 + background_opacity*0.3)}[dimmed];"
        f"[dimmed]subtitles={srt_path}:force_style='{subtitle_force_style}'[v]"
    )

    # FFmpeg command with all enhancements
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", AUDIO_FILE,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-shortest",
        "-movflags", "+faststart",  # Optimize for streaming
        output_path,
    ]

    print("Creating YouTube Short with enhanced visuals...")
    print("Settings:")
    print(f"  - Subtitle style: {subtitle_style}")
    print(f"  - Background opacity: {background_opacity}")
    print(f"  - Zoom effect: {'enabled' if add_zoom else 'disabled'}")
    print(f"  - Video format: 1080x1920 (9:16)")
    
    subprocess.run(cmd, check=True)

    # Clean up subtitle file
    if os.path.exists(srt_path):
        os.remove(srt_path)

    print(f"\n✓ Video created successfully: {output_path}")
    return output_path