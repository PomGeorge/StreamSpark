"""
Twitch Auto-Clipper
Automatically detects and clips highlights from Twitch streams using AI analysis
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import subprocess
import statistics
from collections import defaultdict

class TwitchHighlightClipper:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Twitch clipper
        
        Args:
            client_id: Your Twitch application client ID
            client_secret: Your Twitch application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Twitch API"""
        auth_url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(auth_url, params=params)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            print("✓ Authenticated with Twitch API")
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def get_headers(self) -> Dict:
        """Get headers for Twitch API requests"""
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def get_user_id(self, username: str) -> str:
        """Get Twitch user ID from username"""
        url = f"https://api.twitch.tv/helix/users?login={username}"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            data = response.json()['data']
            if data:
                return data[0]['id']
        raise Exception(f"Could not find user: {username}")
    
    def get_latest_vod(self, user_id: str) -> Dict:
        """Get the most recent VOD for a user"""
        url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first=1"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            data = response.json()['data']
            if data:
                return data[0]
        raise Exception("No VODs found")
    
    def get_chat_data(self, vod_id: str, duration_seconds: int) -> List[Dict]:
        """
        Fetch chat replay data for a VOD
        Note: This uses a third-party API since Twitch doesn't provide chat replay in their official API
        """
        print(f"Fetching chat data for VOD {vod_id}...")
        # Using a mock implementation - in production, you'd use something like:
        # - Twitch's IRC chat logs
        # - Third-party services like https://logs.ivr.fi/
        # - Or record chat data in real-time
        
        # For now, returning mock data structure
        return []
    
    def analyze_chat_velocity(self, chat_data: List[Dict], window_size: int = 10) -> List[Tuple[int, float]]:
        """
        Analyze chat message velocity to find highlight moments
        
        Args:
            chat_data: List of chat messages with timestamps
            window_size: Size of the sliding window in seconds
        
        Returns:
            List of (timestamp, spike_score) tuples
        """
        if not chat_data:
            print("⚠ No chat data available, using audio-only analysis")
            return []
        
        # Count messages per second
        message_counts = defaultdict(int)
        for msg in chat_data:
            timestamp = int(msg['timestamp'])
            message_counts[timestamp] += 1
        
        # Calculate rolling average and find spikes
        highlights = []
        timestamps = sorted(message_counts.keys())
        
        for i in range(len(timestamps)):
            current_time = timestamps[i]
            
            # Get counts in current window
            window_start = current_time - window_size
            window_counts = [message_counts[t] for t in timestamps 
                           if window_start <= t <= current_time]
            
            if len(window_counts) > 0:
                avg = statistics.mean(window_counts)
                current = message_counts[current_time]
                
                # Spike detection: current is significantly higher than average
                if current > avg * 2 and current > 10:
                    spike_score = current / (avg + 1)
                    highlights.append((current_time, spike_score))
        
        return highlights
    
    def download_vod(self, vod_url: str, output_path: str) -> str:
        """
        Download VOD using streamlink or yt-dlp
        
        Args:
            vod_url: Twitch VOD URL
            output_path: Where to save the video
        
        Returns:
            Path to downloaded video
        """
        print(f"Downloading VOD: {vod_url}")
        
        # Try using yt-dlp (more reliable for Twitch)
        try:
            cmd = [
                'yt-dlp',
                '-f', 'best',
                '-o', output_path,
                vod_url
            ]
            subprocess.run(cmd, check=True)
            print(f"✓ Downloaded VOD to {output_path}")
            return output_path
        except subprocess.CalledProcessError:
            print("⚠ yt-dlp failed, trying streamlink...")
            
        # Fallback to streamlink
        try:
            cmd = [
                'streamlink',
                '--output', output_path,
                vod_url,
                'best'
            ]
            subprocess.run(cmd, check=True)
            print(f"✓ Downloaded VOD to {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to download VOD: {e}")
    
    def analyze_audio_energy(self, video_path: str, segment_duration: int = 5) -> List[Tuple[int, float]]:
        """
        Analyze audio energy to find exciting moments
        
        Args:
            video_path: Path to video file
            segment_duration: Duration of each segment to analyze (seconds)
        
        Returns:
            List of (timestamp, energy_score) tuples
        """
        print("Analyzing audio energy...")
        
        # Extract audio using ffmpeg
        audio_path = video_path.replace('.mp4', '_audio.wav')
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            audio_path,
            '-y'
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠ Audio extraction failed: {e}")
            return []
        
        # Analyze audio energy using ffmpeg volumedetect
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-af', 'volumedetect',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse mean volume from output
        # In a full implementation, you'd use librosa or similar for detailed analysis
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return []
    
    def create_clip(self, video_path: str, start_time: int, duration: int, output_path: str):
        """
        Create a clip from the video
        
        Args:
            video_path: Source video path
            start_time: Start time in seconds
            duration: Clip duration in seconds
            output_path: Output clip path
        """
        print(f"Creating clip: {start_time}s for {duration}s")
        
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', video_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'fast',
            output_path,
            '-y'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Clip saved to {output_path}")
    
    def find_highlights(self, vod_url: str, method: str = 'chat', num_clips: int = 5, 
                       clip_duration: int = 30) -> List[str]:
        """
        Main function to find and create highlight clips
        
        Args:
            vod_url: Twitch VOD URL (e.g., https://www.twitch.tv/videos/123456789)
            method: Detection method ('chat', 'audio', or 'hybrid')
            num_clips: Number of highlight clips to create
            clip_duration: Duration of each clip in seconds
        
        Returns:
            List of paths to created clips
        """
        print(f"\n{'='*60}")
        print(f"🎬 Starting Twitch Auto-Clipper")
        print(f"{'='*60}\n")
        
        # Extract VOD ID from URL
        vod_id = vod_url.split('/')[-1]
        
        # Download VOD
        video_path = f'/tmp/twitch_vod_{vod_id}.mp4'
        self.download_vod(vod_url, video_path)
        
        # Analyze for highlights
        highlights = []
        
        if method in ['chat', 'hybrid']:
            chat_data = self.get_chat_data(vod_id, 0)
            chat_highlights = self.analyze_chat_velocity(chat_data)
            highlights.extend(chat_highlights)
        
        if method in ['audio', 'hybrid']:
            audio_highlights = self.analyze_audio_energy(video_path)
            highlights.extend(audio_highlights)
        
        # If no highlights detected, use simple time-based sampling
        if not highlights:
            print("⚠ No automatic highlights detected, using time-based sampling")
            # Get video duration
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            
            # Sample evenly across the video
            interval = duration / (num_clips + 1)
            highlights = [(int(interval * (i + 1)), 1.0) for i in range(num_clips)]
        
        # Sort by score and take top N
        highlights.sort(key=lambda x: x[1], reverse=True)
        top_highlights = highlights[:num_clips]
        
        # Create clips
        output_dir = '/mnt/user-data/outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        clip_paths = []
        for i, (timestamp, score) in enumerate(top_highlights):
            # Add buffer before the highlight moment
            start_time = max(0, timestamp - 5)
            output_path = f'{output_dir}/highlight_{vod_id}_{i+1}.mp4'
            
            self.create_clip(video_path, start_time, clip_duration, output_path)
            clip_paths.append(output_path)
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        
        print(f"\n{'='*60}")
        print(f"✓ Created {len(clip_paths)} highlight clips!")
        print(f"{'='*60}\n")
        
        return clip_paths


def main():
    """Example usage"""
    
    # You need to get these from https://dev.twitch.tv/console
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    
    # Initialize clipper
    clipper = TwitchHighlightClipper(CLIENT_ID, CLIENT_SECRET)
    
    # Example: Find highlights from a VOD
    vod_url = "https://www.twitch.tv/videos/123456789"
    
    clips = clipper.find_highlights(
        vod_url=vod_url,
        method='hybrid',  # Use both chat and audio analysis
        num_clips=5,
        clip_duration=30
    )
    
    for i, clip in enumerate(clips, 1):
        print(f"Clip {i}: {clip}")


if __name__ == "__main__":
    main()