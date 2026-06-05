"""
Unit tests for the indicator math in institutional_scanner.

These run without network access — synthetic price series only.
"""

import numpy as np
import pandas as pd
import pytest

from institutional_scanner import (
    calculate_aroon,
    calculate_calmar_ratio,
    calculate_fibonacci_levels,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_williams_r,
)


@pytest.fixture
def trending_series():
    """Steady-uptrend OHLC: predictable for sanity-checking direction-dependent indicators."""
    n = 100
    close = pd.Series(np.linspace(100, 200, n))
    high = close * 1.01
    low = close * 0.99
    return high, low, close


@pytest.fixture
def flat_series():
    """Constant-price series: indicators should be at trivial extremes or NaN-safe."""
    n = 50
    close = pd.Series([100.0] * n)
    high = pd.Series([100.0] * n)
    low = pd.Series([100.0] * n)
    return high, low, close


def test_williams_r_bounds(trending_series):
    high, low, close = trending_series
    value = calculate_williams_r(high, low, close)
    assert -100.0 <= value <= 0.0


def test_williams_r_uptrend_near_zero(trending_series):
    """In a steady uptrend, close ≈ recent-high, so %R should be close to 0."""
    high, low, close = trending_series
    value = calculate_williams_r(high, low, close)
    assert value > -25.0


def test_fibonacci_levels_ordering(trending_series):
    high, low, _ = trending_series
    levels = calculate_fibonacci_levels(high, low, lookback=60)
    # 0.0 is the high, 1.0 is the low — levels must be monotonically decreasing
    ordered = [levels[k] for k in ["0.0", "0.236", "0.382", "0.500", "0.618", "0.786", "1.0"]]
    assert ordered == sorted(ordered, reverse=True)


def test_fibonacci_levels_50_pct_is_midpoint(trending_series):
    high, low, _ = trending_series
    levels = calculate_fibonacci_levels(high, low, lookback=60)
    expected_mid = (levels["0.0"] + levels["1.0"]) / 2
    assert levels["0.500"] == pytest.approx(expected_mid, rel=1e-9)


def test_sharpe_handles_empty_returns():
    assert calculate_sharpe_ratio(pd.Series([])) == 0.0
    assert calculate_sharpe_ratio(pd.Series([0.01])) == 0.0


def test_sharpe_does_not_crash_on_constant_returns():
    """Constant returns must not raise. Numerical FP makes the result implementation-defined,
    but it must be a finite float so downstream scoring keeps working."""
    returns = pd.Series([0.001] * 100)
    result = calculate_sharpe_ratio(returns)
    assert isinstance(result, float)
    assert np.isfinite(result) or result == 0.0


def test_sortino_handles_no_downside():
    """All-positive returns ⇒ no downside ⇒ guarded zero rather than ZeroDivisionError."""
    returns = pd.Series([0.001] * 100)
    assert calculate_sortino_ratio(returns) == 0.0


def test_max_drawdown_monotonic_up_is_zero(trending_series):
    _, _, close = trending_series
    max_dd, max_dd_pct = calculate_max_drawdown(close)
    # In a strict uptrend the cumulative return only grows, so drawdown is ~0
    assert max_dd >= -1e-9
    assert max_dd_pct >= -1e-7


def test_max_drawdown_known_dip():
    """50 → 100 → 50: peak-to-trough drawdown is exactly -50%."""
    close = pd.Series([50.0, 100.0, 50.0])
    max_dd, max_dd_pct = calculate_max_drawdown(close)
    assert max_dd == pytest.approx(-0.5, abs=1e-9)
    assert max_dd_pct == pytest.approx(-50.0, abs=1e-7)


def test_calmar_handles_zero_drawdown():
    returns = pd.Series([0.001] * 100)
    assert calculate_calmar_ratio(returns, max_drawdown=0.0) == 0.0


def test_aroon_bounds(trending_series):
    high, low, _ = trending_series
    aroon_up, aroon_down = calculate_aroon(high, low, period=14)
    assert 0.0 <= aroon_up <= 100.0
    assert 0.0 <= aroon_down <= 100.0
