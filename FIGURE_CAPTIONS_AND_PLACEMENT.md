# Figure Captions and Placement Guide for Research Paper

## Available Screenshots

Based on your screenshots folder, you have:
- ✅ Figure 1: System Architecture (generated)
- ✅ Figure 2: Video Browser tab
- ✅ Figure 3: Live Monitoring tab
- ✅ Figure 4: Manual Check results
- ✅ Figure 6: Topic modeling visualization
- ✅ Figure 8: 30-day sentiment trends

**Missing (need to create or capture):**
- ⚠️ Figure 5: Correlation heatmap
- ⚠️ Figure 7: Aspect-based sentiment bar chart
- ⚠️ Figure 9: Case study sentiment recovery

---

## Figure Captions (IEEE Format)

### Figure 1: System Architecture
**Placement:** Section III.A (Methodology - System Architecture), after paragraph describing the four-layer architecture

**Caption:**
```
Fig. 1. System architecture of the YouTube Sentiment Analysis framework, 
showing the four-layer design: Presentation Layer (Streamlit web application 
with five interactive tabs), Application Layer (modular Python pipeline with 
data loading, sentiment analysis, feature extraction, and visualization 
modules), Data Layer (SQLite database with four tables, YouTube Data API v3 
integration, and CSV batch support), and Infrastructure Layer (Docker 
containerization with Python 3.11-slim base image, Docker Compose 
orchestration, and health monitoring). The diagram illustrates data flow from 
user interactions through the application layers to persistent storage, with 
external integration via YouTube Data API v3.
```

**Shorter version (if space is limited):**
```
Fig. 1. System architecture showing four layers: Presentation (Streamlit 
dashboard), Application (Python analysis pipeline), Data (SQLite + YouTube API), 
and Infrastructure (Docker containerization).
```

---

### Figure 2: Video Browser Tab
**Placement:** Section III.F (Methodology - Interactive Dashboard), after the paragraph describing the Video Browser tab

**Caption:**
```
Fig. 2. Video Browser tab interface demonstrating channel-based video discovery. 
The screenshot shows the channel input field accepting Channel ID, username, or 
URL, with configurable options for maximum videos (5-10) and maximum comments per 
video (100-500). The interface displays fetched videos in expandable cards 
showing video metadata, with "Add to Monitoring" and "Analyze Now" buttons 
enabling one-click analysis with custom comment limits. This feature eliminates 
the need for manual video ID lookup, significantly improving user experience 
for content creators and analysts.
```

**Shorter version:**
```
Fig. 2. Video Browser tab showing channel input, video fetching interface, and 
expandable video cards with analysis options.
```

---

### Figure 3: Live Monitoring Tab
**Placement:** Section III.F (Methodology - Interactive Dashboard), after the paragraph describing the Live Monitoring tab

**Caption:**
```
Fig. 3. Live Monitoring tab displaying real-time sentiment analysis results. 
The interface shows a video selector dropdown populated with monitored videos 
(displaying titles instead of IDs), a refresh button for fetching latest 
comments, sentiment trend visualization (stacked area chart or bar chart 
depending on data points), metric cards displaying current sentiment statistics 
(total comments, average sentiment, category breakdown), and a sample comments 
section with color-coded sentiment indicators (green for positive, red for 
negative). The refresh functionality enables continuous monitoring with 
sub-second update latency.
```

**Shorter version:**
```
Fig. 3. Live Monitoring tab with video selector, sentiment trend charts, metric 
cards, and sample comments with real-time refresh capability.
```

---

### Figure 4: Manual Check Analysis Results
**Placement:** Section III.F (Methodology - Interactive Dashboard), after the paragraph describing the Manual Check tab

**Caption:**
```
Fig. 4. Manual Check tab comprehensive analysis results for a single video. 
The screenshot demonstrates the complete visualization suite including: (a) 
sentiment distribution histogram with 30-bin distribution and KDE overlay 
showing mean and median annotations, (b) category breakdown pie chart with 
five-tier sentiment classification (Very Positive, Positive, Neutral, Negative, 
Very Negative) with optimized label positioning to prevent overlap, (c) word 
cloud visualization filtered by sentiment (positive comments shown in green 
shades, negative in red), (d) sample comments section displaying color-coded 
comments with sentiment indicators, and (e) statistical summary table showing 
aggregate metrics including total comments, average sentiment, category counts, 
and engagement statistics. The interface provides export functionality for CSV 
downloads of analysis results.
```

