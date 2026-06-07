# AI Agent Context

This package tracks Formula 1 car update submissions from FIA car presentation
PDFs. Future agents should treat the JSON files as the editable source of truth;
the raw PDFs in `ref/` are local reference artifacts and are ignored by git.

## Purpose

`woUpgrade` answers one question: how quickly does each team grow its update
complexity across the season?

It does that by:

1. Reading manually extracted update items from `src/woupgrade/data/updates_2026.json`.
2. Mapping each item component to a complexity score using
   `src/woupgrade/data/rubric.json`.
3. Summing event scores and cumulative team scores in
   `src/woupgrade/script/update_growth.py`.
4. Plotting cumulative team trends in `src/woupgrade/plots/update_growth.py`.

## Important Rules

- Do not parse PDFs at runtime. PDF parsing is unreliable for these documents
  because some team pages are image-like or have awkward text streams.
- Edit `updates_2026.json` when a source submission item changes.
- Edit `rubric.json` when the component scoring model changes.
- Keep raw PDFs in `ref/`; they should not be committed.
- Keep generated outputs in `temp/`; they should not be committed.
- Use team names that match `woStrategy` colour keys where possible:
  `McLaren`, `Mercedes`, `Red Bull Racing`, `Ferrari`, `Williams`,
  `Racing Bulls`, `Aston Martin`, `Haas`, `Alpine`, `Audi`, `Cadillac`.

## Current Data Coverage

The current 2026 JSON includes these manually audited item counts:

```text
Australia: McLaren 3, Mercedes 3, Red Bull Racing 3, Ferrari 3, Williams 4,
           Racing Bulls 4, Aston Martin 7, Haas 7, Alpine 3, Audi 3,
           Cadillac 3

China:     Ferrari 1, Racing Bulls 1, Haas 1, Audi 2, Cadillac 2

Japan:     Red Bull Racing 4, Ferrari 2, Williams 1, Aston Martin 3,
           Haas 1, Alpine 3, Cadillac 2

Miami:     McLaren 7, Mercedes 2, Red Bull Racing 7, Ferrari 11, Williams 7,
           Racing Bulls 6, Haas 1, Audi 3, Alpine 6, Cadillac 9

Canada:    McLaren 7, Mercedes 7, Red Bull Racing 4, Williams 3,
           Racing Bulls 4, Haas 5, Audi 4, Alpine 2, Cadillac 2
```

The current JSON contains 163 update items in total.

Pages with `No updates submitted for this event` are intentionally omitted from
`updates_2026.json`.

## Known Extraction Pitfall

The first implementation missed visually present pages, including Australian
Williams, Australian Haas, and Australian Audi, because a text-only extraction
pass did not capture every page consistently. When auditing new PDFs, render the
PDF pages visually and compare visible row counts with JSON item counts.

## Verification Command

From `woUpgrade/`:

```bash
/Users/zhxutong/dr-wo/woStrategy/.venv/bin/python \
  src/woupgrade/script/update_growth.py \
  --output temp/update_growth_2026.png \
  --summary-output temp/update_growth_2026.csv
```

The script also supports module execution after editable install:

```bash
python -m pip install -e .
python -m woupgrade.script.update_growth \
  --output temp/update_growth_2026.png \
  --summary-output temp/update_growth_2026.csv
```
