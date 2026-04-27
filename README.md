# 🎮 Game Glitch Investigator + Reliability Dashboard

## Original Project

**Game Glitch Investigator** is a number-guessing game built with Streamlit where an AI generated buggy code on purpose. The player picks a difficulty, guesses a secret number, and gets "Higher/Lower" hints — but the original AI-generated version had backwards hints, a secret that reset on every button click, and difficulty ranges that weren't respected. The project's goal was to find and fix those bugs, then refactor the logic into a testable module.

---

## New System: Reliability Dashboard

The final project extends the fixed game with a **Reliability Dashboard** — a second Streamlit page that stress-tests all four game logic functions using `hypothesis`, a property-based testing library. Instead of hand-writing specific test cases, hypothesis automatically generates hundreds of inputs (including edge cases no human would think of) and verifies that the logic holds up for all of them. Results are displayed per-function with pass/fail status, case counts, and interesting examples that hypothesis surfaced.

**Advanced AI feature type:** Reliability/Testing System

---

## Architecture

```
applied-ai-system-project/
├── app.py                          # Game UI (Streamlit page 1)
├── logic_utils.py                  # Pure Python game logic — no Streamlit
├── pages/
│   └── 2_Reliability_Dashboard.py  # Dashboard UI (Streamlit page 2)
├── reliability/
│   ├── hypothesis_tests.py         # 4 @given-decorated test functions with counters
│   └── runner.py                   # run_all() — calls each test, returns results
├── tests/
│   ├── test_game_logic.py          # Original bug-encoding tests
│   ├── test_logic_utils.py         # Unit tests for logic_utils
│   └── test_runner.py              # Tests for the runner output structure
└── requirements.txt
```

**Data flow:**
1. User navigates to Reliability Dashboard and clicks "Run Reliability Check"
2. Dashboard calls `runner.run_all()`
3. Runner resets counters, calls each hypothesis test function, catches failures
4. Each test generates ~300 random inputs via `@given`, checks assertions
5. Results (name, tested count, pass/fail, interesting cases) stored in `st.session_state`
6. Dashboard renders per-function expanders and a summary line

---

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (both pages available from the sidebar)
streamlit run app.py
```

---

## Sample Interactions

### 1. Playing the game (Normal difficulty)

```
Range: 1–100 | Attempts allowed: 8

Guess: 50  →  📈 Go LOWER!
Guess: 25  →  📉 Go HIGHER!
Guess: 37  →  🎉 Correct! Final score: 70
```

### 2. Reliability Dashboard — all functions pass

After clicking "Run Reliability Check":

```
✅ check_guess           — 300 cases tested
   Interesting: check_guess(0, 0) → ('Win', '🎉 Correct!')
                check_guess(-14467, 12881) → ('Too Low', ...)
                check_guess(9, "100") → ("Too Low", ...) [string secret, no TypeError]

✅ parse_guess           — 300 cases tested
   Interesting: parse_guess('') → (False, None, 'Enter a guess.')

✅ update_score          — 300 cases tested
   Interesting: update_score(0, 'Win', 0) → 90
                update_score(-28368, 'Win', 0) → -28278

✅ get_range_for_difficulty — 4 cases tested
   Interesting: get_range_for_difficulty('Easy') → (1, 20)
                get_range_for_difficulty('Hard') → (1, 200)
                get_range_for_difficulty('Unknown') → (1, 100)

4/4 functions passed · 904 total cases tested
```

### 3. Reliability Dashboard — catching a bug

If someone introduced a bug in `check_guess` (e.g., flipped `>` to `<`):

```
❌ check_guess  — 2 cases tested
   Failure: assert 'Too High' == 'Win'
            Falsifying example: check_guess(guess=0, secret=0)
```

Hypothesis finds the minimal failing input automatically.

---

## Design Decisions and Trade-offs

**Why `logic_utils.py` instead of importing from `app.py`?**
`app.py` runs Streamlit UI code at module level (`st.set_page_config`, `st.title`, etc.). Importing from it inside the reliability module would trigger those calls in the wrong context. Moving logic to `logic_utils.py` (pure Python, zero Streamlit) eliminates this entirely. The game still works because `app.py` imports from `logic_utils`.

**Why `sampled_from` for `get_range_for_difficulty`?**
The function only has four meaningful inputs. Using `text()` would generate arbitrary strings, and the difficulty-specific assertions (`Hard range ≥ Normal range`) would almost never trigger. `sampled_from(["Easy", "Normal", "Hard", "Unknown"])` tests exactly the cases that matter. Hypothesis correctly stops at 4 unique examples rather than running 300 redundant ones.

**Why store results in `st.session_state`?**
Hypothesis tests take a few seconds to run. Storing results in session state means navigating away and back doesn't re-trigger the run. The "Clear Results" button lets the user reset explicitly.

**Trade-off: UI not tested**
The dashboard tests pure logic only. Streamlit UI behavior (button clicks, page navigation, session state transitions) is not covered. Manual testing covers that layer.

---

## Testing Summary

| Test file | What it covers | Tests |
|---|---|---|
| `tests/test_game_logic.py` | Original bug-encoding tests — correct behavior for known bugs | 10 |
| `tests/test_logic_utils.py` | Unit tests for all 4 functions in `logic_utils.py` | 11 |
| `tests/test_runner.py` | `run_all()` returns correct structure, all functions pass, sufficient coverage | 6 |
| **hypothesis (via dashboard)** | Property-based stress-test: 300 random inputs per function at runtime | ~904 |

Run the static suite:
```bash
pytest -v
# 27 passed
```

---

## Reflection

Building the Reliability Dashboard taught me that automated testing has two distinct layers: verifying specific known cases (what `test_game_logic.py` does) and verifying general behavioral properties across a wide input space (what hypothesis does). The two are complementary — you need both.

The most surprising moment was discovering that `hypothesis` stops early when the input space is finite. With only four valid difficulty strings, it runs 4 examples, not 300. That forced me to think about what "sufficient coverage" actually means for a specific function, rather than applying one threshold to all functions.

The reliability framing also clarified why this matters for AI-generated code: when an AI writes a function, you don't always know what edge cases it considered. Property-based testing makes you state your assumptions explicitly as assertions, then lets a search algorithm find the inputs where those assumptions break. That's a more honest way to validate AI-generated code than reading it and hoping it looks right.

---

## What This Project Says About Me as an AI Engineer

I approach AI not just as a tool to generate output, but as something that needs to be verified. When I extended this project, I didn't stop at "the code works" — I built a system to prove it works, automatically, across inputs I didn't hand-pick. That instinct — to question AI-generated code and put structure around validating it — is something I want to carry into every project I work on. This project also showed me that good AI engineering means knowing when to use AI and when to use deterministic tools: hypothesis doesn't need an LLM to find edge cases, and that's exactly the right tool for this job. I'm most proud of the fact that the reliability system is integrated into the app itself, not a separate script I'd have to remember to run.

---

## Demo - https://drive.google.com/file/d/1cVj29TzjM_rj3xqqpCjsz4stOgP1MVD4/view?usp=sharing 

![Fixed winning game screenshot](assets/win.jpeg)
![Reliability Dashboard](assets/image.png)
