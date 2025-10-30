#!/usr/bin/env python3
"""
Quick Start Example
Demonstrates the complete workflow from VOD to subtitled clips
"""

import os
import json

# Import our modules
from twitch_clipper import TwitchHighlightClipper
from ai_clipper import SmartTwitchClipper
from subtitle_generator import add_subtitles_to_clips

def load_config():
    """Load API keys from config"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found. Please run setup.sh first!")
        exit(1)

def example_basic_usage():
    """Example 1: Basic usage with chat/audio analysis"""
    print("\n" + "="*60)
    print("Example 1: Basic Highlight Detection")
    print("="*60 + "\n")
    
    config = load_config()
    
    # Initialize clipper
    clipper = TwitchHighlightClipper(
        client_id=config['twitch']['client_id'],
        client_secret=config['twitch']['client_secret']
    )
    
    # Find highlights
    vod_url = "https://www.twitch.tv/videos/2303742658"  # Replace with actual VOD
    
    try:
        clips = clipper.find_highlights(
            vod_url=vod_url,
            method='hybrid',  # Use both chat and audio
            num_clips=3,
            clip_duration=30
        )
        
        print(f"\n✅ Created {len(clips)} clips:")
        for i, clip in enumerate(clips, 1):
            print(f"   {i}. {clip}")
        
        return clips
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Your Twitch API keys are correct in config.json")
        print("  2. The VOD URL is valid and accessible")
        print("  3. You have ffmpeg and yt-dlp installed")
        return []

def example_ai_powered():
    """Example 2: AI-powered highlight detection"""
    print("\n" + "="*60)
    print("Example 2: AI-Powered Highlight Detection")
    print("="*60 + "\n")
    
    config = load_config()
    
    # Check if Anthropic API key is set
    if not config['anthropic'].get('api_key') or config['anthropic']['api_key'] == 'YOUR_ANTHROPIC_API_KEY_HERE':
        print("⚠️  Anthropic API key not set. Skipping AI example.")
        print("   Add your API key to config.json to use AI features.\n")
        return []
    
    # Initialize AI clipper
    clipper = SmartTwitchClipper(
        twitch_client_id=config['twitch']['client_id'],
        twitch_client_secret=config['twitch']['client_secret'],
        anthropic_api_key=config['anthropic']['api_key']
    )
    
    # Find highlights with AI
    vod_url = "https://www.twitch.tv/videos/2303742658"  # Replace with actual VOD
    
    try:
        clips = clipper.find_highlights_with_ai(
            vod_url=vod_url,
            game_name="Valorant",  # Specify the game for better context
            num_clips=3,
            clip_duration=30
        )
        
        print(f"\n✅ Created {len(clips)} AI-selected clips:")
        for i, clip in enumerate(clips, 1):
            print(f"   {i}. {clip}")
        
        return clips
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

def example_with_subtitles():
    """Example 3: Complete workflow with subtitles"""
    print("\n" + "="*60)
    print("Example 3: Highlights + Automatic Subtitles")
    print("="*60 + "\n")
    
    # First, create clips
    print("Step 1: Creating highlight clips...")
    clips = example_basic_usage()
    
    if not clips:
        print("⚠️  No clips created, skipping subtitle generation")
        return
    
    # Then add subtitles
    print("\nStep 2: Adding subtitles...")
    
    try:
        from subtitle_generator import SubtitleGenerator
        
        print("\n⚠️  Subtitle generation requires:")
        print("   1. pip install openai-whisper")
        print("   2. Significant processing time (minutes per clip)")
        print("   3. Good CPU/GPU for faster processing")
        
        response = input("\nContinue with subtitle generation? (y/n): ")
        
        if response.lower() == 'y':
            subtitled_clips = add_subtitles_to_clips(
                clips,
                language='en',
                style='gaming',
                subtitle_type='burn'
            )
            
            print(f"\n✅ Created {len(subtitled_clips)} subtitled clips:")
            for i, clip in enumerate(subtitled_clips, 1):
                print(f"   {i}. {clip}")
        else:
            print("\nSkipping subtitle generation.")
    
    except ImportError:
        print("\n⚠️  Whisper not installed. Install with:")
        print("   pip install openai-whisper")

def interactive_mode():
    """Interactive mode - ask user what they want to do"""
    print("\n" + "="*60)
    print("🎬 Twitch Auto-Clipper - Quick Start")
    print("="*60 + "\n")
    
    print("What would you like to do?")
    print("  1. Basic highlight detection (chat + audio)")
    print("  2. AI-powered highlight detection (recommended)")
    print("  3. Complete workflow (highlights + subtitles)")
    print("  4. Start web interface")
    print("  5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_ai_powered()
    elif choice == '3':
        example_with_subtitles()
    elif choice == '4':
        print("\nStarting web interface...")
        print("Open http://localhost:5000 in your browser\n")
        os.system("python3 web_app.py")
    elif choice == '5':
        print("\nGoodbye! 👋\n")
    else:
        print("\n❌ Invalid choice")

def main():
    """Main entry point"""
    
    # Check if config exists
    if not os.path.exists('config.json'):
        print("\n❌ config.json not found!")
        print("\nPlease run setup first:")
        print("  ./setup.sh")
        print("\nOr copy the example:")
        print("  cp config.example.json config.json")
        print("  # Then edit config.json with your API keys\n")
        return
    
    # Run interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()