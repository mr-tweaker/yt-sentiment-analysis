# API Key Configuration (YouTube Data API v3)

## Recommended: environment variable

Set your key via `YOUTUBE_API_KEY` so it never lives in git history:

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

The key will be used automatically by:
- `monitoring_dashboard.py`
- `monitor_service.py`
- `src.youtube_monitor.YouTubeSentimentMonitor` (when `api_key` is not passed)

## Alternative: pass explicitly

In code:

```python
from src.youtube_monitor import YouTubeSentimentMonitor

monitor = YouTubeSentimentMonitor(api_key="YOUR_YOUTUBE_API_KEY")
```

## Getting a YouTube API key

1. Open Google Cloud Console
2. Create/select a project
3. Enable **YouTube Data API v3**
4. Create an **API key** under Credentials

## Key restrictions (strongly recommended)

In Google Cloud Console → Credentials → your API key:
- **API restrictions**: restrict to **YouTube Data API v3**
- **Application restrictions**:
  - Local dev: usually **None** (or your current IP)
  - Server: restrict by **server IP(s)**

If you see errors like “Requests … are blocked”, it’s usually due to incorrect restrictions.

## Security notes

- **Never commit API keys** to source control.
- This project redacts obvious secrets (like `key=...`) from dashboard error output, but you should still treat exposed keys as compromised and rotate them.