**Shorter version:**
```
Fig. 4. Manual Check analysis results showing sentiment distribution histogram, 
category pie chart, word cloud, sample comments, and statistical summary table.
```

---

### Figure 5: Correlation Heatmap
**Placement:** Section V.C (Results - Feature Analysis), after the paragraph describing engagement correlation analysis

**Caption:**
```
Fig. 5. Correlation heatmap visualizing relationships between sentiment polarity, 
engagement metrics (likes, replies), comment length (characters, words), 
emoji count, and temporal features. The heatmap uses a diverging colormap 
(red for negative correlations, blue for positive correlations) with annotated 
correlation coefficients. Key findings include positive correlation between 
sentiment and likes (r=0.31, p<0.001), moderate negative correlation between 
comment length and sentiment (r=-0.28), and emoji presence correlating with 
increased engagement (34% average increase). The visualization enables quick 
identification of feature relationships for understanding comment patterns.
```

**Note:** This figure needs to be generated from your analysis data. You can create it using the correlation heatmap visualization from your analysis results.

---

### Figure 6: Topic Modeling Visualization
**Placement:** Section V.C (Results - Feature Analysis), after the paragraph describing topic modeling results

**Caption:**
```
Fig. 6. Topic modeling visualization using Latent Dirichlet Allocation (LDA) 
with five extracted topics. The diagram shows keyword clouds for each topic 
with font size proportional to term frequency, accompanied by average 
sentiment scores per topic. Example topics identified include "Product Quality" 
(avg sentiment +0.32), "Pricing Concerns" (avg sentiment -0.18), and 
"Customer Service" (avg sentiment -0.42). The visualization demonstrates how 
topic modeling enables identification of specific discussion themes driving 
overall sentiment, with topics explaining 47% of sentiment variance in the 
analyzed dataset.
```

**Shorter version:**
```
Fig. 6. Topic modeling visualization showing five extracted topics with keyword 
clouds and sentiment scores per topic.
```

---

### Figure 7: Aspect-Based Sentiment Bar Chart
**Placement:** Section V.C (Results - Feature Analysis), after the paragraph describing aspect-based sentiment analysis

**Caption:**
```
Fig. 7. Aspect-based sentiment analysis bar chart displaying sentiment scores 
for 12 identified aspects extracted from YouTube comments. The chart shows 
positive aspects (video quality: +0.41, content: +0.29, editing: +0.36) 
in green bars and negative aspects (ads: -0.68, clickbait: -0.82) in red bars. 
The visualization enables identification of specific features driving viewer 
satisfaction or dissatisfaction, providing actionable insights for content 
creators to focus improvement efforts on aspects with negative sentiment scores.
```

**Shorter version:**
```
Fig. 7. Aspect-based sentiment bar chart showing sentiment scores for 12 
identified aspects (video quality, audio, content, ads, clickbait, etc.).
```

**Note:** This figure needs to be generated from your aspect analysis results.

---

### Figure 8: 30-Day Sentiment Trends with Alerts
**Placement:** Section V.E (Results - Real-time Monitoring), after the paragraph describing monitoring evaluation

**Caption:**
```
Fig. 8. Thirty-day sentiment trend analysis for monitored videos showing 
temporal evolution of sentiment polarity over time. The time series chart 
displays sentiment scores (y-axis) plotted against dates (x-axis) with stacked 
area chart showing category distribution (Very Positive, Positive, Neutral, 
Negative, Very Negative) or line chart for aggregate sentiment. Alert markers 
indicate threshold breaches where sentiment dropped more than 20% or exceeded 
predefined thresholds, demonstrating the automated alert system's capability 
to detect significant sentiment changes. The visualization enables identification 
of sentiment patterns, trend directions, and critical events requiring 
intervention.
```

**Shorter version:**
```
Fig. 8. Thirty-day sentiment trends with alert markers showing sentiment 
evolution and threshold breaches over time.
```

---

### Figure 9: Case Study - Sentiment Recovery
**Placement:** Section V.E (Results - Real-time Monitoring), after the case study paragraph describing product launch video

**Caption:**
```
Fig. 9. Case study demonstrating sentiment recovery after content creator 
intervention. The visualization shows sentiment evolution for a product launch 
video: initial positive sentiment (+0.28) declining to negative (-0.15) over 
48 hours, triggering an automated alert 3 hours after threshold breach. 
Following content creator response (pinned comment addressing concerns), 
sentiment recovered to positive (+0.08) within 24 hours. The chart illustrates 
the practical utility of real-time monitoring and early detection, enabling 
proactive management of viewer sentiment through timely intervention. The case 
study validates the system's effectiveness in supporting content creators' 
decision-making processes.
```

