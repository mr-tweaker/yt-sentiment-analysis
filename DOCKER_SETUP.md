# Quick Docker Setup Instructions

## For You (Building and Pushing)

### 1. Build the Image

```bash
# Replace 'your-registry' with your actual registry
docker build -t your-registry/youtube-sentiment-analysis:latest .
```

**Common registries:**
- Docker Hub: `your-username/youtube-sentiment-analysis:latest`
- GitHub: `ghcr.io/your-username/youtube-sentiment-analysis:latest`

### 2. Test Locally

```bash
docker run -d \
  --name youtube-sentiment-test \
  -p 8501:8501 \
  -e YOUTUBE_API_KEY=your_api_key \
  your-registry/youtube-sentiment-analysis:latest
```

Visit http://localhost:8501 to test.

### 3. Push to Registry

#### Docker Hub:
```bash
docker login
docker tag your-registry/youtube-sentiment-analysis:latest your-username/youtube-sentiment-analysis:latest
docker push your-username/youtube-sentiment-analysis:latest
```

#### GitHub Container Registry:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
docker tag your-registry/youtube-sentiment-analysis:latest ghcr.io/YOUR_USERNAME/youtube-sentiment-analysis:latest
docker push ghcr.io/YOUR_USERNAME/youtube-sentiment-analysis:latest
```

### 4. Share with Your Friend

Send them:
1. The image name: `your-registry/youtube-sentiment-analysis:latest`
2. The `WINDOWS_QUICK_START.md` file

## For Your Friend (Windows 11)

See `WINDOWS_QUICK_START.md` for detailed instructions.

**Quick version:**
1. Install Docker Desktop
2. Run: `docker pull YOUR_REGISTRY/youtube-sentiment-analysis:latest`
3. Run: `docker run -d --name youtube-sentiment -p 8501:8501 -e YOUTUBE_API_KEY=their_key YOUR_REGISTRY/youtube-sentiment-analysis:latest`
4. Open: http://localhost:8501

## Using the Build Script

```bash
# Build and optionally push
./build-and-push.sh your-registry latest

# Example for Docker Hub
./build-and-push.sh your-username latest
```
