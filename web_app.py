"""
Web Interface for Twitch Auto-Clipper
Simple Flask app to use the clipper through a browser
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import json
from threading import Thread
from twitch_clipper import TwitchHighlightClipper
from ai_clipper import SmartTwitchClipper

app = Flask(__name__)

# Store job status
jobs = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎬 Twitch Auto-Clipper</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            display: none;
        }
        .status.active {
            display: block;
        }
        .status h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .progress {
            margin: 10px 0;
            color: #666;
        }
        .clips {
            margin-top: 20px;
        }
        .clip-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .clip-item a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .clip-item a:hover {
            text-decoration: underline;
        }
        .info-box {
            background: #e8f4f8;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box strong {
            color: #667eea;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Twitch Auto-Clipper</h1>
        <p class="subtitle">Automatically find and clip the best moments from any Twitch stream</p>
        
        <div class="info-box">
            <strong>⚙️ Setup Required:</strong> Make sure you've configured your API keys in config.json
        </div>
        
        <form id="clipForm">
            <div class="form-group">
                <label for="vodUrl">Twitch VOD URL</label>
                <input type="text" id="vodUrl" name="vodUrl" 
                       placeholder="https://www.twitch.tv/videos/123456789" required>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="numClips">Number of Clips</label>
                    <input type="number" id="numClips" name="numClips" value="5" min="1" max="20">
                </div>
                
                <div class="form-group">
                    <label for="clipDuration">Clip Duration (seconds)</label>
                    <input type="number" id="clipDuration" name="clipDuration" value="30" min="10" max="120">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="method">Detection Method</label>
                    <select id="method" name="method">
                        <option value="hybrid">Hybrid (Chat + Audio)</option>
                        <option value="ai">AI Vision (Recommended)</option>
                        <option value="chat">Chat Analysis Only</option>
                        <option value="audio">Audio Analysis Only</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="gameName">Game Name (for AI mode)</label>
                    <input type="text" id="gameName" name="gameName" 
                           placeholder="e.g. Valorant, League of Legends">
                </div>
            </div>
            
            <button type="submit" id="submitBtn">🚀 Generate Highlights</button>
        </form>
        
        <div class="status" id="status">
            <h3>Processing...</h3>
            <div class="spinner"></div>
            <p class="progress" id="progress">Initializing...</p>
            <div class="clips" id="clips"></div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('clipForm');
        const status = document.getElementById('status');
        const progress = document.getElementById('progress');
        const clips = document.getElementById('clips');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                vodUrl: document.getElementById('vodUrl').value,
                numClips: parseInt(document.getElementById('numClips').value),
                clipDuration: parseInt(document.getElementById('clipDuration').value),
                method: document.getElementById('method').value,
                gameName: document.getElementById('gameName').value
            };
            
            status.classList.add('active');
            submitBtn.disabled = true;
            clips.innerHTML = '';
            
            try {
                const response = await fetch('/api/create-clips', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    pollJobStatus(data.job_id);
                } else {
                    progress.textContent = 'Error: ' + data.error;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                progress.textContent = 'Error: ' + error.message;
                submitBtn.disabled = false;
            }
        });
        
        async function pollJobStatus(jobId) {
            const response = await fetch(`/api/job-status/${jobId}`);
            const data = await response.json();
            
            progress.textContent = data.status;
            
            if (data.complete) {
                document.querySelector('.spinner').style.display = 'none';
                
                if (data.clips && data.clips.length > 0) {
                    progress.textContent = `✅ Generated ${data.clips.length} clips!`;
                    
                    clips.innerHTML = data.clips.map((clip, i) => `
                        <div class="clip-item">
                            <span>Highlight ${i + 1}</span>
                            <a href="${clip}" download>Download</a>
                        </div>
                    `).join('');
                } else {
                    progress.textContent = '❌ Failed to generate clips. Check console for errors.';
                }
                
                submitBtn.disabled = false;
            } else if (data.error) {
                progress.textContent = '❌ Error: ' + data.error;
                submitBtn.disabled = false;
            } else {
                setTimeout(() => pollJobStatus(jobId), 2000);
            }
        }
    </script>
</body>
</html>
"""

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'twitch': {
                'client_id': os.environ.get('TWITCH_CLIENT_ID', ''),
                'client_secret': os.environ.get('TWITCH_CLIENT_SECRET', '')
            },
            'anthropic': {
                'api_key': os.environ.get('ANTHROPIC_API_KEY', '')
            }
        }

def process_clips(job_id, vod_url, method, num_clips, clip_duration, game_name):
    """Background task to process clips"""
    try:
        config = load_config()
        
        jobs[job_id]['status'] = 'Initializing clipper...'
        
        if method == 'ai':
            clipper = SmartTwitchClipper(
                twitch_client_id=config['twitch']['client_id'],
                twitch_client_secret=config['twitch']['client_secret'],
                anthropic_api_key=config['anthropic']['api_key']
            )
            
            jobs[job_id]['status'] = 'Analyzing with AI...'
            clip_paths = clipper.find_highlights_with_ai(
                vod_url=vod_url,
                game_name=game_name,
                num_clips=num_clips,
                clip_duration=clip_duration
            )
        else:
            clipper = TwitchHighlightClipper(
                client_id=config['twitch']['client_id'],
                client_secret=config['twitch']['client_secret']
            )
            
            jobs[job_id]['status'] = 'Analyzing highlights...'
            clip_paths = clipper.find_highlights(
                vod_url=vod_url,
                method=method,
                num_clips=num_clips,
                clip_duration=clip_duration
            )
        
        # Convert paths to URLs
        clip_urls = [f'/clips/{os.path.basename(path)}' for path in clip_paths]
        
        jobs[job_id]['status'] = 'Complete!'
        jobs[job_id]['complete'] = True
        jobs[job_id]['clips'] = clip_urls
        
    except Exception as e:
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['complete'] = True

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/create-clips', methods=['POST'])
def create_clips():
    """API endpoint to start clip generation"""
    data = request.json
    
    job_id = f"job_{len(jobs)}"
    jobs[job_id] = {
        'status': 'Starting...',
        'complete': False,
        'clips': []
    }
    
    # Start background processing
    thread = Thread(
        target=process_clips,
        args=(
            job_id,
            data['vodUrl'],
            data['method'],
            data['numClips'],
            data['clipDuration'],
            data.get('gameName', '')
        )
    )
    thread.start()
    
    return jsonify({'success': True, 'job_id': job_id})

@app.route('/api/job-status/<job_id>')
def job_status(job_id):
    """Check job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])

@app.route('/clips/<filename>')
def serve_clip(filename):
    """Serve generated clips"""
    clip_path = os.path.join('/mnt/user-data/outputs', filename)
    if os.path.exists(clip_path):
        return send_file(clip_path, mimetype='video/mp4')
    return "Clip not found", 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 Twitch Auto-Clipper Web Interface")
    print("="*60)
    print("\n🌐 Server starting at: http://localhost:5000")
    print("\n⚙️  Make sure to configure config.json with your API keys!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)