**Shorter version:**
```
Fig. 9. Case study showing sentiment recovery pattern: initial decline, alert 
trigger, creator intervention, and subsequent recovery.
```

**Note:** This figure can be created from your monitoring history data or manually annotated screenshot.

---

## Placement Summary Table

| Figure | Section | Subsection | Location in Paper |
|--------|---------|------------|-------------------|
| **Fig. 1** | III. METHODOLOGY | A. System Architecture | After paragraph describing four-layer architecture |
| **Fig. 2** | III. METHODOLOGY | F. Interactive Dashboard | After Video Browser description |
| **Fig. 3** | III. METHODOLOGY | F. Interactive Dashboard | After Live Monitoring description |
| **Fig. 4** | III. METHODOLOGY | F. Interactive Dashboard | After Manual Check description |
| **Fig. 5** | V. RESULTS | C. Feature Analysis | After engagement correlation paragraph |
| **Fig. 6** | V. RESULTS | C. Feature Analysis | After topic modeling paragraph |
| **Fig. 7** | V. RESULTS | C. Feature Analysis | After aspect-based sentiment paragraph |
| **Fig. 8** | V. RESULTS | E. Real-time Monitoring | After monitoring evaluation paragraph |
| **Fig. 9** | V. RESULTS | E. Real-time Monitoring | After case study paragraph |

---

## IEEE Formatting Guidelines

1. **Figure Numbering:** Use "Fig. 1." format (not "Figure 1" or "Fig 1")
2. **Caption Placement:** Below the figure (centered or left-aligned)
3. **Caption Style:** 
   - First sentence: Brief description
   - Subsequent sentences: Detailed explanation
   - Use present tense ("shows", "demonstrates", "illustrates")
4. **Figure Size:** 
   - Single column: 3.5 inches wide
   - Double column: 7 inches wide
   - Maintain aspect ratio
5. **Resolution:** Minimum 300 DPI for print quality
6. **File Format:** PNG or PDF (vector preferred for diagrams)

---

## Quick Reference: Where to Insert Each Figure

### Section III: METHODOLOGY

**After III.A paragraph ending with:** "...four-layer architecture (Figure 1):"
- **Insert:** Fig. 1 (System Architecture)

**After III.F paragraph describing Video Browser:**
- **Insert:** Fig. 2 (Video Browser tab)

**After III.F paragraph describing Live Monitoring:**
- **Insert:** Fig. 3 (Live Monitoring tab)

**After III.F paragraph describing Manual Check:**
- **Insert:** Fig. 4 (Manual Check results)

### Section V: RESULTS AND EVALUATION

**After V.C paragraph about engagement correlation:**
- **Insert:** Fig. 5 (Correlation heatmap)

**After V.C paragraph about topic modeling:**
- **Insert:** Fig. 6 (Topic modeling visualization)

**After V.C paragraph about aspect-based sentiment:**
- **Insert:** Fig. 7 (Aspect-based sentiment bar chart)

**After V.E paragraph about monitoring evaluation:**
- **Insert:** Fig. 8 (30-day sentiment trends)

**After V.E case study paragraph:**
- **Insert:** Fig. 9 (Sentiment recovery case study)

---

## Tips for Inserting Figures in Word

1. **Insert → Pictures → This Device** (select PNG file)
2. **Right-click figure → Wrap Text → Top and Bottom** (or In Line with Text)
3. **Right-click figure → Format Picture → Size** (set width to 3.5" or 7" for columns)
4. **Insert caption:** References → Insert Caption → Label: Figure → Caption: paste from above
5. **Cross-reference:** References → Cross-reference → Reference type: Figure → Insert reference

---

## Missing Figures - How to Create

### Figure 5 (Correlation Heatmap)
- Use your existing `correlation_heatmap.png` from `output/figures/`
- Or regenerate using: `src/features/medium_features.py` → `create_sentiment_heatmap()`

### Figure 7 (Aspect-Based Sentiment)
- Generate from aspect analysis results
- Use matplotlib/seaborn bar chart
- Or create manually from your analysis data

### Figure 9 (Case Study)
- Use Sentiment History tab screenshot with annotated recovery pattern
- Or create custom visualization showing before/after intervention

---

**Last Updated:** Based on RESEARCH_PAPER_COMPRESSED.md structure
