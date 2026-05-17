# Short Figure Captions (IEEE-style)

Paths are under `screenshots/`. Regenerate DFDs: `python scripts/generate_dfd_diagrams.py`.

### Fig. 1 — `architecture.png`
```
Fig. 1. System architecture: Presentation (Streamlit), Application (Python pipeline),
Data (SQLite, YouTube API v3, CSV), Infrastructure (Docker).
```

### Fig. 2 — `video_browser.png`
```
Fig. 2. Video Browser: channel input, video list, Add to Monitoring and Analyze actions.
```

### Fig. 3 — `live_monitoring.png`
```
Fig. 3. Live Monitoring: snapshot metrics, sentiment distribution, Top Comments and trends.
```

### Fig. 4 — `manual_check.png`
```
Fig. 4. Manual Check: single-video analysis with sentiment distribution and summary stats.
```

### Fig. 5 — `keyword_hashtag_trends.png`
```
Fig. 5. Keyword and hashtag trends with time window, buckets, n-grams, and time-basis toggle.
```

### Fig. 6 — `dfd_level0.png`
```
Fig. 6. Context diagram (DFD Level 0): user, YouTube API, CSV batch, and system boundary.
```

### Fig. 7 — `dfd_level1.png`
```
Fig. 7. DFD Level 1: ingest, preprocess, score, persist, analytics/alerts, and UI processes.
```

## Placement quick reference

| Fig. | Section hint |
|------|----------------|
| 1 | Architecture / methodology |
| 2–5 | Interactive dashboard / results |
| 6–7 | Data flow / methodology |
