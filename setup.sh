#!/bin/bash

# Twitch Auto-Clipper Setup Script

echo "=================================="
echo "🎬 Twitch Auto-Clipper Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python is installed"
echo ""

# Check FFmpeg
echo "Checking FFmpeg..."
ffmpeg -version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: choco install ffmpeg"
    echo ""
    exit 1
fi
echo "✅ FFmpeg is installed"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Create config file
if [ ! -f "config.json" ]; then
    echo "Creating config.json from template..."
    cp config.example.json config.json
    echo "✅ Created config.json"
    echo ""
    echo "⚠️  IMPORTANT: Edit config.json and add your API keys:"
    echo "   1. Twitch Client ID and Secret (get from https://dev.twitch.tv/console)"
    echo "   2. Anthropic API Key (optional, get from https://console.anthropic.com/)"
    echo ""
else
    echo "✅ config.json already exists"
    echo ""
fi

# Create output directory
mkdir -p /mnt/user-data/outputs
echo "✅ Created output directory"
echo ""

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit config.json with your API keys:"
echo "   nano config.json"
echo ""
echo "2. Run a test:"
echo "   python3 twitch_clipper.py"
echo ""
echo "3. Or start the web interface:"
echo "   python3 web_app.py"
echo "   Then open http://localhost:5000 in your browser"
echo ""
echo "📖 See README.md for full documentation"
echo ""