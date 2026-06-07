from __future__ import annotations

import os
import tempfile
from pathlib import Path

_default_mpl_config_dir = Path(tempfile.gettempdir()) / "woupgrade-matplotlib"
_default_mpl_config_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_default_mpl_config_dir))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

try:
    from wostrategy.plots.style_maps import F1_TEAM_COLORS
except ImportError:
    F1_TEAM_COLORS = {
        "Ferrari": "#dc0000",
        "McLaren": "#ff8700",
        "Red Bull Racing": "#3029ed",
        "Mercedes": "#00fbe2",
        "Aston Martin": "#006f62",
        "Alpine": "#ff87bc",
        "Williams": "#1f6af4ff",
        "Haas": "#6e6e6e",
        "Cadillac": "#82d8f4",
        "Kick Sauber": "#00e701",
        "Racing Bulls": "#5e59ee",
    }


def plot_update_growth(
    summary: pd.DataFrame,
    *,
    title: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot cumulative car update complexity by team."""
    required_columns = {"Round", "GrandPrixShortName", "Team", "CumulativeScore"}
    missing_columns = required_columns.difference(summary.columns)
    if missing_columns:
        raise ValueError(f"summary is missing required columns: {sorted(missing_columns)}")

    fig, ax = plt.subplots(figsize=(13, 7))
    x_labels = (
        summary[["Round", "GrandPrixShortName"]]
        .drop_duplicates()
        .sort_values("Round")
        .set_index("Round")["GrandPrixShortName"]
        .to_dict()
    )

    for team, team_rows in summary.sort_values("Round").groupby("Team", sort=True):
        ax.plot(
            team_rows["Round"],
            team_rows["CumulativeScore"],
            marker="o",
            linewidth=2.2,
            label=team,
            color=F1_TEAM_COLORS.get(team),
        )

    ax.set_xlabel("Grand Prix")
    ax.set_ylabel("Cumulative update complexity score")
    ax.set_title(title or "Car Update Growth")
    ax.set_xticks(list(x_labels))
    ax.set_xticklabels(
        [x_labels[round_number] for round_number in x_labels],
        rotation=25,
        ha="right",
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)
    ax.legend(title="Team", ncols=2)
    fig.tight_layout()
    return fig, ax


def save_update_growth_figure(
    summary: pd.DataFrame,
    output_path: str | Path,
    *,
    title: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plot_update_growth(summary, title=title)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig, ax


def close_figure(fig: plt.Figure) -> None:
    plt.close(fig)
