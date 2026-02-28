# Quick Start Guide

## Preconfigured API Key

Your YouTube API key has been preconfigured in `src/config.py`. It will be automatically used when running:
- `monitoring_dashboard.py`
- `monitor_service.py`
- Any Python scripts using `YouTubeSentimentMonitor`

## Running the Monitoring Dashboard

```bash
streamlit run monitoring_dashboard.py
```

The dashboard will:
- ✅ Automatically use your preconfigured API key
- ✅ Display video titles instead of IDs for easier identification
- ✅ Cache video information for faster loading
- ✅ Show video details (title, channel, views) in all views

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

⚠️ **Note**: The API key is stored in `src/config.py`. For production use, consider:
- Using environment variables instead
- Adding `src/config.py` to `.gitignore` if committing to a public repository
- Rotating the key periodically
