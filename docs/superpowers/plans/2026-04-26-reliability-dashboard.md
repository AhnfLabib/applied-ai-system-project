# Reliability Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Streamlit "Reliability Dashboard" page that stress-tests all four game logic functions using hypothesis-generated inputs and displays a per-function pass/fail breakdown.

**Architecture:** Implement `logic_utils.py` (completing the intended refactor), have `hypothesis_tests.py` import from it (pure Python, no streamlit dependency), and expose results via `runner.run_all()`. The dashboard lives in `pages/` so Streamlit's multipage convention picks it up automatically under the same `streamlit run app.py` command.

**Tech Stack:** Python 3, Streamlit, hypothesis (property-based testing), pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `logic_utils.py` | Implement | The 4 game logic functions — pure Python, no streamlit |
| `app.py` | Minimal edit | Replace inline function definitions with `from logic_utils import ...` |
| `requirements.txt` | Modify | Add `hypothesis>=6.0.0` |
| `reliability/__init__.py` | Create | Empty — makes `reliability/` a package |
| `reliability/hypothesis_tests.py` | Create | 4 `@given`-decorated test functions with module-level counters |
| `reliability/runner.py` | Create | `run_all()` — resets state, calls each test, returns `List[dict]` |
| `pages/2_Reliability_Dashboard.py` | Create | Streamlit page — button, spinner, per-function expanders, summary |
| `tests/test_logic_utils.py` | Create | TDD tests for logic_utils before implementing it |
| `tests/test_runner.py` | Create | TDD tests for runner structure before implementing it |

---

## Task 1: Implement `logic_utils.py`

**Files:**
- Modify: `logic_utils.py`
- Create: `tests/test_logic_utils.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_logic_utils.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score


def test_get_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_get_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_get_range_hard_larger_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


def test_check_guess_win():
    outcome, msg = check_guess(50, 50)
    assert outcome == "Win"
    assert isinstance(msg, str)


def test_check_guess_too_low():
    outcome, _ = check_guess(9, 100)
    assert outcome == "Too Low"


def test_check_guess_string_secret():
    outcome, _ = check_guess(9, "100")
    assert outcome == "Too Low"


def test_parse_guess_valid_int():
    ok, val, err = parse_guess("42")
    assert ok is True
    assert val == 42
    assert err is None


def test_parse_guess_decimal():
    ok, val, err = parse_guess("3.7")
    assert ok is True
    assert val == 3


def test_parse_guess_empty():
    ok, val, err = parse_guess("")
    assert ok is False
    assert val is None
    assert isinstance(err, str)


def test_update_score_too_high():
    assert update_score(10, "Too High", 1) == 5


def test_update_score_win_minimum():
    result = update_score(0, "Win", 100)
    assert result >= 10
```

- [ ] **Step 2: Run to confirm all 11 tests fail**

```bash
pytest tests/test_logic_utils.py -v
```

Expected: 11 FAILED with `NotImplementedError`

- [ ] **Step 3: Implement `logic_utils.py`**

Replace entire file content:

```python
def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."
    if raw == "":
        return False, None, "Enter a guess."
    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."
    return True, value, None


def check_guess(guess, secret):
    guess = int(guess)
    secret = int(secret)
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📈 Go LOWER!"
    return "Too Low", "📉 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points
    if outcome == "Too High":
        return current_score - 5
    if outcome == "Too Low":
        return current_score - 5
    return current_score
```

- [ ] **Step 4: Run tests to confirm all pass**

```bash
pytest tests/test_logic_utils.py -v
```

Expected: 11 PASSED

- [ ] **Step 5: Commit**

```bash
git add logic_utils.py tests/test_logic_utils.py
git commit -m "feat: implement game logic functions in logic_utils"
```

---

## Task 2: Update `app.py` to import from `logic_utils`

**Files:**
- Modify: `app.py` (lines 1–57 — replace the 4 function definitions with one import line)

- [ ] **Step 1: Replace the function definitions with an import**

In `app.py`, replace this block (lines 1–57):

```python
import random
import streamlit as st

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    guess = int(guess)
    secret = int(secret)
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📈 Go LOWER!"
    else:
        return "Too Low", "📉 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
```

With:

```python
import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score
```

Everything from line 59 (`st.set_page_config(...)`) onwards stays exactly as-is.

- [ ] **Step 2: Run existing tests to confirm nothing broke**

```bash
pytest tests/test_game_logic.py tests/test_logic_utils.py -v
```

