# Changes Summary

This document summarizes the major improvements added after the initial monitoring dashboard work.

## ✅ Security + API key handling

- Removed “preconfigured API key” guidance from docs (never store keys in source control).
- Added best-effort redaction of `key=...` in error messages so API keys don’t get printed in UI/terminal logs.

## ✅ Data pipeline robustness

- `src/data_loader.prepare_data()` now merges video metadata using only the columns that exist (prevents crashes when `category_name` is absent).

## ✅ Monitoring dashboard upgrades

### Top Comments feed (latest snapshot)

- Added a DB-backed “Top Comments” feed with filters:
  - sort by **Most liked** / **Newest**
  - sentiment bucket filter
  - keyword search
  - min likes threshold

### Keyword & hashtag trends (over time)

- Added keyword/hashtag extraction from snapshots with:
  - n-grams (1/2/3)
  - configurable time bucket
  - time basis toggle:
    - **Snapshot time** (when you refreshed)
    - **Comment published time** (fallbacks safely if missing)

### Smarter alerts (anomaly detection)

- Alerting now supports:
  - z-score anomaly
  - EWMA anomaly
  - volatility-aware “big move”
- Alerts store structured JSON in `alerts.details` including baseline stats and example comments.
- Alerts tab renders `details` in an expandable UI.

### Per-language sentiment

- Adds comment language detection (when `langdetect` is installed).
- Live Monitoring shows per-language count and average sentiment with full language names.

### Sentiment model backend switch (optional)

- `SENTIMENT_BACKEND=textblob` (default, fast)
- `SENTIMENT_BACKEND=transformer` (optional, more accurate; requires `transformers` + `torch`)
- Caching added to avoid rescoring repeated comments.

### Live Monitoring — full snapshot analytics

- **Live Monitoring** uses `get_latest_snapshot_full()` so one tab shows the same *depth* as a Video Browser-style analysis: sentiment histogram, category pie/bar (when `category_id` / `category_name` are present in stored snapshots), summary stats, most positive/negative samples, Top Comments filters, and per-language sentiment—all from the latest SQLite snapshot. Time-series blocks still need enough history (e.g. refreshes over time).

## ✅ Environment variables

- `YOUTUBE_API_KEY`: YouTube Data API v3 key
- `SENTIMENT_BACKEND`: `textblob` (default) or `transformer`
- `TRANSFORMER_MODEL_NAME`: optional Hugging Face model id

## ✅ Documentation & figures (`screenshots/`)

- Renamed dashboard captures: `video_browser.png`, `live_monitoring.png`, `manual_check.png`, `keyword_hashtag_trends.png`, `architecture.png`.
- Added **DFD Level 0/1** via `scripts/generate_dfd_diagrams.py` → `dfd_level0.png`, `dfd_level1.png` (+ `.dot` sources).
- Updated **README.md**, **SCREENSHOT_GUIDE.md**, **FIGURE_CAPTIONS_AND_PLACEMENT.md**, **SHORT_FIGURE_CAPTIONS.md** to match current filenames and regeneration commands.
- Removed legacy `Figure2.png`–`Figure8.png` / `Pasted image.png` from the repo (superseded by descriptive names).
