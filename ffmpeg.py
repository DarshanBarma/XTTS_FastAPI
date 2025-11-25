import os
import random
import subprocess
import time
import json

VIDEO_DIR = "videos"
OUTPUT_DIR = "outputs"
AUDIO_FILE = "final.wav"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _pick_random_video() -> str:
    """Picks a random video file from VIDEO_DIR."""
    try:
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
    except Exception as e:
        print(f"Error picking random video: {e}")
        raise


def _get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds using ffprobe."""
    try:
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
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        raise


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _generate_subtitles_from_list(subtitles: list, output_path: str) -> str:
    """
    Generate SRT subtitle file from a list of subtitle dictionaries.
    
    Args:
        subtitles: List of dicts with 'text', 'start', and 'end' keys
                  Example: [
                      {'text': 'Hello', 'start': 0.0, 'end': 1.5},
                      {'text': 'World', 'start': 1.5, 'end': 3.0}
                  ]
        output_path: Path to save the SRT file
    """
    try:
        srt_content = []
        for i, sub in enumerate(subtitles, 1):
            start_str = _format_srt_time(sub['start'])
            end_str = _format_srt_time(sub['end'])
            srt_content.append(f"{i}\n{start_str} --> {end_str}\n{sub['text']}\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(srt_content))
        
        return output_path
    except Exception as e:
        print(f"Error generating subtitles from list: {e}")
        raise


def _generate_auto_subtitles(text: str, audio_duration: float, output_path: str) -> str:
    """
    Generate SRT with word-by-word timing based on audio duration.
    """
    try:
        words = text.split()
        if not words:
            words = [""]
        
        time_per_word = audio_duration / len(words)
        
        srt_content = []
        for i, word in enumerate(words):
            start_time = i * time_per_word
            end_time = (i + 1) * time_per_word
            
            start_str = _format_srt_time(start_time)
            end_str = _format_srt_time(end_time)
            
            srt_content.append(f"{i + 1}\n{start_str} --> {end_str}\n{word}\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(srt_content))
        
        return output_path
    except Exception as e:
        print(f"Error generating auto subtitles: {e}")
        raise


def create_video_with_audio(text: str = None,
                           subtitles: list = None,
                           subtitle_style: str = "modern",
                           background_opacity: float = 0.5) -> str:
    """
    Creates a YouTube Shorts video with styled subtitles.
    Background video runs smoothly without effects.
    
    Args:
        text: Simple text to auto-generate subtitles (word-by-word)
        subtitles: List of subtitle dicts with 'text', 'start', 'end' keys
                  Example: [
                      {'text': 'Hello world', 'start': 0.0, 'end': 1.5},
                      {'text': 'Welcome back', 'start': 1.5, 'end': 3.0}
                  ]
                  Use this for precise timing control!
        subtitle_style: Style preset ('modern', 'bold', 'minimal', 'gaming')
        background_opacity: Video brightness (0.0-1.0), lower = darker
        
    Returns:
        Path to the output video file
    """
    try:
        if not os.path.exists(AUDIO_FILE):
            raise FileNotFoundError(f"Audio file '{AUDIO_FILE}' not found.")

        if text is None and subtitles is None:
            raise ValueError("Either 'text' or 'subtitles' must be provided.")

        video_path = _pick_random_video()
        audio_duration = _get_audio_duration(AUDIO_FILE)
        print(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Generate subtitles
        timestamp = int(time.time())
        srt_filename = f"subtitles_{timestamp}.srt"
        srt_path = os.path.join(OUTPUT_DIR, srt_filename)
        
        if subtitles:
            print(f"Using custom subtitles with {len(subtitles)} entries")
            _generate_subtitles_from_list(subtitles, srt_path)
        else:
            print("Auto-generating word-by-word subtitles")
            _generate_auto_subtitles(text, audio_duration, srt_path)

        output_filename = f"final_{timestamp}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Subtitle style configurations
        styles = {
            "modern": (
                "Alignment=10,"
                "FontName=Arial Black,"
                "FontSize=24,"
                "Bold=1,"
                "PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,"
                "Outline=3,"
                "Shadow=2,"
                "MarginV=100"
            ),
            "bold": (
                "Alignment=10,"
                "FontName=Impact,"
                "FontSize=28,"
                "Bold=1,"
                "PrimaryColour=&H00FFFF00,"
                "OutlineColour=&H00000000,"
                "Outline=4,"
                "Shadow=3,"
                "MarginV=100"
            ),
            "minimal": (
                "Alignment=10,"
                "FontName=Helvetica,"
                "FontSize=22,"
                "Bold=1,"
                "PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,"
                "Outline=2,"
                "Shadow=1,"
                "MarginV=80"
            ),
            "gaming": (
                "Alignment=10,"
                "FontName=Arial Black,"
                "FontSize=26,"
                "Bold=1,"
                "PrimaryColour=&H0000FFFF,"  # Cyan/Yellow
                "OutlineColour=&H00000000,"
                "Outline=3,"
                "Shadow=2,"
                "MarginV=120"
            )
        }
        
        subtitle_force_style = styles.get(subtitle_style, styles["modern"])

        # Simple filter: just crop to 9:16 and adjust brightness
        # NO zoom, NO slow-motion - video runs at normal speed
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"eq=brightness=-{(1-background_opacity)*0.3},"
            f"format=yuv420p[dimmed];"
            f"[dimmed]subtitles={srt_path}:force_style='{subtitle_force_style}'[v]"
        )

        # FFmpeg command - video plays at normal speed
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
            "-movflags", "+faststart",
            output_path,
        ]

        print("\nCreating YouTube Short...")
        print(f"  - Subtitle style: {subtitle_style}")
        print(f"  - Background opacity: {background_opacity}")
        print(f"  - Video format: 1080x1920 (9:16)")
        print(f"  - Video runs at normal speed (no effects)\n")
        
        subprocess.run(cmd, check=True)

        # Clean up subtitle file
        if os.path.exists(srt_path):
            os.remove(srt_path)

        print(f"\n✓ Video created successfully: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error creating video with audio: {e}")
        # Clean up subtitle file on error
        if 'srt_path' in locals() and os.path.exists(srt_path):
            os.remove(srt_path)
        raise