Expected: all tests PASS (`from app import check_guess` still works because `app` re-exports it from `logic_utils`)

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "refactor: import game logic from logic_utils in app.py"
```

---

## Task 3: Add hypothesis and create package skeleton

**Files:**
- Modify: `requirements.txt`
- Create: `reliability/__init__.py`

- [ ] **Step 1: Add hypothesis to requirements**

In `requirements.txt`, add a new line:

```
hypothesis>=6.0.0
```

Final file:
```
streamlit>=1.21.0
altair<5
pytest
hypothesis>=6.0.0
```

- [ ] **Step 2: Install the new dependency**

```bash
pip install hypothesis
```

Expected: hypothesis installs successfully, ends with `Successfully installed hypothesis-...`

- [ ] **Step 3: Create the empty package init**

Create `reliability/__init__.py` with empty content (zero bytes).

- [ ] **Step 4: Commit**

```bash
git add requirements.txt reliability/__init__.py
git commit -m "feat: add hypothesis dependency and reliability package skeleton"
```

---

## Task 4: Write failing tests for `runner.run_all()`

**Files:**
- Create: `tests/test_runner.py`

- [ ] **Step 1: Write the test file**

Create `tests/test_runner.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reliability.runner import run_all


def test_run_all_returns_four_results():
    results = run_all()
    assert len(results) == 4


def test_run_all_result_keys():
    results = run_all()
    for r in results:
        assert "name" in r
        assert "tested" in r
        assert "passed" in r
        assert "interesting" in r
        assert "failure" in r


def test_run_all_correct_types():
    results = run_all()
    for r in results:
        assert isinstance(r["name"], str)
        assert isinstance(r["tested"], int)
        assert isinstance(r["passed"], bool)
        assert isinstance(r["interesting"], list)


def test_run_all_all_pass():
    results = run_all()
    for r in results:
        assert r["passed"] is True, f"{r['name']} failed: {r['failure']}"


def test_run_all_function_names():
    results = run_all()
    names = {r["name"] for r in results}
    assert names == {"check_guess", "parse_guess", "update_score", "get_range_for_difficulty"}


def test_run_all_sufficient_coverage():
    results = run_all()
    for r in results:
        assert r["tested"] >= 100, f"{r['name']} tested too few cases: {r['tested']}"
```

- [ ] **Step 2: Run to confirm it fails with the right error**

```bash
pytest tests/test_runner.py -v
```

Expected: ERROR — `ModuleNotFoundError: No module named 'reliability.runner'`

---

## Task 5: Create `reliability/hypothesis_tests.py`

**Files:**
- Create: `reliability/hypothesis_tests.py`

- [ ] **Step 1: Create the file**

Create `reliability/hypothesis_tests.py`:

```python
from hypothesis import given, settings
from hypothesis.strategies import integers, text, sampled_from
from logic_utils import check_guess, parse_guess, update_score, get_range_for_difficulty

# --- check_guess ---
_check_counter = [0]
_check_interesting = []


@given(integers(), integers())
@settings(max_examples=300)
def test_check_guess_properties(guess, secret):
    _check_counter[0] += 1
    outcome, message = check_guess(guess, secret)
    assert outcome in ("Win", "Too High", "Too Low")
    assert isinstance(message, str) and len(message) > 0
    if outcome == "Win":
        assert guess == secret
    elif outcome == "Too High":
        assert guess > secret
    else:
        assert guess < secret
    if len(_check_interesting) < 3:
        if guess == secret:
            _check_interesting.append(
                f"check_guess({guess}, {secret}) → ('{outcome}', '{message}')"
            )
        elif abs(guess) > 10_000 or abs(secret) > 10_000:
            _check_interesting.append(f"check_guess({guess}, {secret}) → ('{outcome}', ...)")


# --- parse_guess ---
_parse_counter = [0]
_parse_interesting = []


@given(text())
@settings(max_examples=300)
def test_parse_guess_properties(raw):
    _parse_counter[0] += 1
    result = parse_guess(raw)
    assert isinstance(result, tuple) and len(result) == 3
    ok, value, error = result
    assert isinstance(ok, bool)
    if ok:
        assert isinstance(value, int)
        assert error is None
    else:
        assert value is None
        assert isinstance(error, str) and len(error) > 0
    if len(_parse_interesting) < 3:
        if "." in raw and ok:
            _parse_interesting.append(
                f"parse_guess({repr(raw[:20])}) → ({ok}, {value}, {error})"
            )
        elif raw == "":
            _parse_interesting.append(f"parse_guess('') → ({ok}, {value}, {repr(error)})")


# --- update_score ---
_score_counter = [0]
_score_interesting = []


@given(
    integers(),
    sampled_from(["Win", "Too High", "Too Low", "Other"]),
    integers(min_value=0),
)
@settings(max_examples=300)
def test_update_score_properties(current_score, outcome, attempt_number):
    _score_counter[0] += 1
    new_score = update_score(current_score, outcome, attempt_number)
    if outcome == "Too High":
        assert new_score == current_score - 5
    elif outcome == "Too Low":
        assert new_score == current_score - 5
    elif outcome == "Win":
        assert new_score >= current_score + 10
    else:
        assert new_score == current_score
    if len(_score_interesting) < 3:
        if attempt_number == 0:
            _score_interesting.append(
                f"update_score({current_score}, '{outcome}', 0) → {new_score}"
            )
        elif outcome == "Win" and new_score == current_score + 10:
            _score_interesting.append(
                f"update_score({current_score}, 'Win', {attempt_number}) → {new_score} (min bonus clamped)"
            )


