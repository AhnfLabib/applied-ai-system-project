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
