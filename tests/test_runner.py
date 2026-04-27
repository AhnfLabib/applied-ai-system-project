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