# --- get_range_for_difficulty ---
_range_counter = [0]
_range_interesting = []


@given(sampled_from(["Easy", "Normal", "Hard", "Unknown"]))
@settings(max_examples=300)
def test_get_range_properties(difficulty):
    _range_counter[0] += 1
    low, high = get_range_for_difficulty(difficulty)
    assert low < high
    assert low >= 1
    normal_low, normal_high = get_range_for_difficulty("Normal")
    if difficulty == "Hard":
        assert (high - low) >= (normal_high - normal_low)
    if len(_range_interesting) < 4:
        if not any(difficulty in s for s in _range_interesting):
            _range_interesting.append(
                f"get_range_for_difficulty('{difficulty}') → ({low}, {high})"
            )
```

- [ ] **Step 2: Run the runner tests to confirm error message changed**

```bash
pytest tests/test_runner.py -v
```

Expected: ERROR — `ModuleNotFoundError: No module named 'reliability.runner'` (unchanged — runner still missing)

---

## Task 6: Create `reliability/runner.py`

**Files:**
- Create: `reliability/runner.py`

- [ ] **Step 1: Create the file**

Create `reliability/runner.py`:

```python
from reliability.hypothesis_tests import (
    test_check_guess_properties,
    _check_counter,
    _check_interesting,
    test_parse_guess_properties,
    _parse_counter,
    _parse_interesting,
    test_update_score_properties,
    _score_counter,
    _score_interesting,
    test_get_range_properties,
    _range_counter,
    _range_interesting,
)
from logic_utils import check_guess


def _run_one(name, test_fn, counter, interesting):
    counter[0] = 0
    interesting.clear()
    try:
        test_fn()
        passed = True
        failure = None
    except Exception as e:
        passed = False
        failure = str(e)
    return {
        "name": name,
        "tested": counter[0],
        "passed": passed,
        "interesting": list(interesting[:3]),
        "failure": failure,
    }


def run_all():
    results = []

    result = _run_one(
        "check_guess", test_check_guess_properties, _check_counter, _check_interesting
    )
    if result["passed"]:
        try:
            outcome, _ = check_guess(9, "100")
            assert outcome == "Too Low", f"Expected 'Too Low' but got '{outcome}'"
            if len(result["interesting"]) < 3:
                result["interesting"].append(
                    'check_guess(9, "100") → ("Too Low", ...) [string secret, no TypeError]'
                )
        except TypeError as e:
            result["passed"] = False
            result["failure"] = f"check_guess(9, '100') raised TypeError: {e}"
    results.append(result)

    results.append(
        _run_one("parse_guess", test_parse_guess_properties, _parse_counter, _parse_interesting)
    )
    results.append(
        _run_one(
            "update_score",
            test_update_score_properties,
            _score_counter,
            _score_interesting,
        )
    )
    results.append(
        _run_one(
            "get_range_for_difficulty",
            test_get_range_properties,
            _range_counter,
            _range_interesting,
        )
    )

    return results
```

- [ ] **Step 2: Run all tests to confirm they pass**

```bash
pytest tests/test_runner.py tests/test_logic_utils.py tests/test_game_logic.py -v
```

Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add reliability/hypothesis_tests.py reliability/runner.py tests/test_runner.py
git commit -m "feat: add hypothesis tests and reliability runner"
```

---

## Task 7: Create `pages/2_Reliability_Dashboard.py`

**Files:**
- Create: `pages/2_Reliability_Dashboard.py`

- [ ] **Step 1: Create the file**

Create `pages/2_Reliability_Dashboard.py`:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add pages/2_Reliability_Dashboard.py
git commit -m "feat: add Reliability Dashboard Streamlit page"
```

---

## Task 8: Smoke test the full app

- [ ] **Step 1: Run the full test suite one final time**

```bash
pytest -v
```

Expected: all tests PASS (test_game_logic.py, test_logic_utils.py, test_runner.py)

- [ ] **Step 2: Start the app**

```bash
streamlit run app.py
```

Expected: browser opens, shows "🎮 Game Glitch Investigator" with a sidebar navigation showing both pages.

- [ ] **Step 3: Verify the game page still works**

Play one round: pick a difficulty, submit a guess, confirm hints and scoring work correctly.

- [ ] **Step 4: Navigate to Reliability Dashboard and run the check**

Click "Reliability Dashboard" in the sidebar. Click "Run Reliability Check". Confirm:
- Spinner appears while tests run (a few seconds)
- 4 expanders appear, all with ✅
- Each expander shows a `tested` count ≥ 100
- At least one interesting case is shown per function
- Summary line reads "4/4 functions passed · 1,200 total cases tested"

- [ ] **Step 5: Verify "Clear Results" works**

Click "Clear Results" — expanders disappear. Click "Run Reliability Check" again — results reappear.

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "feat: complete reliability dashboard — hypothesis stress-testing integrated into Streamlit app"
```
