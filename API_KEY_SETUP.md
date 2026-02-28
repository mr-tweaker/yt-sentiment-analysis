# API Key Configuration

## ✅ Preconfigured API Key

Your YouTube API key has been preconfigured in the project:

**Location**: `src/config.py`
**Key**: `AIzaSyBvlqgKW9aFMKpaZK-jOc8KvF_cC8QbOdw`

## Automatic Usage

The API key is automatically loaded when you run:

1. **Monitoring Dashboard**:
   ```bash
   streamlit run monitoring_dashboard.py
   ```
   - Key is preloaded in the sidebar
   - No need to enter it manually

2. **Monitoring Service**:
   ```bash
   python monitor_service.py
   ```
   - Automatically uses the preconfigured key

3. **Python Scripts**:
   ```python
   from src.youtube_monitor import YouTubeSentimentMonitor
   
   # No need to pass api_key - uses default
   monitor = YouTubeSentimentMonitor()
   ```

## Override (Optional)

You can still override the key if needed:

**Environment Variable**:
```bash
export YOUTUBE_API_KEY="different_key"
```

**Command Line**:
```bash
python monitor_service.py --api-key "different_key"
```

**In Code**:
```python
monitor = YouTubeSentimentMonitor(api_key="different_key")
```

## Video Title Display

All monitoring interfaces now automatically:
- ✅ Fetch video titles from YouTube API
- ✅ Display titles instead of IDs
- ✅ Cache video information for performance
- ✅ Show video details (title, channel, views) everywhere

**Example**: Instead of seeing `dQw4w9WgXcQ`, you'll see:
- **Title**: "Rick Astley - Never Gonna Give You Up (Official Video)"
- **Channel**: "RickAstleyVEVO"
- **ID**: `dQw4w9WgXcQ` (shown as reference)

## Security Note

⚠️ The API key is stored in source code. For production:
- Consider using environment variables
- Add `src/config.py` to `.gitignore` if needed
- Rotate keys periodically
