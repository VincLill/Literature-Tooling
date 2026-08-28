"""Small Streamlit interface for configurable RIS screening."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from .core import screen_ris

st.set_page_config(page_title="RIS Pre-Screener", page_icon="📚", layout="wide")
st.title("📚 RIS Pre-Screener")
st.caption("Transparent screening of RIS files using configurable keyword groups.")

uploaded = st.file_uploader("1. Choose a RIS file", type=["ris"])
output_name = st.text_input("2. INCLUDE output filename", "screening_INCLUDE.csv")

st.subheader("3. Include keyword groups")
st.info("Each required group must match at least one term. Terms within a group use OR; groups use AND.")

if "groups" not in st.session_state:
    st.session_state["groups"] = [
        {"name": "Group 1", "terms": "", "required": True},
    ]

for index, group in enumerate(st.session_state["groups"]):
    left, middle, right = st.columns([2, 5, 1])
    with left:
        group["name"] = st.text_input("Group name", group["name"], key=f"group_name_{index}")
    with middle:
        group["terms"] = st.text_area(
            "Terms (one per line)", group["terms"], key=f"group_terms_{index}"
        )
    with right:
        group["required"] = st.checkbox(
            "Required", group["required"], key=f"group_required_{index}"
        )
        if st.button("Remove", key=f"remove_group_{index}"):
            st.session_state["groups"].pop(index)
            st.rerun()

if st.button("Add keyword group"):
    number = len(st.session_state["groups"]) + 1
    st.session_state["groups"].append(
        {"name": f"Group {number}", "terms": "", "required": True}
    )
    st.rerun()

st.subheader("4. Exclude keywords")
exclude_text = st.text_area(
    "One term per line. One match is enough to exclude a record.", ""
)
require_language = st.checkbox(
    "Require English or German language (missing language is excluded)", value=False
)

if st.button("Run screening", type="primary", disabled=uploaded is None):
    if uploaded is None:
        st.error("Please choose a RIS file first.")
    else:
        temp_path: Path | None = None
        try:
            with NamedTemporaryFile(suffix=".ris", delete=False) as handle:
                handle.write(uploaded.getvalue())
                temp_path = Path(handle.name)
            groups = {
                group["name"].strip(): [
                    term.strip()
                    for term in group["terms"].splitlines()
                    if term.strip()
                ]
                for group in st.session_state["groups"]
                if group["name"].strip() and group["terms"].strip()
            }
            required = [
                group["name"].strip()
                for group in st.session_state["groups"]
                if group["required"] and group["name"].strip() and group["terms"].strip()
            ]
            if not groups:
                raise ValueError("Add at least one named keyword group.")
            result = screen_ris(
                temp_path,
                groups,
                [x.strip() for x in exclude_text.splitlines() if x.strip()],
                required,
                require_language,
            )
        except (OSError, ValueError) as exc:
            st.error(f"Screening failed: {exc}")
        else:
            st.session_state["result"] = result
            st.session_state["output_name"] = output_name if output_name.endswith(".csv") else f"{output_name}.csv"
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

if "result" in st.session_state:
    result = st.session_state["result"]
    included = result[result["decision"] == "INCLUDE"]
    st.metric("INCLUDE", len(included))
    st.metric("EXCLUDE", len(result) - len(included))
    st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button("Download INCLUDE CSV", included.to_csv(index=False, encoding="utf-8-sig"), st.session_state["output_name"], "text/csv")
    st.download_button("Download all decisions", result.to_csv(index=False, encoding="utf-8-sig"), "screening_all.csv", "text/csv")


def run() -> None:
    """Entry point used by the repository launcher."""
