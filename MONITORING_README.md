# Real-time YouTube Sentiment Monitoring

This feature enables continuous monitoring of YouTube video comments and tracks sentiment changes over time with alerting capabilities.

## Features

- ✅ **Real-time Comment Fetching**: Automatically fetches latest comments from YouTube videos
- ✅ **Sentiment Tracking**: Monitors sentiment changes over time
- ✅ **Alert System**: Smarter alerts (z-score/EWMA anomalies) with explainer details and example comments
- ✅ **Historical Data**: Stores all monitoring data in SQLite database
- ✅ **Interactive Dashboard**: Streamlit dashboard for monitoring and visualization
- ✅ **Scheduled Monitoring**: Background service for continuous monitoring
- ✅ **Top Comments Feed**: DB-backed feed with filters (latest snapshot)
- ✅ **Keyword & Hashtag Trends**: n-grams + time bucketing + time basis toggle
- ✅ **Per-language Sentiment**: language detection (optional) + per-language breakdown
- ✅ **Pluggable Sentiment Backend**: TextBlob (default) or Transformers (optional)
- ✅ **Live Monitoring (full snapshot)**: Latest DB snapshot per video with sentiment distribution, category pie/bar (when category metadata exists), statistics summary, sample comments, Top Comments, and per-language breakdown—backed by `get_latest_snapshot_full()`; time-series charts appear once you have non-empty history (e.g. multiple refreshes over hours)

## Setup

### 1. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

### 2. Install Dependencies

```bash
pip install google-api-python-client
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 3. Configure API Key

**Option 1: Environment Variable (Recommended)**
```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

**Option 2: Configuration File**
```bash
cp monitoring_config.json.example monitoring_config.json
# Edit monitoring_config.json and add your API key
```

## Usage

### Method 1: Interactive Dashboard (Recommended)

```bash
streamlit run monitoring_dashboard.py
```

Features:
- **Video Browser**: Browse and select videos from any YouTube channel
  - Enter channel ID, username, or full URL
  - Search videos by title
  - Add videos to monitoring list
  - Run quick sentiment analysis on any video
- **Live Monitoring**: Deep view of the **latest** snapshot (distribution, categories, stats, samples, languages) plus historical trend charts when data exists
- Add/remove videos to monitor
- View real-time sentiment trends
- Check alerts
- Manual video checks
- Historical analysis

### Method 2: Monitoring Service (Background)

```bash
python monitor_service.py
```

This runs continuously and monitors videos at specified intervals.

**Command-line options:**
```bash
# Basic usage
python monitor_service.py

# Custom configuration
python monitor_service.py --config my_config.json

# Override settings
python monitor_service.py --interval 15 --videos dQw4w9WgXcQ jNQXAC9IVRw

# Custom API key
python monitor_service.py --api-key YOUR_KEY
```

### Method 3: Python API

```python
from src.youtube_monitor import YouTubeSentimentMonitor

# Initialize monitor
monitor = YouTubeSentimentMonitor(
    api_key="YOUR_API_KEY",
    video_ids=["dQw4w9WgXcQ", "jNQXAC9IVRw"]
)

# Monitor a single video
result = monitor.monitor_video("dQw4w9WgXcQ", max_comments=100)

# Monitor all videos
results = monitor.monitor_all_videos(max_comments=100)

# Get sentiment history
history = monitor.get_sentiment_history("dQw4w9WgXcQ", hours=24)

# Get recent alerts
alerts = monitor.get_recent_alerts(hours=24)

# Browse videos from a channel
videos = monitor.fetch_channel_videos(
    channel_id="UCuAXFkgsw1L7xaCfnd5JJOw",  # Or use channel_username or channel_url
    max_results=50,
    order="date"
)

# Quick analysis of a video
result = monitor.analyze_video_comments("dQw4w9WgXcQ", max_comments=100)
print(f"Average sentiment: {result['avg_sentiment']}")
print(f"Positive comments: {result['positive_pct']:.1f}%")
```

## Video Browser Feature

The Video Browser allows you to:
1. **Fetch videos from any channel** by entering:
   - Channel ID (e.g., `UCuAXFkgsw1L7xaCfnd5JJOw`)
   - Channel username (e.g., `rickastley` or `@rickastley`)
   - Full channel URL (e.g., `https://www.youtube.com/@rickastley`)

2. **Browse and search** through fetched videos by title

3. **Select videos** for:
   - Adding to monitoring list (continuous tracking)
   - Quick sentiment analysis (one-time analysis)

4. **View analysis results** including:
   - Average sentiment score
   - Sentiment distribution chart
   - Top positive/negative comments
   - Comment statistics

### Finding Your Channel ID

1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Click **Settings** (gear icon)
3. Go to **Channel** > **Advanced settings**
4. Your Channel ID is shown under "Channel details"

Or use your channel URL format:
- `https://www.youtube.com/@YourUsername` → Username: `YourUsername`
- `https://www.youtube.com/channel/UC...` → Channel ID: `UC...`

## Configuration

Create `monitoring_config.json`:

