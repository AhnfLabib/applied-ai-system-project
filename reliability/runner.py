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
