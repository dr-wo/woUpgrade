# Data Contract

This document defines how `woUpgrade` data should be shaped so future edits do
not break scoring or plotting.

## `updates_2026.json`

Top-level fields:

- `year`: season year.
- `source_note`: short note about provenance and confidence.
- `grand_prix_order`: ordered event list. This controls plot x-axis order.
- `updates`: per-event update submissions.

Event shape:

```json
{
  "round": 1,
  "grand_prix": "Australian Grand Prix",
  "teams": {
    "McLaren": [
      {
        "component": "floor_body",
        "description": "Revised floor geometry.",
        "guessed": false
      }
    ]
  }
}
```

Rules:

- `round` must match one entry in `grand_prix_order`.
- `grand_prix` should match the official event name used in
  `grand_prix_order`.
- `teams` keys should use the canonical plot/team colour names.
- Each submitted row in the FIA presentation table should become one JSON item.
- If one FIA row combines two parts, use a combined component key in
  `rubric.json` rather than splitting the row unless the source clearly lists
  separate update rows.
- Use `guessed: true` only when the component or description is inferred from a
  poor PDF extraction or unclear table text.

## `rubric.json`

Top-level fields:

- `default_score`: fallback score for unknown components.
- `component_scores`: canonical component complexity scores.
- `component_aliases`: maps JSON component keys to canonical score keys.

Example:

```json
{
  "component_scores": {
    "floor_body": 3.0
  },
  "component_aliases": {
    "floor": "floor_body"
  }
}
```

Rules:

- Add an alias whenever a new component name appears in `updates_2026.json`.
- Prefer a stable component vocabulary over free-form component names.
- Keep subjective score changes in `rubric.json`; do not hard-code scores in
  Python.

## Output Summary Columns

The CLI writes a CSV with:

- `Round`
- `Team`
- `GrandPrix`
- `GrandPrixShortName`
- `EventScore`
- `ItemCount`
- `CumulativeScore`

The plot uses `Round`, `GrandPrixShortName`, `Team`, and `CumulativeScore`.