```json
{
  "api_key": "YOUR_YOUTUBE_API_KEY",
  "video_ids": [
    "dQw4w9WgXcQ",
    "jNQXAC9IVRw"
  ],
  "interval_minutes": 30,
  "max_comments_per_video": 100,
  "check_alerts": true
}
```

### Configuration Options

- **api_key**: Your YouTube Data API v3 key
- **video_ids**: List of YouTube video IDs to monitor
- **interval_minutes**: How often to check for new comments (default: 30)
- **max_comments_per_video**: Maximum comments to fetch per check (default: 100)
- **check_alerts**: Whether to check for alert conditions (default: true)

## Alert System

The monitoring system supports both absolute thresholds and dynamic anomaly detection:

1. **Absolute thresholds** (optional):
   - Negative threshold (default: -0.3)
   - Positive threshold (default: 0.5)
2. **Anomaly detection**:
   - z-score anomalies based on recent baseline
   - EWMA anomalies (moving baseline)
   - volatility-aware “big move” alerts (Δ vs σ)

Alerts store structured JSON details and example comments to explain *why* an alert fired.

### Custom Alert Thresholds

You can customize thresholds when checking alerts:

```python
thresholds = {
    # absolute thresholds (optional)
    'negative_threshold': -0.3,
    'positive_threshold': 0.5,

    # anomaly detection
    'lookback_points': 20,
    'min_points': 6,
    'zscore_threshold': 2.5,
    'ewma_alpha': 0.3,
    'ewma_sigma': 2.5,
    'change_sigma': 2.5
}

alerts = monitor.check_sentiment_alerts(video_id, current_sentiment, thresholds)
```

## Database

Monitoring data is stored in `output/monitoring.db` with three tables:

1. **video_sentiment_history**: Historical sentiment metrics per video
2. **comment_snapshots**: Individual comment snapshots with sentiment (includes `published_at`, `parent_id`, `language`)
3. **alerts**: Alert history (includes `details` JSON)

### Query Examples

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('output/monitoring.db')

# Get all sentiment history
df = pd.read_sql_query('SELECT * FROM video_sentiment_history', conn)

# Get alerts for a specific video
df = pd.read_sql_query(
    'SELECT * FROM alerts WHERE video_id = ? ORDER BY timestamp DESC',
    conn,
    params=('dQw4w9WgXcQ',)
)
```

## API Rate Limits

YouTube Data API v3 has rate limits:
- **Default quota**: 10,000 units per day
- **CommentThreads.list**: 1 unit per request
- **Videos.list**: 1 unit per request

**Tips:**
- Use reasonable `max_comments` values (50-100)
- Set appropriate `interval_minutes` (30+ minutes recommended)
- Monitor fewer videos if hitting quota limits

## Running as a Service

### Linux/Mac (systemd)

Create `/etc/systemd/system/youtube-monitor.service`:

```ini
[Unit]
Description=YouTube Sentiment Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/YouTube-Sentiment_Analysis
Environment="YOUTUBE_API_KEY=your_key"
ExecStart=/usr/bin/python3 /path/to/YouTube-Sentiment_Analysis/monitor_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable youtube-monitor
sudo systemctl start youtube-monitor
```

### Windows (Task Scheduler)

Create a scheduled task to run `monitor_service.py` at startup or on a schedule.

## Troubleshooting

### API Key Issues
- Verify API key is correct
- Check that YouTube Data API v3 is enabled
- Ensure API key has proper permissions

### Rate Limit Errors
- Reduce `max_comments_per_video`
- Increase `interval_minutes`
- Monitor fewer videos

### No Comments Found
- Video may have comments disabled
- Video may be private/unlisted
- Check video ID is correct

## Examples

### Monitor a Single Video

```python
from src.youtube_monitor import YouTubeSentimentMonitor

monitor = YouTubeSentimentMonitor(
    api_key="YOUR_KEY",
    video_ids=["dQw4w9WgXcQ"]
)

# Check once
result = monitor.monitor_video("dQw4w9WgXcQ")
print(f"Average sentiment: {result['avg_sentiment']:.3f}")
```

### Continuous Monitoring

```python
import time

monitor = YouTubeSentimentMonitor(
    api_key="YOUR_KEY",
    video_ids=["dQw4w9WgXcQ"]
)

while True:
    results = monitor.monitor_all_videos()
    time.sleep(1800)  # Wait 30 minutes
```

## Integration with Main Analysis

The monitoring system integrates with the main analysis pipeline:

```python
from src.youtube_monitor import YouTubeSentimentMonitor
from src.data_loader import load_comments

# Monitor videos
monitor = YouTubeSentimentMonitor(api_key="YOUR_KEY", video_ids=["video_id"])
monitor.monitor_all_videos()

# Get historical data and analyze
history = monitor.get_sentiment_history("video_id", hours=24)
# Use history DataFrame with existing analysis functions
```

## Security Notes

- **Never commit API keys to version control**
- Use environment variables or secure config files
- Add `monitoring_config.json` to `.gitignore`
- Rotate API keys periodically
- The dashboard attempts to redact obvious secrets like `key=...` from error output, but you should still treat exposed keys as compromised.
