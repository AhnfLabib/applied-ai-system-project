# Model Card — Reliability Dashboard

## System Overview

The Reliability Dashboard is a second Streamlit page added to the Glitchy Guesser app. It uses the `hypothesis` library to automatically generate hundreds of inputs for each game logic function (`check_guess`, `parse_guess`, `update_score`, `get_range_for_difficulty`) and reports a per-function pass/fail breakdown with interesting edge cases found.

---

## System Limitations and Biases

- **Only tests pure logic, not the UI.** The dashboard stress-tests the four functions in `logic_utils.py` but cannot test anything that happens inside the Streamlit UI layer — button clicks, session state transitions, or page navigation.
- **`get_range_for_difficulty` gets 4 test cases, not 300.** Because there are only four valid difficulty strings (`"Easy"`, `"Normal"`, `"Hard"`, `"Unknown"`), hypothesis exhausts the input space after 4 examples and stops. The other three functions receive 300 cases each. This is expected behavior, not a bug.
- **Interesting cases are capped at 3 per function.** The dashboard only surfaces up to 3 notable examples. A genuinely unusual input found late in the run might not appear.
- **hypothesis generates inputs humans would never type.** For `parse_guess`, hypothesis explores arbitrary Unicode strings. While the function handles them correctly, most are not realistic user inputs. The coverage is thorough but not always meaningful in a practical sense.

---

## Potential Misuse Prevention

- The dashboard is **read-only** — clicking "Run Reliability Check" only executes Python functions internally and writes to `st.session_state`. It does not modify any game state, files, or external systems.
- There are **no external API calls or network requests** in the reliability module. It runs entirely locally with no keys, credentials, or third-party services involved.
- The dashboard cannot be used to cheat at the game — it only shows function behavior, not the current session's secret number (that stays in the game page's `st.session_state`).

---

## Testing Surprises

**Surprise 1: `sampled_from` stops early.**
I expected `@settings(max_examples=300)` to always produce 300 test cases. For `get_range_for_difficulty`, hypothesis detected that `sampled_from(["Easy", "Normal", "Hard", "Unknown"])` only has 4 unique values and stopped after testing all 4. The counter showed 4, not 300. I had to update the coverage threshold test to expect `>= 4` for that function specifically instead of `>= 100` for all functions.

**Surprise 2: Module-level state resets correctly between runs.**
The counters (`_check_counter`, etc.) are module-level lists that persist across calls. I was initially unsure whether calling `run_all()` twice in the same session would double-count. It doesn't — `_run_one()` resets each counter to zero and clears the interesting list before calling the test function, so results are always fresh.

**Surprise 3: `parse_guess` handled every Unicode string without crashing.**
When hypothesis ran 300 arbitrary text inputs through `parse_guess`, every single one returned a valid 3-tuple. The broad `except Exception` in `parse_guess` caught everything hypothesis could generate — emoji, null-like characters, very long strings. No failures.

---

## AI Collaboration Examples

### Helpful: Architectural decision to import from `logic_utils`

When designing the reliability module, AI (Claude Code) flagged a real problem before any code was written: if `hypothesis_tests.py` imported from `app.py`, it would trigger Streamlit's module-level UI code (`st.set_page_config`, `st.title`, etc.) every time the reliability module was loaded. This would break the dashboard page.

The suggested fix was to implement the game functions in `logic_utils.py` (which was already a planned refactor target) and have `hypothesis_tests.py` import from there instead. Since `logic_utils.py` is pure Python with no Streamlit imports, the reliability module loads cleanly in any context. I verified this by running `python -c "from reliability.hypothesis_tests import test_check_guess_properties; print('OK')"` successfully outside of Streamlit.

### Flawed: Changing `sampled_from` to `text()` without authorization

During implementation, a subagent changed the strategy for `test_get_range_properties` from `@given(sampled_from(["Easy", "Normal", "Hard", "Unknown"]))` to `@given(text())`. The reasoning was that `sampled_from` with 4 values wouldn't generate enough examples to meet the `>= 100` coverage threshold.

This was wrong for two reasons: (1) it violated the spec — the intent was to test known difficulty levels, not fuzz with arbitrary strings, and (2) `text()` would rarely generate `"Hard"` or `"Easy"` by chance, meaning the difficulty-specific assertions would almost never run. A spec compliance review caught the change and reverted it. The real fix was to lower the coverage threshold for that specific function, not to change the strategy.
