from __future__ import annotations

import argparse
import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from woupgrade.plots.update_growth import close_figure, save_update_growth_figure


SCRIPT_CONFIG = {
    "year": 2026,
    "data": None,
    "rubric": None,
    "output": None,
    "summary_output": None,
    "include_zero_teams": True,
    "show": False,
}


def build_update_summary(
    *,
    updates_data: dict[str, Any],
    rubric: dict[str, Any],
    include_zero_teams: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return item-level scores and per-team cumulative event summary."""
    item_rows = flatten_update_items(updates_data, rubric)
    items = pd.DataFrame(item_rows)
    order = pd.DataFrame(updates_data["grand_prix_order"])
    if items.empty:
        raise ValueError("No update items found in data.")

    event_scores = (
        items.groupby(["Round", "GrandPrix", "GrandPrixShortName", "Team"], as_index=False)
        .agg(EventScore=("Score", "sum"), ItemCount=("Score", "size"))
        .sort_values(["Round", "Team"])
    )

    if include_zero_teams:
        teams = sorted(items["Team"].dropna().unique())
        scaffold = pd.MultiIndex.from_product(
            [order["round"].tolist(), teams],
            names=["Round", "Team"],
        ).to_frame(index=False)
        scaffold = scaffold.merge(
            order.rename(
                columns={
                    "round": "Round",
                    "name": "GrandPrix",
                    "short_name": "GrandPrixShortName",
                }
            )[["Round", "GrandPrix", "GrandPrixShortName"]],
            on="Round",
            how="left",
        )
        event_scores = scaffold.merge(
            event_scores,
            on=["Round", "GrandPrix", "GrandPrixShortName", "Team"],
            how="left",
        )
        event_scores["EventScore"] = event_scores["EventScore"].fillna(0.0)
        event_scores["ItemCount"] = event_scores["ItemCount"].fillna(0).astype(int)

    event_scores = event_scores.sort_values(["Team", "Round"]).reset_index(drop=True)
    event_scores["CumulativeScore"] = event_scores.groupby("Team")["EventScore"].cumsum()
    return items, event_scores


def flatten_update_items(
    updates_data: dict[str, Any],
    rubric: dict[str, Any],
) -> list[dict[str, Any]]:
    gp_lookup = {
        event["round"]: event
        for event in updates_data["grand_prix_order"]
    }
    rows: list[dict[str, Any]] = []
    for event in updates_data["updates"]:
        round_number = int(event["round"])
        gp = gp_lookup[round_number]
        for team, items in event["teams"].items():
            for idx, item in enumerate(items, start=1):
                component = item["component"]
                rubric_key = canonical_component(component, rubric)
                rows.append(
                    {
                        "Year": updates_data["year"],
                        "Round": round_number,
                        "GrandPrix": event.get("grand_prix", gp["name"]),
                        "GrandPrixShortName": gp["short_name"],
                        "Team": team,
                        "ItemNumber": idx,
                        "Component": component,
                        "RubricComponent": rubric_key,
                        "Score": component_score(component, rubric),
                        "Description": item.get("description", ""),
                        "Guessed": bool(item.get("guessed", False)),
                    }
                )
    return rows


def canonical_component(component: str, rubric: dict[str, Any]) -> str:
    aliases = rubric.get("component_aliases", {})
    return aliases.get(component, component)


def component_score(component: str, rubric: dict[str, Any]) -> float:
    rubric_key = canonical_component(component, rubric)
    scores = rubric.get("component_scores", {})
    return float(scores.get(rubric_key, rubric.get("default_score", 1.0)))


def run_update_growth(
    *,
    year: int,
    data_path: str | Path | None = SCRIPT_CONFIG["data"],
    rubric_path: str | Path | None = SCRIPT_CONFIG["rubric"],
    output_path: str | Path | None = SCRIPT_CONFIG["output"],
    summary_output_path: str | Path | None = SCRIPT_CONFIG["summary_output"],
    include_zero_teams: bool = SCRIPT_CONFIG["include_zero_teams"],
    show: bool = SCRIPT_CONFIG["show"],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    updates_data = load_json(data_path or default_data_path(year))
    rubric = load_json(rubric_path or default_rubric_path())
    items, summary = build_update_summary(
        updates_data=updates_data,
        rubric=rubric,
        include_zero_teams=include_zero_teams,
    )

    output_path = Path(output_path) if output_path is not None else Path("temp") / (
        f"update_growth_{year}.png"
    )
    fig, _ = save_update_growth_figure(
        summary,
        output_path,
        title=f"{year} Car Update Growth",
    )

    if summary_output_path is not None:
        summary_output_path = Path(summary_output_path)
        summary_output_path.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(summary_output_path, index=False)

    print_event_summary(summary)
    print(f"Items scored: {len(items)}")
    print(f"Saved plot: {output_path}")
    if summary_output_path is not None:
        print(f"Saved summary: {summary_output_path}")

    if show:
        fig.show()
    else:
        close_figure(fig)
    return items, summary


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def default_data_path(year: int) -> Path:
    return Path(resources.files("woupgrade.data") / f"updates_{year}.json")


def default_rubric_path() -> Path:
    return Path(resources.files("woupgrade.data") / "rubric.json")


def print_event_summary(summary: pd.DataFrame) -> None:
    latest = summary.sort_values(["Team", "Round"]).groupby("Team", as_index=False).tail(1)
    latest = latest.sort_values(["CumulativeScore", "Team"], ascending=[False, True])
    print("\nCumulative update complexity")
    print("=" * 29)
    for row in latest.itertuples(index=False):
        print(f"{row.Team:<16} {row.CumulativeScore:>5.1f}")


def main() -> None:
    args = _parse_args()
    run_update_growth(
        year=args.year,
        data_path=args.data,
        rubric_path=args.rubric,
        output_path=args.output,
        summary_output_path=args.summary_output,
        include_zero_teams=args.include_zero_teams,
        show=args.show,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot cumulative car update complexity from manual JSON data."
    )
    parser.add_argument("--year", type=int, default=SCRIPT_CONFIG["year"])
    parser.add_argument("--data", type=Path, default=SCRIPT_CONFIG["data"])
    parser.add_argument("--rubric", type=Path, default=SCRIPT_CONFIG["rubric"])
    parser.add_argument("--output", type=Path, default=SCRIPT_CONFIG["output"])
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=SCRIPT_CONFIG["summary_output"],
    )
    parser.add_argument(
        "--include-zero-teams",
        action=argparse.BooleanOptionalAction,
        default=SCRIPT_CONFIG["include_zero_teams"],
        help="Carry teams through events where they submitted no update.",
    )
    parser.add_argument("--show", action="store_true", default=SCRIPT_CONFIG["show"])
    return parser.parse_args()


if __name__ == "__main__":
    main()
