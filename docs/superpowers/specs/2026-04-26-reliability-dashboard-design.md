# Reliability Dashboard — Design Spec
**Date:** 2026-04-26
**Project:** Game Glitch Investigator / Glitchy Guesser
**Feature type:** Reliability/Testing System (CodePath AI110 Week 9 advanced AI feature)

---

## Overview

Add a second Streamlit page ("Reliability Dashboard") to the existing Glitchy Guesser app. The dashboard uses the `hypothesis` library to automatically generate hundreds of random/edge-case inputs for each game logic function, runs assertions against them, and displays a per-function breakdown of results. No external AI API is required.

This extends the existing hand-written pytest suite (`tests/test_game_logic.py`) by stress-testing the same logic with inputs that no human would think to write.

---

## File Structure

```
applied-ai-system-project/
├── app.py                              (unchanged — game UI)
├── reliability/
│   ├── __init__.py                     (empty)
│   ├── hypothesis_tests.py             (4 hypothesis test functions)
│   └── runner.py                       (orchestrates tests, returns result dicts)
├── pages/
│   └── 2_Reliability_Dashboard.py      (new Streamlit page)
├── tests/
│   └── test_game_logic.py              (existing — unchanged)
└── requirements.txt                    (add: hypothesis)
```

Streamlit's multipage convention automatically discovers `pages/` — no changes to `app.py` are needed. Both game and dashboard run under a single `streamlit run app.py`.

---

## Module: `reliability/hypothesis_tests.py`

Contains four `@given`-decorated test functions, one per game logic function. Each uses:
- A module-level mutable counter (`[0]`) and interesting-cases list, reset before each run and read after
- `@settings(max_examples=300)` for thorough coverage without being slow

`@given`-decorated functions cannot return values, so the counter and interesting list are module-level state. `runner.py` resets them, calls the test function, then reads them.

### `test_check_guess_properties`
- **Strategy:** `@given(integers(), integers())`
- **Assertions:**
  - `outcome` is always one of `"Win"`, `"Too High"`, `"Too Low"`
  - `message` is always a non-empty string
  - Logical consistency: `Win` ↔ `guess == secret`, `Too High` ↔ `guess > secret`, `Too Low` ↔ `guess < secret`
  - Explicit inline call `check_guess(9, "100")` inside the test body asserts no `TypeError` and returns `"Too Low"` (string secret edge case — not hypothesis-generated since strategy is `integers()`)
- **Interesting cases collected:** exact wins (`guess == secret`), very large/negative integers

### `test_parse_guess_properties`
- **Strategy:** `@given(text())`
- **Assertions:**
  - Return value is always a 3-tuple `(bool, int|None, str|None)`
  - If `ok=True`, value is an int; if `ok=False`, error is a non-empty string
- **Interesting cases collected:** decimal strings like `"3.7"`, whitespace-only input, very long strings, `"0"`, negative number strings like `"-5"`

### `test_update_score_properties`
- **Strategy:** `@given(integers(), sampled_from(["Win", "Too High", "Too Low", "Other"]), integers(min_value=0))`
- **Assertions:**
  - `"Too High"` and `"Too Low"` outcomes always decrease score by exactly 5
  - `"Win"` outcome always increases score by at least 10
  - `"Other"` outcome leaves score unchanged
- **Interesting cases collected:** `attempt_number=0`, large attempt numbers where win bonus would go below minimum, score starting at 0

### `test_get_range_properties`
- **Strategy:** `@given(sampled_from(["Easy", "Normal", "Hard", "Unknown"]))`
- **Assertions:**
  - `low < high` always
  - `low >= 1` always
  - Hard range size ≥ Normal range size
- **Interesting cases collected:** `"Unknown"` fallback behavior (should default to Normal range)

---

## Module: `reliability/runner.py`

Imports the four test functions and runs each one, returning a list of result dicts.

### Result dict shape per function
```python
{
    "name": str,           # e.g. "check_guess"
    "tested": int,         # number of examples hypothesis generated
    "passed": bool,        # True if no assertion failed
    "interesting": list,   # up to 3 notable input/output examples as strings
    "failure": str | None  # hypothesis failure summary if passed=False, else None
}
```

### Behavior
- Each test is called inside a `try/except` block
- On `AssertionError` or any exception, `passed=False` and `failure` captures `str(e)`
- After the call, counter and interesting cases are read from the closure
- Returns `List[dict]` — one entry per function

---

## Page: `pages/2_Reliability_Dashboard.py`

### Layout

```
🧪 Reliability Dashboard
Automatically stress-tests game logic with hundreds of generated inputs.

[ Run Reliability Check ]   ← button, shows spinner while running

--- results (rendered after run, stored in st.session_state) ---

✅ check_guess        — 300 cases tested   [expander]
✅ parse_guess        — 300 cases tested   [expander]
✅ update_score       — 300 cases tested   [expander]
✅ get_range_for_difficulty — 300 cases tested [expander]

Inside each expander:
  - Cases tested: 300
  - Status: Passed / Failed
  - Interesting cases found:
    • check_guess(0, 0) → ('Win', '🎉 Correct!')
    • check_guess(-999, 1) → ('Too Low', '📉 Go HIGHER!')
    • check_guess(9, "100") → ('Too Low', ...) [no TypeError]
  - [if failed] Failure: <hypothesis failure message>

─────────────────────────────────────────
4/4 functions passed · 1,200 total cases tested
```

### State
- Results stored in `st.session_state["reliability_results"]` so they persist across Streamlit reruns without re-running hypothesis
- A "Clear results" button resets the session state key

---

## Data Flow

```
User clicks "Run Reliability Check"
        ↓
pages/2_Reliability_Dashboard.py calls runner.run_all()
        ↓
runner.py calls each hypothesis test function in try/except
        ↓
Each test generates ~300 random inputs via @given, checks assertions
        ↓
runner.py collects {name, tested, passed, interesting, failure} per function
        ↓
Results stored in st.session_state
        ↓
Dashboard renders per-function expanders + summary line
```

---

## Dependencies

Add to `requirements.txt`:
```
hypothesis>=6.0.0
```

No other new dependencies. No external API keys or network calls required.

---

## What this satisfies (CodePath requirements)

- **Advanced AI feature:** Reliability/Testing System — fully integrated into the application (not a standalone script), accessible from the same `streamlit run app.py` entrypoint
- **Logging/guardrails:** Results stored in session state; failures surface the exact input hypothesis found
- **System diagram component:** Dashboard page + reliability module form a distinct testable subsystem alongside the game
- **Stretch feature eligible:** Test Harness/Evaluation Script (+2 points)
