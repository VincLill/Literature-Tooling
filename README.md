# RIS Pre-Screener

A simple, topic-independent application for transparent first-pass screening of RIS exports.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
streamlit run app.py
```

Upload a RIS file, create any number of keyword groups, and run the screening.
The app provides an INCLUDE CSV and a CSV containing all decisions. The columns
`hits_*`, `exclude_hits`, and `reason` explain every decision.

## Rules

- Only `title` and `abstract` are searched.
- Terms within a group are joined with OR.
- Required groups are joined with AND.
- Exclude matches take precedence.
- Explicitly unsupported languages are excluded by default, while missing language is allowed.
- Enabling the language option also excludes records with missing language.

The interface contains no topic-specific groups or keywords. All criteria are
entered by the user for each screening project.

## CLI and Docker

```json
{
  "include_groups": {
    "Population": ["term one", "term two"],
    "Intervention": ["term three"]
  },
  "required_groups": ["Population", "Intervention"],
  "exclude_terms": ["irrelevant term"]
}
```

```bash
ris-prescreen input.ris config.json --output results/screening
```

```bash
docker build -t ris-pre-screener .
docker run --rm -p 8501:8501 ris-pre-screener
```

All processing happens locally.

## Repository layout

```text
app.py                 # Streamlit launcher
prescreen.py           # CLI launcher
src/ris_prescreener/   # Application and screening library
tests/                 # Automated tests
```

Input files, research material, generated results, notebooks, and secrets are
excluded by `.gitignore` and should never be committed.
