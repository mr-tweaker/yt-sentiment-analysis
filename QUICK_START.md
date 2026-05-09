# Quick Start Guide

## YouTube API key

Set your YouTube Data API v3 key via environment variable:

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

## Running the Monitoring Dashboard

```bash
streamlit run monitoring_dashboard.py
```

The dashboard will:
- ✅ Display video titles instead of IDs for easier identification
- ✅ Cache video information for faster loading
- ✅ Show video details (title, channel, views) in all views
- ✅ Show a “Top Comments” feed with filters
- ✅ Show keyword/hashtag trends over time
- ✅ Show anomaly-based alerts with explainer details
- ✅ Show per-language sentiment (latest snapshot)
- ✅ **Live Monitoring** tab: full snapshot analytics (distribution, category charts when available, statistics, sample comments) and time-series after you’ve built history

## Running the Monitoring Service

```bash
python monitor_service.py --videos dQw4w9WgXcQ jNQXAC9IVRw
```

Or create a config file:
```bash
cp monitoring_config.json.example monitoring_config.json
# Edit monitoring_config.json to add your video IDs
python monitor_service.py
```

## Video Title Display

All monitoring interfaces now show:
- **Video Title** (instead of just ID)
- **Channel Name**
- **Video ID** (shown as reference)

Video information is automatically fetched and cached when you add a video to monitoring.

## Example: Adding a Video

1. Open the monitoring dashboard
2. Enter a video ID in the sidebar (e.g., `dQw4w9WgXcQ`)
3. Click "Add Video"
4. The video title will be automatically fetched and displayed
5. You'll see: **"Rick Astley - Never Gonna Give You Up (Official Video)"** instead of just the ID

## API Key Security

⚠️ **Never commit API keys.**

Use environment variables and rotate keys if they’re ever exposed.
