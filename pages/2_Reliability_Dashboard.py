import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from reliability.runner import run_all

st.set_page_config(page_title="Reliability Dashboard", page_icon="🧪")
st.title("🧪 Reliability Dashboard")
st.caption("Stress-tests each game logic function with hundreds of auto-generated inputs.")

col1, col2 = st.columns([2, 1])
with col1:
    run_btn = st.button("Run Reliability Check", type="primary")
with col2:
    if st.button("Clear Results"):
        st.session_state.pop("reliability_results", None)
        st.rerun()

if run_btn:
    with st.spinner("Running hypothesis tests — generating inputs..."):
        st.session_state["reliability_results"] = run_all()

if "reliability_results" in st.session_state:
    results = st.session_state["reliability_results"]

    passed_count = sum(1 for r in results if r["passed"])
    total_tested = sum(r["tested"] for r in results)

    for r in results:
        icon = "✅" if r["passed"] else "❌"
        with st.expander(f"{icon} `{r['name']}` — {r['tested']} cases tested"):
            st.write(f"**Status:** {'Passed' if r['passed'] else 'Failed'}")
            st.write(f"**Cases tested:** {r['tested']}")
            if r["interesting"]:
                st.write("**Interesting cases found:**")
                for case in r["interesting"]:
                    st.code(case)
            if not r["passed"] and r["failure"]:
                st.error(f"**Failure:**\n{r['failure']}")

    st.divider()
    st.caption(
        f"{passed_count}/{len(results)} functions passed · {total_tested:,} total cases tested"
    )
