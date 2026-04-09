# YouTube Sentiment Analysis

A comprehensive Python project for analyzing sentiment of YouTube comments. This project uses NLP techniques to classify comments as positive, neutral, or negative, and provides extensive analysis features including topic modeling, engagement correlation, and interactive visualizations.

## Docker (Quick Run)

Pre-built image is available on **Docker Hub**:

- **Image:** [mrtweaker/youtube-sentiment-analysis](https://hub.docker.com/r/mrtweaker/youtube-sentiment-analysis)
- **Pull & run:**
  ```bash
  docker pull mrtweaker/youtube-sentiment-analysis:latest
  docker run -d --name youtube-sentiment -p 8501:8501 -e YOUTUBE_API_KEY=your_key mrtweaker/youtube-sentiment-analysis:latest
  ```
- Open the dashboard at **http://localhost:8501**. See [DOCKER_README.md](DOCKER_README.md) and [WINDOWS_QUICK_START.md](WINDOWS_QUICK_START.md) for details.

**ML-enabled image (optional)**:

The default Docker image is kept lightweight and does **not** include `torch/transformers`.
If you want an ML-enabled image, build locally with:

```bash
docker build --build-arg INCLUDE_ML=1 -t mrtweaker/youtube-sentiment-analysis:ml .
```

## Overview

This project provides:
- **Sentiment Analysis**: Pluggable sentiment backends (TextBlob default; optional Transformers backend)
- **Data Processing**: Automated data loading, cleaning, and preprocessing
- **Advanced Features**: 17+ enhancement features including emoji analysis, topic modeling, network graphs, and more
- **Visualizations**: Automated generation of charts, word clouds, and heatmaps
- **Reporting**: Automated report generation and database export
- **Modular Design**: Well-organized Python modules for easy extension

## Tech Stack

- Python 3.8+
- Pandas, NumPy
- Seaborn, Matplotlib
- TextBlob (default sentiment polarity)
- Optional: Transformers + Torch (more accurate sentiment)
- Optional: langdetect (language detection)
- WordCloud (for visualization)

## Dataset

- Expected CSV file: `UScomments.csv` (columns typically include `video_id`, `comment_text`, `likes`, `replies`).
- Place the CSV in a convenient local path and update the path inside the notebook before running.
- Suggested sources: public datasets on Kaggle or data exported via the YouTube API. Ensure you have the right to use and share the data.

## Project Structure

```
YouTube-Sentiment_Analysis/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── data_loader.py          # Data loading and preprocessing
│   ├── sentiment_analyzer.py   # Sentiment analysis functions
│   ├── visualizations.py       # Visualization functions
│   ├── utils.py                # Utility functions
│   └── features/
│       ├── __init__.py
│       ├── basic_features.py   # Basic enhancement features
│       ├── medium_features.py  # Medium complexity features
│       └── advanced_features.py # Advanced features (topic modeling, etc.)
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── ENHANCEMENT_IDEAS.md        # Feature ideas document
├── YOU TUBE SENTIMENT ANALYSIS PROJECT.ipynb  # Original notebook
├── data/                       # Data directory (create and add your CSV files here)
└── output/                     # Output directory (auto-created)
    ├── figures/                # Generated visualizations
    ├── reports/                # Generated reports
    └── youtube_sentiment_analysis.db  # SQLite database
```

## Setup

1. **Clone or download this repository**

2. **Create and activate a virtual environment** (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

Optional (language detection + transformer sentiment backend):

```bash
pip install -r requirements-ml.txt
```

4. **Set your YouTube API key** (for monitoring dashboard):

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

Optional:

```bash
# Switch sentiment backend (default: textblob)
export SENTIMENT_BACKEND=transformer
export TRANSFORMER_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
```

4. **Configure data paths**:

Edit `src/config.py` and update the file paths to match your data location:
- `COMMENTS_CSV`: Path to your comments CSV file
- `VIDEOS_CSV`: Path to your video metadata CSV (optional)
- `ADDITIONAL_DATA_DIR`: Directory with additional data files (optional)

Or create a `data/` directory and place your CSV files there.

## Usage

### Running the Complete Analysis

Simply run the main script:

```bash
python main.py
```

### Running the Monitoring Dashboard

The monitoring dashboard includes:
- ✅ **Video Browser**: fetch videos by channel ID/username/URL
- ✅ **Top Comments feed**: newest/most-liked with filters (latest snapshot)
- ✅ **Keyword & hashtag trends**: n-grams + time bucketing + snapshot vs published time basis
- ✅ **Smarter alerts**: anomaly detection (z-score/EWMA) with explainer details + example comments
- ✅ **Per-language sentiment**: language breakdown with full language names (when `langdetect` installed)
- ✅ **API key redaction**: best-effort redaction of `key=...` in error output

```bash
streamlit run monitoring_dashboard.py
```

**Note**: Don’t hardcode API keys in source. Use `YOUTUBE_API_KEY` env var.

This will:
1. Load and preprocess your data
2. Perform sentiment analysis
3. Run all enhancement features
4. Generate visualizations
5. Create reports
6. Export results to SQLite database

### Using Individual Modules

You can also import and use individual modules:

```python
from src.data_loader import load_comments
from src.sentiment_analyzer import analyze_sentiment_batch
from src.visualizations import plot_sentiment_distribution

# Load data
comments = load_comments()

# Analyze sentiment
comments = analyze_sentiment_batch(comments)

# Visualize
plot_sentiment_distribution(comments)
```

### Running the Original Notebook

The original Jupyter notebook is still available:
```bash
jupyter notebook "YOU TUBE SENTIMENT ANALYSIS PROJECT.ipynb"
```

Minimal example of computing polarity with TextBlob:

```python
from textblob import TextBlob
TextBlob("This video is absolutely amazing!").sentiment.polarity  # returns value in [-1, 1]
```

## Features

### Core Features
- **Sentiment Analysis**: TextBlob-based polarity scoring (−1 to 1)
- **Data Processing**: Automated loading, cleaning, and merging
- **Visualization**: Multiple chart types (histograms, word clouds, heatmaps, etc.)

### Enhancement Features (17+ implemented)

**Basic Features:**
1. Sentiment-Emoji Correlation
2. Comment Length vs. Sentiment Analysis
3. Sentiment Score Distribution with Statistical Insights
4. Sentiment-Based Comment Ranking
5. Sentiment Polarity Binning and Visualization

**Medium Features:**
6. Sentiment-Engagement Correlation Analysis
7. Category-Specific Sentiment Deep Dive
8. Comparative Sentiment Analysis: Channels
9. Interactive Word Clouds with Sentiment Coloring
10. Sentiment Heatmap by Category and Channel

**Advanced Features:**
11. Time-Based Sentiment Trends
12. Topic Modeling with Sentiment (LDA)
13. Network Graph of Related Comments
14. Aspect-Based Sentiment Analysis
15. Automated Report Generation
16. Export to Database (SQLite)
17. Interactive Dashboard Template (Streamlit)

## Methodology

- **Sentiment Metric**: TextBlob polarity in \([-1, 1]\)
  - Negative (< 0), Neutral (≈ 0), Positive (> 0)
- **Processing**:
  - Drop missing `comment_text`
  - Batch processing with progress tracking
  - Automatic data type conversion and cleaning
- **Visualization**:
  - Word clouds for positive/negative comments
  - Sentiment distribution histograms
  - Correlation heatmaps
  - Category and channel comparisons

## Output

After running the analysis, you'll find:

- **Figures** (`output/figures/`): All generated visualizations (PNG format)
- **Reports** (`output/reports/`): Text reports with key statistics
- **Database** (`output/youtube_sentiment_analysis.db`): SQLite database with all results
  - Query with: `SELECT * FROM comments_with_sentiment`
  - View statistics: `SELECT * FROM summary_statistics`

## Results and Interpretation

- **Sentiment Distribution**: Understand overall comment sentiment patterns
- **Top Comments**: Identify most impactful positive/negative comments
- **Category Insights**: See which video categories receive better sentiment
- **Channel Comparison**: Compare sentiment across different YouTube channels
- **Topic Analysis**: Discover main discussion topics and their sentiment
- **Word Clouds**: Visualize frequently used words in positive/negative comments

## Troubleshooting

- Pandas warnings about `error_bad_lines` deprecation: use the modern `on_bad_lines` parameter, e.g. `pd.read_csv(..., on_bad_lines="skip")`.
- Mixed dtypes (`DtypeWarning`): add `low_memory=False` or specify `dtype` per column.
- `SettingWithCopyWarning`: prefer `.loc` assignment, e.g. `df.loc[idx, "Polarity"] = values`.
- Large CSVs: consider chunked loading with `pd.read_csv(..., chunksize=...)`.

## Notes and Limitations

- TextBlob is lexicon-based; results may be simplistic on sarcasm, slang, or domain-specific language.
- For improved accuracy, use the optional Transformers backend via `SENTIMENT_BACKEND=transformer`.

## Security

- **Never commit API keys**. Use environment variables.
- The dashboard attempts to redact obvious secrets (like `key=...`) from error output, but you should still rotate exposed keys.

## Enhancement Ideas

Looking to add more features and novelty to this project? Check out **[ENHANCEMENT_IDEAS.md](ENHANCEMENT_IDEAS.md)** for 20+ realistic, implementable ideas including:
- Sentiment-engagement correlation analysis
- Topic modeling with sentiment
- Interactive dashboards
- Machine learning classification
- Time-based sentiment trends
- And many more!

Each idea includes implementation guidance, code snippets, and difficulty ratings.

## License

Specify your license here (e.g., MIT). If unspecified, the default is “all rights reserved.”

## Acknowledgements

- Inspired by publicly available YouTube comment datasets and the TextBlob library.