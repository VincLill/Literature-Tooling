"""Reusable RIS pre-screening logic.

Include groups are combined with AND; terms inside one group are combined
with OR. Exclude terms always take precedence.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import rispy

ACCEPTED_LANGUAGES = {
    "en", "eng", "english", "de", "ger", "german", "deutsch",
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def find_matches(text: str, terms: Iterable[str]) -> list[str]:
    normalized = normalize_text(text)
    return sorted({term.strip() for term in terms if term.strip() and normalize_text(term) in normalized})


def _language_status(language: str) -> str:
    normalized = normalize_text(language)
    if not normalized:
        return "UNKNOWN"
    parts = [part.strip() for part in re.split(r"[,;/|]", normalized) if part.strip()]
    return "ACCEPTED" if any(part in ACCEPTED_LANGUAGES for part in parts) else "NOT_ACCEPTED"


def classify_record(
    title: str,
    abstract: str,
    language: str = "",
    include_groups: dict[str, Iterable[str]] | None = None,
    exclude_terms: Iterable[str] = (),
    required_groups: Iterable[str] | None = None,
    accepted_languages: Iterable[str] | None = None,
    require_language: bool = False,
    exclude_nonaccepted_language: bool = True,
) -> dict[str, str]:
    groups = include_groups or {}
    required = set(required_groups if required_groups is not None else groups)
    text = normalize_text(f"{title} {abstract}")
    language_status = _language_status(language)
    if accepted_languages is not None:
        accepted = {normalize_text(value) for value in accepted_languages if normalize_text(value)}
        normalized_language = normalize_text(language)
        language_status = (
            "UNKNOWN" if not normalized_language else
            "ACCEPTED" if any(part.strip() in accepted for part in re.split(r"[,;/|]", normalized_language)) else
            "NOT_ACCEPTED"
        )

    group_hits = {name: find_matches(text, terms) for name, terms in groups.items()}
    exclude_hits = find_matches(text, exclude_terms)
    missing = [name for name in required if not group_hits.get(name)]
    language_excluded = (
        exclude_nonaccepted_language and language_status == "NOT_ACCEPTED"
    )

    if language_excluded:
        decision, reason = "EXCLUDE", f"Language not accepted: {language}"
    elif exclude_hits:
        decision, reason = "EXCLUDE", f"Exclude match: {', '.join(exclude_hits)}"
    elif missing:
        decision, reason = "EXCLUDE", f"Missing required group: {', '.join(missing)}"
    elif require_language and language_status == "UNKNOWN":
        decision, reason = "EXCLUDE", "Language unknown"
    else:
        decision = "INCLUDE"
        parts = [f"{name}: {', '.join(group_hits[name])}" for name in groups if group_hits[name]]
        parts.append("Language accepted" if language_status == "ACCEPTED" else "Language not evaluated")
        reason = " | ".join(parts)

    result = {
        "decision": decision,
        "language_status": language_status,
        "exclude_hits": "; ".join(exclude_hits),
        "reason": reason,
    }
    for name, hits in group_hits.items():
        result[f"hits_{name}"] = "; ".join(hits)
    return result


def _first(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key, "")
        if isinstance(value, list):
            value = "; ".join(str(item) for item in value)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def screen_ris(
    input_path: str | Path,
    include_groups: dict[str, Iterable[str]],
    exclude_terms: Iterable[str],
    required_groups: Iterable[str] | None = None,
    require_language: bool = False,
    exclude_nonaccepted_language: bool = True,
) -> pd.DataFrame:
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"RIS file not found: {path}")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        records = rispy.load(handle)

    rows = []
    for record in records:
        title = _first(record, "title", "TI")
        abstract = _first(record, "abstract", "AB")
        language = _first(record, "language", "LA")
        result = classify_record(
            title, abstract, language, include_groups, exclude_terms,
            required_groups, require_language=require_language,
            exclude_nonaccepted_language=exclude_nonaccepted_language,
        )
        rows.append({
            "title": title,
            "abstract": abstract,
            "year": _first(record, "year", "PY"),
            "authors": _first(record, "authors", "AU"),
            "language": language,
            "country": _first(record, "country", "C1"),
            **result,
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen a RIS file using a JSON keyword configuration.")
    parser.add_argument("input", type=Path, help="Path to the RIS file")
    parser.add_argument("config", type=Path, help="JSON file containing include_groups and exclude_terms")
    parser.add_argument("-o", "--output", type=Path, default=Path("screening_results"))
    args = parser.parse_args()
    import json
    configuration = json.loads(args.config.read_text(encoding="utf-8"))
    include_groups = configuration.get("include_groups", {})
    exclude_terms = configuration.get("exclude_terms", [])
    required = configuration.get("required_groups", list(include_groups))
    result = screen_ris(
        args.input,
        include_groups,
        exclude_terms,
        required_groups=required,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output.with_name(args.output.name + "_all.csv"), index=False, encoding="utf-8-sig")
    result[result["decision"] == "INCLUDE"].to_csv(
        args.output.with_name(args.output.name + "_INCLUDE.csv"), index=False, encoding="utf-8-sig"
    )
    print(f"Processed {len(result)} records; included {sum(result['decision'] == 'INCLUDE')}.")


if __name__ == "__main__":
    main()
