# YouTube Sentiment Analysis

A comprehensive Python project for analyzing sentiment of YouTube comments. This project uses NLP techniques to classify comments as positive, neutral, or negative, and provides extensive analysis features including topic modeling, engagement correlation, and interactive visualizations.

## Overview

This project provides:
- **Sentiment Analysis**: TextBlob-based sentiment polarity analysis (−1 to 1)
- **Data Processing**: Automated data loading, cleaning, and preprocessing
- **Advanced Features**: 17+ enhancement features including emoji analysis, topic modeling, network graphs, and more
- **Visualizations**: Automated generation of charts, word clouds, and heatmaps
- **Reporting**: Automated report generation and database export
- **Modular Design**: Well-organized Python modules for easy extension

## Tech Stack

- Python 3.8+
- Pandas, NumPy
- Seaborn, Matplotlib
- TextBlob (for sentiment polarity)
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

The monitoring dashboard now includes:
- ✅ **Preconfigured API Key** - Your API key is automatically loaded
- ✅ **Video Title Display** - Shows video titles instead of IDs everywhere

```bash
streamlit run monitoring_dashboard.py
```

**Note**: Your YouTube API key is preconfigured in `src/config.py` and will be used automatically.

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

- TextBlob uses a lexicon-based approach; results may be simplistic on sarcasm, slang, or domain-specific language.
- For production-grade sentiment analysis, consider transformer-based models (e.g., fine-tuned BERT) and robust preprocessing.

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