# Figure Captions and Placement Guide

## Available figures (`screenshots/`)

| Fig. | File | Status |
|------|------|--------|
| 1 | `architecture.png` | System architecture (four layers) |
| 2 | `video_browser.png` | Video Browser tab |
| 3 | `live_monitoring.png` | Live Monitoring tab |
| 4 | `manual_check.png` | Manual Check tab |
| 5 | `keyword_hashtag_trends.png` | Keyword/hashtag trends |
| 6 | `dfd_level0.png` | DFD Level 0 (context) |
| 7 | `dfd_level1.png` | DFD Level 1 (decomposed processes) |

**Regenerate:** `python scripts/generate_dfd_diagrams.py` (DFD); edit `scripts/generate_dfd_diagrams.py` or `.dot` files, then re-run.

**Optional / batch-only (from `main.py`):** correlation heatmaps, LDA topics, aspect charts — export to `output/figures/` when those features are run; not all have fixed filenames in `screenshots/`.

---

## Figure 1 — System architecture

**Placement:** Methodology / system design (after architecture paragraph).

**Caption (short):**
```
Fig. 1. System architecture: Presentation (Streamlit), Application (Python pipeline),
Data (SQLite, YouTube API v3, CSV), Infrastructure (Docker).
```

---

## Figure 2 — Video Browser

**Placement:** Dashboard / implementation section.

**Caption (short):**
```
Fig. 2. Video Browser: channel input, fetched video list, Add to Monitoring / Analyze actions.
```

---

## Figure 3 — Live Monitoring

**Caption (short):**
```
Fig. 3. Live Monitoring: snapshot metrics, sentiment distribution, Top Comments and trends when history exists.
```

---

## Figure 4 — Manual Check

**Caption (short):**
```
Fig. 4. Manual Check: one-off video analysis with sentiment distribution and summary statistics.
```

---

## Figure 5 — Keyword & hashtag trends

**Caption (short):**
```
Fig. 5. Keyword and hashtag trends with configurable window, bucket size, n-grams, and snapshot vs published time basis.
```

---

## Figure 6 — DFD Level 0

**Placement:** Methodology (data flow / context), often before or after architecture.

**Caption (short):**
```
Fig. 6. Context diagram (DFD Level 0): analyst, YouTube Data API, and CSV batch inputs;
system outputs dashboards, alerts, and analytics.
```

---

## Figure 7 — DFD Level 1

**Placement:** Methodology or implementation (logical decomposition).

**Caption (short):**
```
Fig. 7. DFD Level 1: ingest, preprocess, sentiment scoring, persistence, analytics/alerts,
and Streamlit presentation, with SQLite data stores.
```

---

## Numbering note

Older drafts used nine figures (heatmaps, LDA, case studies). This repository’s **committed** screenshot set focuses on the **monitoring dashboard** and **DFDs** above. Add extra figures from `output/figures/` if your paper still requires them.
