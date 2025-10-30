# 🎬 Twitch Auto-Clipper

An AI-powered system that automatically detects and clips highlights from Twitch streams and VODs.

## 🌟 Features

- **Multiple Detection Methods**:
  - Chat velocity analysis (spikes in chat activity)
  - Audio energy analysis (volume/excitement spikes)
  - AI vision analysis (game action detection)
  
- **AI-Powered Highlights**: Uses Claude's vision capabilities to identify exciting gameplay moments

- **Automatic Clipping**: Generates ready-to-share video clips

- **Future-Ready**: Built with subtitle generation in mind

## 🚀 Quick Start

### 1. Prerequisites

Install required system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip

# macOS
brew install ffmpeg python3

# Windows (using Chocolatey)
choco install ffmpeg python3
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Credentials

#### Twitch API (Required)
1. Go to https://dev.twitch.tv/console
2. Register your application
3. Get your **Client ID** and **Client Secret**

#### Anthropic API (Optional - for AI analysis)
1. Go to https://console.anthropic.com/
2. Create an API key
3. Set it as environment variable: `export ANTHROPIC_API_KEY="your-key"`

### 4. Basic Usage

#### Simple Mode (Chat + Audio Analysis)

```python
from twitch_clipper import TwitchHighlightClipper

# Initialize
clipper = TwitchHighlightClipper(
    client_id="YOUR_TWITCH_CLIENT_ID",
    client_secret="YOUR_TWITCH_CLIENT_SECRET"
)

# Create highlights from a VOD
clips = clipper.find_highlights(
    vod_url="https://www.twitch.tv/videos/2303742658",
    method='hybrid',  # 'chat', 'audio', or 'hybrid'
    num_clips=5,
    clip_duration=30
)

print(f"Created {len(clips)} clips!")
```

#### AI-Powered Mode (Recommended)

```python
from ai_clipper import SmartTwitchClipper

# Initialize with AI
clipper = SmartTwitchClipper(
    twitch_client_id="YOUR_TWITCH_CLIENT_ID",
    twitch_client_secret="YOUR_TWITCH_CLIENT_SECRET",
    anthropic_api_key="YOUR_ANTHROPIC_KEY"  # Optional
)

# Find highlights with AI vision analysis
clips = clipper.find_highlights_with_ai(
    vod_url="https://www.twitch.tv/videos/2303742658",
    game_name="Valorant",  # Helps AI understand context
    num_clips=5,
    clip_duration=30
)
```

## 📊 How It Works

### 1. Chat Velocity Analysis
Monitors Twitch chat replay data to detect spikes in message frequency. When chat activity increases dramatically (2x average), it indicates an exciting moment.

### 2. Audio Energy Analysis
Analyzes the audio track to find moments of high energy (loud moments, crowd reactions, excitement).

### 3. AI Vision Analysis (Advanced)
Uses Claude's vision API to:
- Detect in-game events (kills, achievements, score changes)
- Identify visual intensity (explosions, effects)
- Recognize dramatic situations
- Score each frame 0-10 for highlight potential

### 4. Clip Generation
Once highlights are identified:
1. Adds 5-10 second buffer before the highlight
2. Extracts the segment using FFmpeg
3. Saves as ready-to-share MP4 files

## 🎮 Detection Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Chat** | Fast, real community reactions | Requires chat data | Popular streamers |
| **Audio** | Works without chat, catches excitement | May miss visual highlights | Solo streamers |
| **AI Vision** | Most accurate, game-aware | Slower, costs API credits | High-quality curation |
| **Hybrid** | Balanced approach | More complex | General use |

## 💡 Advanced Usage

### Custom Highlight Detection

```python
# Adjust sensitivity
clipper.find_highlights(
    vod_url="...",
    method='chat',
    num_clips=10,
    clip_duration=45,  # Longer clips
    chat_sensitivity=1.5  # Lower = more sensitive
)
```

### Real-Time Stream Clipping

```python
# Monitor a live stream
clipper.monitor_live_stream(
    channel_name="shroud",
    check_interval=30,  # Check every 30 seconds
    auto_clip=True
)
```

### Batch Processing

```python
# Process multiple VODs
vods = [
    "https://www.twitch.tv/videos/123",
    "https://www.twitch.tv/videos/456",
    "https://www.twitch.tv/videos/789"
]

for vod in vods:
    clips = clipper.find_highlights(vod)
```

## 🎯 Future Features Roadmap

### Phase 1: Current ✅
- [x] VOD downloading
- [x] Chat velocity analysis
- [x] Audio energy analysis
- [x] AI vision analysis
- [x] Automatic clipping

### Phase 2: Coming Soon 🚧
- [ ] **Automatic Subtitles**: Using Whisper AI
- [ ] **Live stream monitoring**: Real-time clip generation
- [ ] **Multi-language support**: Subtitles in any language
- [ ] **Custom trained models**: Game-specific highlight detection
- [ ] **Web dashboard**: Easy-to-use interface

### Phase 3: Advanced 🔮
- [ ] **Automated upload**: Post to YouTube, TikTok, Twitter
- [ ] **Highlight compilation**: Create "best of" videos
- [ ] **Sponsor detection**: Skip sponsor segments
- [ ] **Face tracking**: Zoom into streamer reactions
- [ ] **Meme potential scoring**: Find viral-worthy moments

## 🔧 Configuration

Create a `config.json` file:

```json
{
  "twitch": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  },
  "anthropic": {
    "api_key": "your_api_key"
  },
  "settings": {
    "default_clip_duration": 30,
    "default_num_clips": 5,
    "output_directory": "./clips",
    "temp_directory": "/tmp"
  }
}
```

## 📝 Adding Subtitles (Coming Soon)

The subtitle feature will use OpenAI's Whisper:

```python
from subtitle_generator import add_subtitles

# Add subtitles to clips
for clip in clips:
    add_subtitles(
        video_path=clip,
        language='en',
        style='gaming'  # Different styles available
    )
```

## 🐛 Troubleshooting

### "yt-dlp failed to download VOD"
- Make sure yt-dlp is up to date: `pip install -U yt-dlp`
- Some VODs may be subscriber-only or deleted

### "No chat data available"
- Chat data requires third-party services or real-time recording
- Use 'audio' or 'hybrid' method instead

### "FFmpeg not found"
- Install FFmpeg: See prerequisites section
- Ensure it's in your system PATH

### "AI analysis too slow"
- Reduce `batch_size` parameter
- Use fewer frames (increase `interval`)
- Consider using 'hybrid' method without AI

## 💰 Cost Considerations

### Using AI Vision Analysis
- Claude API: ~$0.01-0.05 per VOD (depending on length)
- Analyzing 20 frames at ~$0.002/frame
- Budget-friendly for personal use

### Optimization Tips
- Use AI only for final curation
- Start with chat/audio detection
- Process shorter VOD segments
- Cache frame analysis results

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your clips!

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Credits

- FFmpeg for video processing
- yt-dlp for Twitch downloads
- Anthropic Claude for AI analysis
- Twitch API for stream data

---

**Questions?** Open an issue or reach out!

**Happy Clipping! 🎬✨**
