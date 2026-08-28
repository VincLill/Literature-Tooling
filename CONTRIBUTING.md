# Contributing

Thank you for helping improve RIS Pre-Screener.

## Before you start

- Do not commit RIS files, literature exports, generated CSV files, notebooks,
  credentials, or personal data.
- Open an issue first for larger feature proposals.
- Keep changes focused and explain the user-facing effect.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Run the checks before opening a pull request:

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py prescreen.py src/ris_prescreener/*.py tests/*.py
```

## Pull requests

Please describe what changed, how it was tested, and any documentation
updates. Do not include real research data in screenshots or test fixtures.
