# Windows 11 Quick Start Guide

This guide is for your friend who wants to run the YouTube Sentiment Analysis application on Windows 11.

## Step 1: Install Docker Desktop

1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop
2. Run the installer and follow the setup wizard
3. Restart your computer if prompted
4. Start Docker Desktop (you'll see a whale icon in the system tray)

## Step 2: Get Your YouTube API Key

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable "YouTube Data API v3"
4. Create credentials (API Key)
5. Copy your API key

## Step 3: Pull and Run the Container

Open PowerShell or Command Prompt and run:

```powershell
# Pull the image from registry
docker pull mrtweaker/youtube-sentiment-analysis:latest

# Run the container (replace YOUR_API_KEY with your actual key)
docker run -d `
  --name youtube-sentiment `
  -p 8501:8501 `
  -e YOUTUBE_API_KEY=YOUR_API_KEY `
  -v ${PWD}/output:/app/output `
  mrtweaker/youtube-sentiment-analysis:latest
```

**Image name: `mrtweaker/youtube-sentiment-analysis:latest`**

## Step 4: Access the Dashboard

1. Open your web browser
2. Go to: http://localhost:8501
3. You should see the YouTube Sentiment Analysis dashboard!

## Step 5: Using the Dashboard

1. **Enter API Key** (if not set via environment variable):
   - Look for the API key input in the sidebar
   - Paste your YouTube API key
   - The dashboard will remember it for this session

2. **Start Analyzing Videos**:
   - Go to the "Video Browser" tab
   - Enter a channel ID, username, or URL
   - Click "Fetch Videos"
   - Click "Analyze Now" on any video

3. **Monitor Sentiment**:
   - Use "Live Monitoring" to track sentiment over time
   - Use "Sentiment History" to view historical data
   - Use "Manual Check" to analyze individual videos

## Managing the Container

### Stop the Container
```powershell
docker stop youtube-sentiment
```

### Start the Container
```powershell
docker start youtube-sentiment
```

### View Logs
```powershell
docker logs youtube-sentiment
```

### Remove the Container
```powershell
docker stop youtube-sentiment
docker rm youtube-sentiment
```

### Update to Latest Version
```powershell
docker pull YOUR_REGISTRY/youtube-sentiment-analysis:latest
docker stop youtube-sentiment
docker rm youtube-sentiment
# Then run the docker run command again from Step 3
```

## Troubleshooting

### "Port 8501 is already in use"
- Another application is using port 8501
- Change the port: `-p 8502:8501` (then access via http://localhost:8502)

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running
- Check the system tray for the Docker icon

### "No comments found"
- Check your API key is correct
- Make sure YouTube Data API v3 is enabled
- Verify the video ID is correct
- Some videos have comments disabled

### Dashboard won't load
- Check if container is running: `docker ps`
- Check logs: `docker logs youtube-sentiment`
- Try accessing via `http://127.0.0.1:8501`

## Data Persistence

Your analysis data is saved in the `output` folder in the same directory where you ran the docker command. This includes:
- Databases (monitoring.db, youtube_sentiment_analysis.db)
- Reports
- Generated figures/charts

## Need Help?

Contact your friend who set up the Docker image, or check the main README.md file for more detailed documentation.
