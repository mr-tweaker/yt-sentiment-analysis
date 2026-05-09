# Friend Quickstart (Python + Docker)

## What this project is

This is a little app that **reads YouTube comments** and tries to guess if people are being:
- **Nice** 🙂
- **Meh / normal**
- **Mean** 😠

Think of it like a “mood meter” for YouTube videos.

It has **two ways to run**:

- **Batch mode (offline)**: You already have a big file of comments (a CSV). The app reads it and makes charts and a little database.
- **Dashboard mode (live)**: The app talks to YouTube (using an API key), pulls comments for videos, and shows a live web page with graphs and alerts.

### What it can do (high level)

### Batch mode (offline) — `python main.py`

- Reads comments from `data/UScomments.csv`
- Cleans them (throws away empty/broken ones)
- Gives each comment a **score**:
  - close to **-1** = very mean
  - close to **0** = neutral
  - close to **+1** = very nice
- Makes charts (pictures) and saves results in:
  - `output/figures/` (charts/images)
  - `output/reports/` (a report file)
  - `output/youtube_sentiment_analysis.db` (a small database)

### Dashboard mode (live) — `streamlit run monitoring_dashboard.py`

- You give it a **YouTube API key** (a “secret password” that lets the app ask YouTube for data)
- It shows a website on your computer: `http://localhost:8501`
- You can add a video (or pick one from a channel) and press refresh to pull new comments
- It saves “snapshots” over time in `output/monitoring.db` so you can see changes

The dashboard shows:
- **Live Monitoring**: a big “how is everything I’m watching doing *right now*?” screen—charts for nice/meh/mean split, categories (when YouTube tells us the video type), a short stats summary, and example comments; over time you also get line charts if you refresh on different days
- **Top Comments**: newest or most-liked comments
- **Trends**: what the mood looks like over time
- **Keywords/hashtags**: what words people keep using
- **Alerts**: it warns you when the mood suddenly changes a lot
- **Languages**: it can show sentiment by language (English, Russian, etc.)

### Key settings

- **YouTube API key** (needed for live dashboard):

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

- **Sentiment “brain”**:
  - Default = **TextBlob** (fast, simple)
  - Optional = **Transformers** (slower, often smarter)

To use the smarter one:

```bash
export SENTIMENT_BACKEND=transformer
```

---

## Quickstart (Python path)

### 1) Get the code + create venv

```bash
git clone <YOUR_REPO_URL>
cd yt-sentiment-analysis

python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

Optional (language detection + transformer sentiment backend):

```bash
pip install -r requirements-ml.txt
```

### 3) Run **offline batch analysis** (CSV → charts/report/db)

Put your comments CSV here:
- `data/UScomments.csv`

Then run:

```bash
python main.py
```

Outputs:
- `output/figures/`
- `output/reports/`
- `output/youtube_sentiment_analysis.db`

### 4) Run the **live monitoring dashboard** (YouTube API → Streamlit)

Set your YouTube API key:

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

Run Streamlit:

```bash
streamlit run monitoring_dashboard.py
```

Open:
- `http://localhost:8501`

Optional sentiment backend switch:

```bash
export SENTIMENT_BACKEND=transformer
export TRANSFORMER_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
streamlit run monitoring_dashboard.py
```

---

## Quickstart (Docker path)

### 1) Pull and run

```bash
docker pull mrtweaker/youtube-sentiment-analysis:latest
docker run -d --name youtube-sentiment \
  -p 8501:8501 \
  -e YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY" \
  mrtweaker/youtube-sentiment-analysis:latest
```

Open:
- `http://localhost:8501`

### 2) Stop / restart / logs

```bash
docker logs -f youtube-sentiment
docker stop youtube-sentiment
docker start youtube-sentiment
docker rm -f youtube-sentiment
```

### 3) Persist database/output (recommended)

```bash
mkdir -p output
docker run -d --name youtube-sentiment \
  -p 8501:8501 \
  -e YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY" \
  -v "$PWD/output:/app/output" \
  mrtweaker/youtube-sentiment-analysis:latest
```

### 4) (Optional) Build an ML-enabled image locally

This includes transformer support (bigger image):

```bash
docker build --build-arg INCLUDE_ML=1 -t mrtweaker/youtube-sentiment-analysis:ml .
docker run -d --name youtube-sentiment-ml \
  -p 8501:8501 \
  -e YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY" \
  -e SENTIMENT_BACKEND=transformer \
  mrtweaker/youtube-sentiment-analysis:ml
```

