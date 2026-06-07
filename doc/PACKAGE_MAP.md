# Package Map

`woUpgrade` intentionally mirrors the lightweight `woStrategy` workflow style:
data lives in JSON, plotting lives in `plots`, and executable orchestration
lives in `script`.

## Files Included In The Package

```text
pyproject.toml
README.md
doc/
  AI_AGENT_CONTEXT.md
  DATA_CONTRACT.md
  PACKAGE_MAP.md
  assets/
    example_update_growth_2026.png
src/woupgrade/
  __init__.py
  data/
    __init__.py
    rubric.json
    updates_2026.json
  plots/
    __init__.py
    update_growth.py
  script/
    __init__.py
    update_growth.py
ref/
  .gitkeep
```

## Layer Responsibilities

### Data Layer

`src/woupgrade/data/updates_2026.json`

Manual event/team/item extraction from FIA car presentation submissions. This is
the main file to update when a team submission is corrected.

`src/woupgrade/data/rubric.json`

Scoring model. Component scores and aliases are kept here so the Python logic
does not need edits when the subjective rubric changes.

### Plot Layer

`src/woupgrade/plots/update_growth.py`

Pure matplotlib rendering. It expects a scored summary dataframe and does not
know about PDF extraction.

It imports `F1_TEAM_COLORS` from `woStrategy` when available and falls back to a
local copy of the colour map.

### Script Layer

`src/woupgrade/script/update_growth.py`

Workflow orchestration:

1. Load JSON data and rubric.
2. Flatten update items.
3. Score each item.
4. Sum event and cumulative team scores.
5. Save plot and optional CSV.

The script can run as either:

```bash
python -m woupgrade.script.update_growth
```

or directly:

```bash
python src/woupgrade/script/update_growth.py
```

The direct-run support is intentional for local experiments and future Vibe
coding sessions.

### Documentation Assets

`doc/assets/example_update_growth_2026.png`

Committed example plot generated from the current JSON and rubric. This image is
for README/docs only. Runtime output should still be written to `temp/` unless a
developer intentionally refreshes the committed example.

## Ignored Files

`ref/` is ignored except for `.gitkeep`. Put manually downloaded FIA PDFs there
for local review.

`temp/` is ignored. Generated plots, CSV files, rendered PDF pages, and local
matplotlib caches belong there.
