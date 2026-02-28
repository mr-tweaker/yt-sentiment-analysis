# 15-Slide PPT Content for NTCC Mid-term Evaluation (05-02-2026)
## YouTube Sentiment Analysis with Real-time Monitoring

**Instructions:** Copy each slide’s title and content into gamma.app. Use “Title” for slide titles and “Bullet” or “Body” for the content as needed.

---

## SLIDE 1 — Title Slide

**Title:**  
YouTube Sentiment Analysis with Real-time Monitoring

**Subtitle:**  
NTCC Even Sem 2026 — Mid-term Evaluation | PG Major Project / BCA/BSc-Hons Dissertation

**Optional line:**  
Progress Update | 05-02-2026

---

## SLIDE 2 — Introduction

**Title:** Introduction

**Content:**
- **Problem:** Understanding viewer sentiment from YouTube comments is manual and time-consuming.
- **Solution:** A system that analyzes comment sentiment and monitors it in near real time.
- **Scope:** From a basic Jupyter notebook to a modular Python application with a web dashboard and Docker deployment.
- **Outcome:** Production-ready application with 18+ features, real-time monitoring, and containerized deployment (Docker Hub).

---

## SLIDE 3 — Objectives

**Title:** Objectives

**Content:**
- **Primary:** Build an end-to-end YouTube comment sentiment analysis system with real-time monitoring.
- **Secondary objectives:**
  - Implement NLP-based sentiment analysis (TextBlob) and categorization.
  - Add advanced analytics: topic modeling (LDA), aspect-based sentiment, engagement correlation.
  - Provide an interactive web dashboard (Streamlit) for analysis and monitoring.
  - Enable continuous monitoring with historical tracking and alerts.
  - Containerize the application for one-command deployment (Docker).

---

## SLIDE 4 — Flow Diagram of Project Work (High-Level)

**Title:** Flow Diagram of Project Work

**Content (describe flow; you can turn this into a diagram in gamma):**
1. **Data ingestion** — Load comments (CSV / YouTube API).
2. **Preprocessing** — Clean text, handle encoding, optional sampling.
3. **Sentiment analysis** — TextBlob polarity → positive / neutral / negative categories.
4. **Feature extraction** — Emoji, length, engagement, topics (LDA), aspects.
5. **Visualization & reporting** — Charts, word clouds, heatmaps, automated reports.
6. **Real-time path** — YouTube API → fetch comments → analyze → store in SQLite → dashboard.
7. **Deployment** — Docker build → push to registry → run on host (e.g. Windows 11).

**Tip for gamma:** Use a simple flowchart: Data → Preprocess → Analyze → Visualize → Monitor → Deploy.

---

## SLIDE 5 — Flow Diagram (Detailed Pipeline)

**Title:** Detailed Project Pipeline

**Content:**
- **Batch analysis:** CSV → `data_loader` → `sentiment_analyzer` → `features` (basic/medium/advanced) → `visualizations` → reports & DB export.
- **Real-time monitoring:** Video/Channel input → YouTube API → comment fetch → sentiment analysis → SQLite snapshot → alerts → dashboard refresh.
- **Dashboard:** Video Browser | Live Monitoring | Sentiment History | Alerts | Manual Check.

---

## SLIDE 6 — Dataset Description

**Title:** Dataset Description

**Content:**
- **Primary dataset:** Comment CSV (e.g. `UScomments.csv`) with columns such as `video_id`, `comment_text`, `likes`, `replies`; optional video metadata CSV.
- **Source:** Public datasets (e.g. Kaggle) and/or data fetched via YouTube Data API v3.
- **Preprocessing:** Multiple encoding support (UTF-8, Latin-1, etc.), missing value handling, optional sample size for large files.
- **Live data:** Comments fetched in real time via YouTube Data API v3 for selected videos/channels; configurable comment limit per video.

---

## SLIDE 7 — Methodology / Approach (Overview)

**Title:** Methodology / Approach

**Content:**
- **Sentiment analysis:** TextBlob polarity score (−1 to +1) and 5-tier categorization (e.g. very positive → very negative).
- **Analytics:** Statistical summaries, sentiment–emoji correlation, comment length vs. sentiment, engagement (likes/replies) correlation.
- **Advanced NLP:** LDA for topic modeling with sentiment per topic; keyword-based aspect extraction and aspect-level sentiment.
- **Visualization:** Histograms, pie/bar charts, word clouds (sentiment-colored), heatmaps, time-series and stacked area charts.
- **System design:** Modular Python packages (`src/`), config-driven paths and API keys, SQLite for history and alerts.

