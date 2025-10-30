"""
Automatic Subtitle Generator for Twitch Clips
Uses OpenAI's Whisper for speech-to-text
"""

import os
import subprocess
from typing import List, Dict
import json

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper not installed. Install with: pip install openai-whisper")


class SubtitleGenerator:
    """Generate and add subtitles to video clips"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize subtitle generator
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: fastest, least accurate
                       - base: good balance (recommended)
                       - large: most accurate, slowest
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper not installed")
        
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print("✓ Model loaded")
    
    def transcribe_video(self, video_path: str, language: str = None) -> Dict:
        """
        Transcribe audio from video
        
        Args:
            video_path: Path to video file
            language: Optional language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            Dict with transcription and segments
        """
        print(f"Transcribing {video_path}...")
        
        # Transcribe
        options = {}
        if language:
            options['language'] = language
        
        result = self.model.transcribe(video_path, **options)
        
        print(f"✓ Transcription complete")
        return result
    
    def generate_srt(self, segments: List[Dict], output_path: str):
        """
        Generate SRT subtitle file
        
        Args:
            segments: List of segments from Whisper transcription
            output_path: Where to save the SRT file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # SRT format:
                # 1
                # 00:00:00,000 --> 00:00:04,000
                # Subtitle text
                
                start = self._format_timestamp(segment['start'])
                end = self._format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        
        print(f"✓ SRT file saved to {output_path}")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def burn_subtitles(self, video_path: str, srt_path: str, output_path: str,
                       style: str = "gaming"):
        """
        Burn subtitles into video (hardcoded)
        
        Args:
            video_path: Input video
            srt_path: SRT subtitle file
            output_path: Output video with burned subtitles
            style: Subtitle style preset
        """
        print("Burning subtitles into video...")
        
        # Subtitle styles
        styles = {
            'gaming': "FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=0,Bold=1",
            'minimal': "FontName=Arial,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1",
            'youtube': "FontName=YouTube Sans,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1"
        }
        
        subtitle_style = styles.get(style, styles['gaming'])
        
        # FFmpeg command to burn subtitles
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles={srt_path}:force_style='{subtitle_style}'",
            '-c:a', 'copy',
            output_path,
            '-y'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video with subtitles saved to {output_path}")
    
    def add_soft_subtitles(self, video_path: str, srt_path: str, output_path: str):
        """
        Add soft subtitles (can be toggled on/off by viewer)
        
        Args:
            video_path: Input video
            srt_path: SRT subtitle file
            output_path: Output video with embedded subtitles
        """
        print("Adding soft subtitles...")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', srt_path,
            '-c', 'copy',
            '-c:s', 'mov_text',  # Subtitle codec for MP4
            output_path,
            '-y'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video with soft subtitles saved to {output_path}")
    
    def process_clip(self, video_path: str, output_path: str = None,
                    language: str = None, style: str = "gaming",
                    subtitle_type: str = "burn") -> str:
        """
        Complete workflow: transcribe and add subtitles
        
        Args:
            video_path: Input video
            output_path: Output video (optional, will auto-generate)
            language: Language code (optional, auto-detect if None)
            style: Subtitle style preset
            subtitle_type: 'burn' (hardcoded) or 'soft' (toggleable)
        
        Returns:
            Path to output video
        """
        if not output_path:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_subtitled{ext}"
        
        # Transcribe
        result = self.transcribe_video(video_path, language)
        
        # Generate SRT
        srt_path = video_path.replace('.mp4', '.srt')
        self.generate_srt(result['segments'], srt_path)
        
        # Add subtitles to video
        if subtitle_type == 'burn':
            self.burn_subtitles(video_path, srt_path, output_path, style)
        else:
            self.add_soft_subtitles(video_path, srt_path, output_path)
        
        return output_path


def add_subtitles_to_clips(clip_paths: List[str], language: str = None,
                          style: str = "gaming", subtitle_type: str = "burn") -> List[str]:
    """
    Convenience function to add subtitles to multiple clips
    
    Args:
        clip_paths: List of video file paths
        language: Optional language code
        style: Subtitle style preset
        subtitle_type: 'burn' or 'soft'
    
    Returns:
        List of paths to subtitled videos
    """
    generator = SubtitleGenerator(model_size="base")
    
    subtitled_clips = []
    for i, clip in enumerate(clip_paths, 1):
        print(f"\n[{i}/{len(clip_paths)}] Processing {os.path.basename(clip)}")
        
        output_path = clip.replace('.mp4', '_subtitled.mp4')
        subtitled_path = generator.process_clip(
            clip, output_path, language, style, subtitle_type
        )
        subtitled_clips.append(subtitled_path)
    
    print(f"\n✅ Added subtitles to {len(subtitled_clips)} clips!")
    return subtitled_clips


def main():
    """Example usage"""
    
    # Example: Add subtitles to existing clips
    clips = [
        '/mnt/user-data/outputs/highlight_1.mp4',
        '/mnt/user-data/outputs/highlight_2.mp4'
    ]
    
    subtitled = add_subtitles_to_clips(
        clips,
        language='en',
        style='gaming',
        subtitle_type='burn'  # or 'soft'
    )
    
    print("\nSubtitled clips:")
    for clip in subtitled:
        print(f"  - {clip}")


if __name__ == "__main__":
    main()