# Screenshot & Diagram Guide

This folder documents figures under `screenshots/` for papers, reports, and demos.

## Current assets in `screenshots/`

| File | Use |
|------|-----|
| `architecture.png` | System architecture (four layers) |
| `video_browser.png` | Video Browser tab |
| `live_monitoring.png` | Live Monitoring tab |
| `manual_check.png` | Manual Check tab |
| `keyword_hashtag_trends.png` | Keyword & hashtag trends |
| `dfd_level0.png` | DFD Level 0 (context diagram) |
| `dfd_level1.png` | DFD Level 1 (processes + data stores) |
| `dfd_level0.dot` / `dfd_level1.dot` | Graphviz source — edit and re-render |

Legacy numbered files (`Figure2.png`, etc.) were replaced by the descriptive names above.

## Regenerate diagrams from code

**DFD (Level 0 & 1)** — aligned with `src/data_loader.py`, `youtube_monitor.py`, `sentiment_analyzer.py`, `monitoring_dashboard.py`:

```bash
python scripts/generate_dfd_diagrams.py
```

Requires [Graphviz](https://graphviz.org/) `dot` on your PATH for PNG export. Without `dot`, use the generated `.dot` files in [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/).

**Layered architecture** (optional alternate to `architecture.png`):

```bash
python scripts/generate_figure1_architecture.py
```

## Capture UI screenshots

1. Run the dashboard: `streamlit run monitoring_dashboard.py` (or Docker on port 8501).
2. Set browser zoom to **100%**, hide clutter, use PNG export.
3. Save with the filenames above so docs and captions stay consistent.

### Video Browser → `video_browser.png`

1. Open **Video Browser**.
2. Enter channel ID, `@handle`, or channel URL.
3. Set max videos (5–10) and comments per video (100–500).
4. Click **Fetch Videos**; capture the list with titles and actions.

### Live Monitoring → `live_monitoring.png`

1. Add a video from Video Browser (**Add to Monitoring**).
2. Open **Live Monitoring**, select the video, **Refresh Now**.
3. Capture headline metrics, sentiment distribution, and scroll for Top Comments / trends if visible.

### Manual Check → `manual_check.png`

1. Open **Manual Check**.
2. Paste video URL or ID; set comment limit (e.g. 200); run analysis.
3. Capture histogram and summary metrics.

### Keyword & hashtag trends → `keyword_hashtag_trends.png`

1. From Live Monitoring (or trends section), set window, bucket, n-grams.
2. Toggle **snapshot time** vs **published time** if timestamps exist.
3. Capture chart and table.

## Docker (optional)

```bash
docker pull mrtweaker/youtube-sentiment-analysis:latest
docker run -d --name youtube-sentiment -p 8501:8501 -e YOUTUBE_API_KEY=your_key mrtweaker/youtube-sentiment-analysis:latest
```

Open http://localhost:8501. See [DOCKER_README.md](DOCKER_README.md).

## Tips

- PNG for print; keep labels readable at report scale.
- Never commit API keys; use environment variables.
- For batch-only demos, use `python main.py` and figures under `output/figures/`.