---

## SLIDE 8 — Methodology (Real-time & Deployment)

**Title:** Real-time Monitoring & Deployment Approach

**Content:**
- **API integration:** YouTube Data API v3 for video metadata and comment threads; rate limiting and error handling.
- **Persistence:** SQLite tables for sentiment history, comment snapshots, alerts, and video info cache.
- **Dashboard:** Streamlit with session state; tabs for browsing channels, live monitoring, history, alerts, and manual checks.
- **Deployment:** Dockerfile (Python 3.11-slim), Docker Compose, environment variables for API key; image published on Docker Hub for cross-platform use (including Windows 11).

---

## SLIDE 9 — Timeline of Project Work (PERT-Style)

**Title:** Timeline of Project Work (PERT Chart)

**Content (phases; adjust dates to your actual schedule):**
- **Phase 1 — Enhancement (Notebook):** Add 17+ features in Jupyter (sentiment, emoji, length, engagement, topics, aspects, reports, DB export).
- **Phase 2 — Restructuring:** Convert notebook to modular project (`src/`, `main.py`, feature modules).
- **Phase 3 — Real-time monitoring:** YouTube API, SQLite schema, monitoring service, alert logic.
- **Phase 4 — Dashboard:** Streamlit UI, Video Browser, Live Monitoring, History, Alerts, Manual Check, visualizations.
- **Phase 5 — Docker & docs:** Dockerfile, Compose, push to Docker Hub, Windows 11 and API key documentation.

**Tip for gamma:** Use a horizontal timeline or a simple Gantt/PERT block diagram with these phases.

---

## SLIDE 10 — Research Paper Status

**Title:** Research Paper Status

**Content:**
- **Status:** Work in progress (WIP).
- **Planned focus:** Sentiment analysis of YouTube comments using NLP; real-time monitoring and practical deployment (Streamlit + Docker).
- **Target:** Submit/present paper in line with NTCC schedule (to be updated as per department guidelines).
- **Current:** Literature review and methodology sections aligned with implemented system; results and discussion to be updated post final evaluation.

---

## SLIDE 11 — Key Features & Novelty

**Title:** Key Features & Novelty

**Content:**
- **Real-time monitoring:** Continuous sentiment tracking, historical snapshots, threshold-based alerts.
- **Integrated video discovery:** Browse by channel ID/URL/username; select by video title; one-click analysis with custom comment limit.
- **Advanced analytics:** Topic modeling (LDA) with sentiment; aspect-based sentiment; engagement correlation; network-style visualization.
- **Production readiness:** Modular code, error handling, type safety, memory optimization; Docker image on Docker Hub for easy deployment.

---

## SLIDE 12 — Technical Stack & Deliverables

**Title:** Technical Stack & Deliverables

**Content:**
- **Stack:** Python 3.8+, Pandas, NumPy, TextBlob, Matplotlib/Seaborn/Plotly, WordCloud, Streamlit, Google API Client (YouTube Data API v3), SQLite, Docker.
- **Deliverables:** Modular Python application; Streamlit dashboard; monitoring service script; Docker image (`mrtweaker/youtube-sentiment-analysis:latest`); README, Docker/Windows/API key docs; example configs and run commands.

---

## SLIDE 13 — Challenges & Solutions

**Title:** Challenges & Solutions

**Content:**
- **Data:** Encoding errors → multiple encoding fallbacks; missing files → clear errors and path/CLI options.
- **Types:** DB values as strings → `pd.to_numeric()` and NaN handling before calculations.
- **Memory:** Segmentation faults → Agg backend, garbage collection, DataFrame copies, figure cleanup.
- **UX:** Pie chart overlap → label distance/explode; readability → color-coded sample comments.
- **Deployment:** Windows vs Linux commands → platform-specific docs and single-line Docker run examples.

---

## SLIDE 14 — Conclusion & Future Work

**Title:** Conclusion & Future Work

**Content:**
- **Achieved:** 18/20 planned features (excluding 2 ML-based by choice); real-time monitoring; interactive dashboard; Docker deployment; documentation.
- **Future work:** (Optional) ML-based sentiment classification; sentiment prediction model; more languages; performance tuning for very large datasets.

---

## SLIDE 15 — Thank You / Q&A

**Title:** Thank You

**Content:**
- **Questions?**
- **Contact / Project repo:** [Add your name, enrollment/details, and link to repo or Docker image if desired.]
- **Docker:** `docker pull mrtweaker/youtube-sentiment-analysis:latest`

---

**End of 15-slide content.**
