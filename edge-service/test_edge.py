"""
Tests for the edge detection service.
Unit tests run without a server. Integration tests require: uv run python main.py

Run:
    uv run python test_edge.py
"""
import sys

from app.services.edge import calculate_edge


def test_buy_yes():
    # Model says 71%, market says 58% → edge = +0.13 → BUY YES
    r = calculate_edge(71, 0.58)
    assert r.signal == "BUY YES",  f"expected BUY YES, got {r.signal}"
    assert r.edge == 0.13,         f"expected edge=0.13, got {r.edge}"
    assert r.ev > 0,               f"expected positive EV"
    assert r.kelly_fraction > 0,   f"expected positive Kelly"
    print(f"PASS  BUY YES   edge={r.edge}  ev={r.ev}  kelly={r.kelly_fraction}")


def test_buy_no():
    # Model says 40%, market says 58% → edge = -0.18 → BUY NO
    r = calculate_edge(40, 0.58)
    assert r.signal == "BUY NO",  f"expected BUY NO, got {r.signal}"
    assert r.edge < 0
    assert r.kelly_fraction == 0  # Kelly only applies to positive edges
    print(f"PASS  BUY NO    edge={r.edge}  ev={r.ev}  kelly={r.kelly_fraction}")


def test_no_edge():
    # Model says 60%, market says 58% → edge = +0.02 → too small
    r = calculate_edge(60, 0.58)
    assert r.signal == "NO EDGE", f"expected NO EDGE, got {r.signal}"
    print(f"PASS  NO EDGE   edge={r.edge}  ev={r.ev}  kelly={r.kelly_fraction}")


def test_exact_threshold():
    # Edge exactly at threshold (7%) → BUY YES
    r = calculate_edge(65, 0.58)
    assert r.edge == 0.07
    assert r.signal == "BUY YES", f"expected BUY YES at exact threshold, got {r.signal}"
    print(f"PASS  THRESHOLD edge={r.edge}  signal={r.signal}")


def test_fifty_fifty():
    # Model and market agree at 50% → no edge, zero EV
    r = calculate_edge(50, 0.50)
    assert r.signal == "NO EDGE"
    assert r.edge == 0.0
    assert r.ev == 0.0
    print(f"PASS  50/50     edge={r.edge}  ev={r.ev}")


if __name__ == "__main__":
    print("=== Unit Tests ===\n")
    tests = [test_buy_yes, test_buy_no, test_no_edge, test_exact_threshold, test_fifty_fifty]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1

    print(f"\n{'All tests passed.' if not failed else f'{failed} test(s) failed.'}")
    sys.exit(failed)
