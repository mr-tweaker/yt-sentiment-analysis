# Screenshot Guide for Research Paper

## Container Status

✅ **Container is running:** `youtube-sentiment-screenshots`  
✅ **Dashboard URL:** http://localhost:8501  
✅ **API Key:** Pre-configured in container

## Access the Dashboard

1. **Open your web browser** and navigate to:
   ```
   http://localhost:8501
   ```

2. **Wait for the dashboard to load** (may take 10-15 seconds on first load)

## Screenshots Needed for Research Paper

Based on your research paper, you need screenshots for these figures:

### Figure 1: System Architecture Diagram
- **Location:** Create a diagram showing the 4-layer architecture
- **Tools:** Use draw.io, Lucidchart, or PowerPoint
- **Shows:** Presentation Layer → Application Layer → Data Layer → Infrastructure Layer
- **Include:** Data flow arrows, component labels

### Figure 2: Video Browser Tab
- **Location:** Dashboard → Video Browser tab
- **Steps:**
  1. Enter a YouTube channel ID/URL (e.g., `UC_x5XG1OV2P6uZZ5FSM9Ttw` for Google Developers)
  2. Set "Max Videos" to 5-10
  3. Set "Max Comments per Video" to 100-500
  4. Click "Fetch Videos"
  5. Wait for videos to load
  6. Take screenshot showing the video list with expandable cards

### Figure 3: Live Monitoring Tab
- **Location:** Dashboard → Live Monitoring tab
- **Steps:**
  1. First, add a video to monitoring (use Video Browser → "Add to Monitoring")
  2. Go to Live Monitoring tab
  3. Select a video from dropdown
  4. Click "🔄 Refresh Now" to fetch comments
  5. Wait for analysis to complete
  6. Take screenshot showing:
     - Sentiment trend chart (bar chart or stacked area)
     - Metric cards (Total Comments, Avg Sentiment, etc.)
     - Sample comments section

### Figure 4: Manual Check Analysis Results
- **Location:** Dashboard → Manual Check tab
- **Steps:**
  1. Enter a YouTube video ID or URL (e.g., `dQw4w9WgXcQ` or any popular video)
  2. Set comment limit (e.g., 200)
  3. Click "Analyze Video"
  4. Wait for analysis (may take 30-60 seconds)
  5. Take screenshot showing:
     - Sentiment Distribution histogram
     - Category Breakdown pie chart
     - Word Cloud (if generated)
     - Sample Comments section
     - Statistics table

### Figure 5: Correlation Heatmap
- **Location:** This would be generated from analysis results
- **Note:** You may need to run analysis and export data, then create heatmap in Python/Jupyter
- **Shows:** Correlation between sentiment, engagement metrics, comment length, emoji count

### Figure 6: Topic Modeling Visualization
- **Location:** Generated from topic modeling feature
- **Note:** May need to run advanced analysis or create visualization manually
- **Shows:** 5 topics with keywords and sentiment scores per topic

### Figure 7: Aspect-Based Sentiment Bar Chart
- **Location:** Generated from aspect analysis
- **Note:** May need to run advanced analysis or create visualization manually
- **Shows:** 12 aspects (video quality, audio, content, etc.) with sentiment scores

### Figure 8: 30-Day Sentiment Trends with Alerts
- **Location:** Dashboard → Sentiment History tab
- **Steps:**
  1. Ensure you have historical data (run monitoring for multiple days or use existing data)
  2. Go to Sentiment History tab
  3. Select a video with historical data
  4. Take screenshot showing:
     - Time series chart with sentiment trends
     - Alert markers (if any alerts were triggered)
     - Date range selector

### Figure 9: Case Study - Sentiment Recovery
- **Location:** Dashboard → Alerts tab or Sentiment History
- **Steps:**
  1. Look for videos with alert history
  2. Show sentiment trend before and after intervention
  3. May need to create a custom visualization showing recovery pattern

## Tips for Taking Good Screenshots

1. **Full Screen:** Use browser full-screen mode (F11) for cleaner screenshots
2. **High Resolution:** Ensure your display is set to high resolution
3. **Clean UI:** Close unnecessary browser tabs, hide bookmarks bar
4. **Consistent Style:** Use the same browser and zoom level (100%) for all screenshots
5. **Annotate:** Consider adding arrows or labels in PowerPoint/Image editor if needed
6. **File Format:** Save as PNG for best quality

## Quick Test Video IDs for Screenshots

- **Popular Tech Channel:** `UC_x5XG1OV2P6uZZ5FSM9Ttw` (Google Developers)
- **Popular Video:** `dQw4w9WgXcQ` (Rick Astley - Never Gonna Give You Up)
- **Educational:** Search for any educational channel ID

## Container Management Commands

```bash
# View logs
docker logs youtube-sentiment-screenshots

# Stop container
docker stop youtube-sentiment-screenshots

# Start container again
docker start youtube-sentiment-screenshots

# Remove container (when done)
docker rm -f youtube-sentiment-screenshots

# Restart container
docker restart youtube-sentiment-screenshots
```

## Troubleshooting

### Dashboard not loading?
- Wait 10-15 seconds for Streamlit to fully start
- Check logs: `docker logs youtube-sentiment-screenshots`
- Try accessing: http://127.0.0.1:8501 instead of localhost

### No videos found?
- Make sure API key is valid
- Try a different channel ID
- Check YouTube API quota limits

### Analysis taking too long?
- Reduce comment limit (try 50-100 comments first)
- Use smaller videos with fewer comments

### Need to reset?
```bash
docker restart youtube-sentiment-screenshots
```

## Next Steps

1. ✅ Container is running
2. Open http://localhost:8501 in your browser
3. Start taking screenshots following the guide above
4. Save screenshots in a dedicated folder for easy access
5. Insert screenshots into your research paper at the designated figure locations

Good luck with your research paper! 🎓
