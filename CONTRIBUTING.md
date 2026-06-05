# Contributing

Thanks for taking the time. This is a small project maintained in spare time, so the contribution loop is intentionally lightweight.

## Reporting a bug

Open an issue with:

- the command you ran (or the dashboard action)
- the ticker(s) involved
- the full traceback or unexpected output
- Python version and OS

## Proposing a change

For small fixes (typos, obvious bugs, single-indicator tweaks), open a PR directly.

For larger changes (new indicators, new data sources, refactors), open an issue first to discuss the approach before writing the code. This avoids wasted work.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install ruff pytest
```

Run the linters and tests before pushing:

```bash
ruff check .
pytest -q
```

CI runs the same commands — green CI is required to merge.

## Code style

- Python 3.10+, type hints where they help readability.
- Keep new indicators in their own functions; do not inline calculations into the scoring loop.
- Network calls go through `data_sources.fetch_stock_data` so fallback logic stays centralized.
- No silent `except Exception: pass`. Log at `WARNING` and let the caller decide.

## What I'm unlikely to merge

- New broker / trading-execution code. This is a **scanner** — execution is intentionally out of scope.
- Heavy ML dependencies (TF / PyTorch). The project should stay installable from `requirements.txt` in under a minute on a fresh machine.
- Hardcoded API keys or credentials of any kind.
