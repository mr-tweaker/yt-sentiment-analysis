#!/usr/bin/env python3
"""
Generate DFD diagrams (Level 0 and Level 1) for the NTCC report.

Why not "pure" auto-generation?
  Classical DFDs describe *logical* processes and *named data flows*. Static Python
  analysis gives import graphs or call graphs — useful, but not the same notation.
  This script keeps a **single source of truth** (DOT strings below) that maps
  1:1 to your real modules (see comments). When you refactor code, update the DOT
  here and re-run.

Outputs (default):
  screenshots/dfd_level0.dot, dfd_level0.png
  screenshots/dfd_level1.dot, dfd_level1.png

Requirements:
  - Graphviz `dot` on PATH for PNG (optional: you can render .dot online or in VS Code)

Optional — *module* dependency graph (not a DFD, but code-derived):
  pip install pydeps
  pydeps yt_sentiment_pkg --max-bacon=2
  # or: pydeps src/youtube_monitor.py -T svg -o screenshots/pydeps_monitor.svg

Run:
  python scripts/generate_dfd_diagrams.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCREENSHOTS = PROJECT_ROOT / "screenshots"

# ---------------------------------------------------------------------------
# Level 0 — context. Maps to: monitoring_dashboard.py + batch main.py as one system.
# Notation: Gane–Sarson style (rounded process, rectangles for external entities).
# ---------------------------------------------------------------------------
DOT_LEVEL0 = r"""
digraph DFD_L0 {
  graph [
    rankdir=LR,
    splines=polyline,
    bgcolor="white",
    pad=0.5,
    nodesep=0.55,
    ranksep=2.2,
    fontname="Arial",
    fontsize=13,
    fontcolor="#1a1a1a",
    label="Context diagram (DFD Level 0)",
    labelloc=t,
    labeljust=c
  ];
  node [fontname="Arial", fontsize=11, color="#2c3e50"];
  edge [fontname="Arial", fontsize=9, fontcolor="#34495e", color="#34495e", penwidth=1.15];

  /* External environment — dashed cluster (common in academic DFDs) */
  subgraph cluster_ext {
    graph [fontname="Arial", fontsize=11];
    label="External entities";
    labelloc=t;
    labeljust=l;
    fontsize=11;
    fontcolor="#546e7a";
    style="rounded,dashed";
    color="#78909c";
    bgcolor="#f8fafc";
    margin=18;

    node [
      shape=box,
      style="filled,rounded",
      fillcolor="#eceff1",
      color="#546e7a",
      penwidth=1.25,
      margin="0.2,0.15"
    ];
    /* Top → bottom order on the left (declaration order + same rank) */
    EE_user [label="Analyst / User"];
    EE_yt   [label="YouTube Data API v3"];
    EE_csv  [label="Local CSV dataset\n(batch & offline analysis)"];

    { rank=same; EE_user; EE_yt; EE_csv; }
  }

  /* Single system process (Level 0 bubble) */
  P0 [
    shape=box,
    style="rounded,filled",
    fillcolor="#e3f2fd",
    color="#0d47a1",
    penwidth=2.2,
    margin="0.35,0.28",
    label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4">
      <TR><TD ALIGN="center"><B>YouTube Sentiment Analysis</B></TD></TR>
      <TR><TD ALIGN="center"><B>&amp; Monitoring System</B></TD></TR>
      <TR><TD ALIGN="center"><FONT POINT-SIZE="9" COLOR="#37474f">(Streamlit · Python · SQLite · API/CSV)</FONT></TD></TR>
    </TABLE>>
  ];

  /* Data flows — distinct compass ports on P0 reduce overlap */
  EE_user:e -> P0:nw [
    label="User inputs\n(video / channel IDs,\nrefresh, caps, UI)",
    minlen=2
  ];
  EE_yt:e -> P0:w [
    label="Live data\n(comment threads,\nvideo metadata)",
    minlen=2
  ];
  EE_csv:e -> P0:s [
    label="Batch files\n(comments CSV,\noptional metadata)",
    minlen=2
  ];
  /* User return flow: SW port (CSV uses S to avoid clashing) */
  P0:sw -> EE_user:e [
    label="Outputs\n(dashboards, history,\nalerts, Top Comments,\nkeyword trends)",
    minlen=2
  ];
}
"""

# ---------------------------------------------------------------------------
# Level 1 — processes aligned with repository modules (update when code changes).
# P1: data_loader.py + youtube_monitor fetch paths
# P2: cleaning / normalization (in loaders + monitor)
# P3: sentiment_analyzer.py
# P4: youtube_monitor persistence + main.py export_to_database
# P5: features/* + alert/heuristic logic + keyword trends (split across monitor & dashboard)
# P6: monitoring_dashboard.py / dashboard.py / visualizations.py
# D1: SQLite monitoring DB; D2: batch SQLite / output DB
# ---------------------------------------------------------------------------
DOT_LEVEL1 = r"""
digraph DFD_L1 {
  graph [fontname="Helvetica", fontsize=11, rankdir=LR, splines=ortho, bgcolor="white"];
  node [fontname="Helvetica", fontsize=10];
  edge [fontname="Helvetica", fontsize=8];

  /* --- External entities --- */
  EE_user [shape=box, label="User"];
  EE_yt   [shape=box, label="YouTube\nAPI v3"];
  EE_csv  [shape=box, label="CSV\nfiles"];

  /* --- Processes (rounded = transform) --- */
  P1 [shape=box, style=rounded, label="P1 Ingest data\n──────────────\ndata_loader.py\nyoutube_monitor.py\n(API/CSV)"];
  P2 [shape=box, style=rounded, label="P2 Preprocess\n──────────────\ndedupe, clean text,\nnormalize rows"];
  P3 [shape=box, style=rounded, label="P3 Sentiment scoring\n──────────────\nsentiment_analyzer.py\n(TextBlob / optional\nTransformers)"];
  P4 [shape=box, style=rounded, label="P4 Persist snapshots\n──────────────\nyoutube_monitor.py\nmain.py export"];
  P5 [shape=box, style=rounded, label="P5 Analytics & alerts\n──────────────\nfeatures/*, alert rules,\nkeyword / hashtag trends"];
  P6 [shape=box, style=rounded, label="P6 Present UI\n──────────────\nmonitoring_dashboard.py\ndashboard.py\nvisualizations.py"];

  /* --- Data stores (open-style via cylinder = DB convention in Graphviz) --- */
  D1 [shape=cylinder, label="D1 SQLite\nmonitoring.db\n(snapshots,\nhistory, alerts)"];
  D2 [shape=cylinder, label="D2 SQLite /\noutput\n(batch runs,\nfigures)"];

  /* --- Main pipeline --- */
  EE_yt  -> P1 [label="JSON threads,\nmetadata"];
  EE_csv -> P1 [label="tabular\ncomments"];
  P1 -> P2 [label="raw\ncomments"];
  P2 -> P3 [label="cleaned\nrows"];
  P3 -> P4 [label="polarity,\nbuckets"];
  P4 -> D1 [label="write\nsnapshots"];
  D1 -> P4 [label="read\nhistory"];
  P4 -> D2 [label="optional\nbatch export"];

  P3 -> P5 [label="scores"];
  D1 -> P5 [label="series for\nalert / trends"];
  P5 -> D1 [label="alert\nrecords"];

  P5 -> P6 [label="plot data,\nmetrics"];
  D1 -> P6 [label="query\nlatest snapshot"];
  EE_user -> P6 [label="clicks,\nparameters"];
  P6 -> EE_user [label="charts,\ntables,\nJSON details"];
}
"""


def write_dot(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"// Auto-generated by scripts/generate_dfd_diagrams.py\n"
        f"// Edit the Python source and re-run — do not hand-edit structure in duplicate.\n\n"
    )
    path.write_text(header + content.strip() + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def render_png(dot_path: Path, png_path: Path) -> bool:
    dot_exe = shutil.which("dot")
    if not dot_exe:
        print("Graphviz 'dot' not found; skipped PNG. Install graphviz or render .dot online.")
        return False
    try:
        subprocess.run(
            [dot_exe, "-Tpng", "-Gdpi=300", "-o", str(png_path), str(dot_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Wrote {png_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(e.stderr or e.stdout or str(e), file=sys.stderr)
        return False


def main() -> int:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    f0_dot = SCREENSHOTS / "dfd_level0.dot"
    f1_dot = SCREENSHOTS / "dfd_level1.dot"
    f0_png = SCREENSHOTS / "dfd_level0.png"
    f1_png = SCREENSHOTS / "dfd_level1.png"

    write_dot(f0_dot, DOT_LEVEL0)
    write_dot(f1_dot, DOT_LEVEL1)

    ok0 = render_png(f0_dot, f0_png)
    ok1 = render_png(f1_dot, f1_png)
    if not ok0 or not ok1:
        print("\nTip: open the .dot files in https://dreampuf.github.io/GraphvizOnline/ if dot failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
