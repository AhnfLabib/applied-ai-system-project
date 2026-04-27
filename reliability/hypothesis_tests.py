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


@given(text())
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
        if difficulty in ["Easy", "Normal", "Hard", "Unknown"] and not any(difficulty in s for s in _range_interesting):
            _range_interesting.append(
                f"get_range_for_difficulty('{difficulty}') → ({low}, {high})"
            )
