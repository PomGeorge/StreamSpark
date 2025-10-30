"""
Advanced AI-Powered Twitch Clipper
Uses vision AI and multimodal analysis for superior highlight detection
"""

import os
import json
import base64
import subprocess
from typing import List, Dict, Tuple
import anthropic
from PIL import Image
import io

class AIHighlightDetector:
    """Uses AI vision models to detect exciting moments in gameplay"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize AI detector
        
        Args:
            api_key: Anthropic API key for Claude
        """
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get('ANTHROPIC_API_KEY'))
    
    def extract_frames(self, video_path: str, interval: int = 5) -> List[str]:
        """
        Extract frames from video at regular intervals
        
        Args:
            video_path: Path to video file
            interval: Extract one frame every N seconds
        
        Returns:
            List of frame file paths
        """
        print(f"Extracting frames every {interval} seconds...")
        
        output_dir = '/tmp/frames'
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'fps=1/{interval}',
            f'{output_dir}/frame_%04d.jpg',
            '-y'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Get list of frames
        frames = sorted([
            os.path.join(output_dir, f) 
            for f in os.listdir(output_dir) 
            if f.endswith('.jpg')
        ])
        
        print(f"✓ Extracted {len(frames)} frames")
        return frames
    
    def analyze_frame_with_ai(self, frame_path: str, game_context: str = "") -> Dict:
        """
        Analyze a single frame using Claude's vision capabilities
        
        Args:
            frame_path: Path to frame image
            game_context: Optional context about what game is being played
        
        Returns:
            Dict with excitement_score (0-10) and reasoning
        """
        # Read and encode image
        with open(frame_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        # Construct prompt
        game_context_text = f" The game being played is {game_context}." if game_context else ""
        
        prompt = f"""Analyze this gaming/streaming frame for highlight potential.{game_context_text}

Rate the excitement level from 0-10 based on:
- Visual intensity (explosions, effects, action)
- UI indicators (kills, achievements, score changes)
- Unusual or impressive moments
- Dramatic situations

Return ONLY a JSON object with this format:
{{"excitement_score": <0-10>, "reasoning": "<brief explanation>"}}"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            # Parse response
            response_text = message.content[0].text
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"⚠ AI analysis failed: {e}")
            return {"excitement_score": 0, "reasoning": "Analysis failed"}
    
    def batch_analyze_frames(self, frames: List[str], game_context: str = "", 
                            batch_size: int = 10) -> List[Tuple[int, float, str]]:
        """
        Analyze multiple frames in batches
        
        Args:
            frames: List of frame paths
            game_context: Game being played
            batch_size: Number of frames to analyze (to control costs)
        
        Returns:
            List of (frame_index, score, reasoning) tuples
        """
        print(f"Analyzing frames with AI (using {batch_size} samples)...")
        
        # Sample frames if too many
        if len(frames) > batch_size:
            indices = [int(i * len(frames) / batch_size) for i in range(batch_size)]
            sampled_frames = [(i, frames[i]) for i in indices]
        else:
            sampled_frames = list(enumerate(frames))
        
        results = []
        for i, frame_path in sampled_frames:
            print(f"  Analyzing frame {i+1}/{len(sampled_frames)}...", end='\r')
            
            analysis = self.analyze_frame_with_ai(frame_path, game_context)
            score = analysis.get('excitement_score', 0)
            reasoning = analysis.get('reasoning', '')
            
            results.append((i, score, reasoning))
        
        print()  # New line after progress updates
        return results
    
    def identify_highlight_segments(self, frame_results: List[Tuple[int, float, str]], 
                                   frame_interval: int = 5,
                                   threshold: float = 7.0) -> List[Dict]:
        """
        Convert frame scores into highlight segments
        
        Args:
            frame_results: Results from batch_analyze_frames
            frame_interval: Seconds between frames
            threshold: Minimum score to consider a highlight
        
        Returns:
            List of highlight segments with timestamps
        """
        highlights = []
        
        for frame_idx, score, reasoning in frame_results:
            if score >= threshold:
                timestamp = frame_idx * frame_interval
                highlights.append({
                    'timestamp': timestamp,
                    'score': score,
                    'reasoning': reasoning
                })
        
        return highlights


class SmartTwitchClipper:
    """Enhanced clipper that combines chat, audio, and AI vision analysis"""
    
    def __init__(self, twitch_client_id: str, twitch_client_secret: str,
                 anthropic_api_key: str = None):
        """
        Initialize smart clipper
        
        Args:
            twitch_client_id: Twitch API client ID
            twitch_client_secret: Twitch API secret
            anthropic_api_key: Optional Anthropic API key for AI analysis
        """
        from twitch_clipper import TwitchHighlightClipper
        
        self.twitch_clipper = TwitchHighlightClipper(twitch_client_id, twitch_client_secret)
        self.ai_detector = AIHighlightDetector(anthropic_api_key) if anthropic_api_key else None
    
    def find_highlights_with_ai(self, vod_url: str, game_name: str = "",
                                num_clips: int = 5, clip_duration: int = 30) -> List[str]:
        """
        Find highlights using AI vision analysis
        
        Args:
            vod_url: Twitch VOD URL
            game_name: Name of the game being played
            num_clips: Number of clips to create
            clip_duration: Duration of each clip
        
        Returns:
            List of clip file paths
        """
        print(f"\n{'='*60}")
        print(f"🤖 AI-Powered Twitch Clipper")
        print(f"{'='*60}\n")
        
        if not self.ai_detector:
            print("⚠ AI detector not initialized, falling back to basic detection")
            return self.twitch_clipper.find_highlights(vod_url, 'hybrid', num_clips, clip_duration)
        
        # Extract VOD ID
        vod_id = vod_url.split('/')[-1]
        
        # Download VOD
        video_path = f'/tmp/twitch_vod_{vod_id}.mp4'
        self.twitch_clipper.download_vod(vod_url, video_path)
        
        # Extract frames for analysis
        frames = self.ai_detector.extract_frames(video_path, interval=10)
        
        # Analyze with AI
        frame_results = self.ai_detector.batch_analyze_frames(
            frames, 
            game_context=game_name,
            batch_size=20  # Adjust based on your budget
        )
        
        # Get highlight segments
        highlights = self.ai_detector.identify_highlight_segments(
            frame_results,
            frame_interval=10,
            threshold=7.0
        )
        
        print(f"\n✓ Found {len(highlights)} potential highlights")
        for i, h in enumerate(highlights[:num_clips], 1):
            print(f"  {i}. t={h['timestamp']}s (score: {h['score']}/10) - {h['reasoning']}")
        
        # Create clips
        output_dir = '/mnt/user-data/outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        clip_paths = []
        for i, highlight in enumerate(highlights[:num_clips], 1):
            start_time = max(0, highlight['timestamp'] - 10)  # Start 10s before
            output_path = f'{output_dir}/ai_highlight_{vod_id}_{i}.mp4'
            
            self.twitch_clipper.create_clip(video_path, start_time, clip_duration, output_path)
            clip_paths.append(output_path)
        
        # Cleanup frames
        for frame in frames:
            if os.path.exists(frame):
                os.remove(frame)
        
        # Cleanup video
        if os.path.exists(video_path):
            os.remove(video_path)
        
        print(f"\n{'='*60}")
        print(f"✓ Created {len(clip_paths)} AI-selected highlight clips!")
        print(f"{'='*60}\n")
        
        return clip_paths


def main():
    """Example usage of AI-powered clipper"""
    
    # Configuration
    TWITCH_CLIENT_ID = "your_twitch_client_id"
    TWITCH_CLIENT_SECRET = "your_twitch_client_secret"
    ANTHROPIC_API_KEY = "your_anthropic_api_key"  # Optional
    
    # Initialize smart clipper
    clipper = SmartTwitchClipper(
        twitch_client_id=TWITCH_CLIENT_ID,
        twitch_client_secret=TWITCH_CLIENT_SECRET,
        anthropic_api_key=ANTHROPIC_API_KEY
    )
    
    # Find highlights using AI
    clips = clipper.find_highlights_with_ai(
        vod_url="https://www.twitch.tv/videos/123456789",
        game_name="League of Legends",  # Helps AI understand context
        num_clips=5,
        clip_duration=30
    )
    
    print("\nGenerated clips:")
    for clip in clips:
        print(f"  - {clip}")


if __name__ == "__main__":
    main()