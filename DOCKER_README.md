# Docker Setup Guide

This guide explains how to build, push, and run the YouTube Sentiment Analysis application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Hub account (or another container registry)
- YouTube API key

## Building and Pushing to Registry

### 1. Build the Docker Image

```bash
# Build the image
docker build -t your-registry/youtube-sentiment-analysis:latest .

# Replace 'your-registry' with your actual registry:
# - Docker Hub: your-username/youtube-sentiment-analysis:latest
# - GitHub Container Registry: ghcr.io/your-username/youtube-sentiment-analysis:latest
# - Other registries: registry.example.com/youtube-sentiment-analysis:latest
```

### 2. Test the Image Locally

```bash
# Run the container locally to test
docker run -d \
  --name youtube-sentiment-test \
  -p 8501:8501 \
  -e YOUTUBE_API_KEY=your_api_key_here \
  -v $(pwd)/output:/app/output \
  your-registry/youtube-sentiment-analysis:latest

# Access the dashboard at http://localhost:8501
# Stop and remove: docker stop youtube-sentiment-test && docker rm youtube-sentiment-test
```

### 3. Push to Docker Registry

#### Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag the image (replace 'your-username' with your Docker Hub username)
docker tag your-registry/youtube-sentiment-analysis:latest your-username/youtube-sentiment-analysis:latest

# Push to Docker Hub
docker push your-username/youtube-sentiment-analysis:latest
```

#### GitHub Container Registry (ghcr.io)

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Tag the image
docker tag your-registry/youtube-sentiment-analysis:latest ghcr.io/YOUR_GITHUB_USERNAME/youtube-sentiment-analysis:latest

# Push to GitHub Container Registry
docker push ghcr.io/YOUR_GITHUB_USERNAME/youtube-sentiment-analysis:latest
```

#### Other Registries

```bash
# Login to your registry
docker login your-registry.com

# Tag and push
docker tag your-registry/youtube-sentiment-analysis:latest your-registry.com/youtube-sentiment-analysis:latest
docker push your-registry.com/youtube-sentiment-analysis:latest
```

## Running on Windows 11

### Option 1: Using Docker Run (Simple)

1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Pull the Image**
   ```powershell
   docker pull your-registry/youtube-sentiment-analysis:latest
   ```

3. **Run the Container**
   ```powershell
   docker run -d `
     --name youtube-sentiment `
     -p 8501:8501 `
     -e YOUTUBE_API_KEY=your_api_key_here `
     -v ${PWD}/output:/app/output `
     your-registry/youtube-sentiment-analysis:latest
   ```

4. **Access the Dashboard**
   - Open browser: http://localhost:8501

5. **Stop the Container**
   ```powershell
   docker stop youtube-sentiment
   docker rm youtube-sentiment
   ```

### Option 2: Using Docker Compose (Recommended)

1. **Create a `.env` file** (optional, for API key)
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

2. **Update docker-compose.yml** with your registry image name:
   ```yaml
   image: your-registry/youtube-sentiment-analysis:latest
   ```

3. **Run with Docker Compose**
   ```powershell
   docker-compose up -d
   ```

4. **View Logs**
   ```powershell
   docker-compose logs -f
   ```

5. **Stop**
   ```powershell
   docker-compose down
   ```

## Environment Variables

You can set the YouTube API key in several ways:

1. **Command line** (shown above)
2. **Environment file** (`.env` file with Docker Compose)
3. **Docker Compose environment section**
4. **Inside the container** (via the dashboard UI)

## Persistent Data

The container uses volumes to persist:
- **Databases**: `./output/monitoring.db` and `./output/youtube_sentiment_analysis.db`
- **Reports**: `./output/reports/`
- **Figures**: `./output/figures/`

These are stored in the `./output` directory on your host machine.

## Troubleshooting

### Container won't start
```powershell
# Check logs
docker logs youtube-sentiment

# Check if port is already in use
netstat -ano | findstr :8501
```

### API Key not working
- Make sure the API key is set correctly
- Check the dashboard sidebar for API key input
- Verify the API key has YouTube Data API v3 enabled

### Can't access dashboard
- Ensure Docker Desktop is running
- Check firewall settings
- Try accessing via `http://127.0.0.1:8501` instead of `localhost`

### Permission issues (Linux/Mac)
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER ./output
```

## Updating the Container

```powershell
# Pull latest version
docker pull your-registry/youtube-sentiment-analysis:latest

# Stop and remove old container
docker stop youtube-sentiment
docker rm youtube-sentiment

# Run new version (same command as before)
docker run -d --name youtube-sentiment -p 8501:8501 ...
```

## Image Size Optimization

The current image is optimized but if you need to reduce size further:
- Use multi-stage builds
- Remove unnecessary system packages
- Use Alpine Linux base (may require additional dependencies)

## Security Notes

- Never commit API keys to version control
- Use environment variables or secrets management
- Regularly update base images for security patches
- Consider using Docker secrets for production deployments
