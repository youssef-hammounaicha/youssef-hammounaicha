# CW3 public development reports

This folder contains only information explicitly approved for publication. Never add private source code, credentials, internal URLs, customer data, screenshots, or operational details.

Create a report with:

```powershell
python scripts/cw3_deck.py new --date 2026-11-07
```

Review the generated JSON, then rebuild the deck:

```powershell
python scripts/cw3_deck.py build
```

The build validates every report, regenerates the dark/light SVGs, and updates the marked Execution Deck block in `README.md`. Review the diff and commit manually.
