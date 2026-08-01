"""fixture-shop - a tiny discount engine. Golden-scenario fixture, not a real app."""


def apply_discount(price: float, pct: float) -> float:
    """Discounted price. Contract: the result is never negative.

    KNOWN BUG (the scenario's target): pct is not clamped, so pct > 100
    returns a negative price. The slice PLAN (.gravity/demo/PLAN.fix.md)
    states this as a currently-false scenario; the fix must clamp pct to
    [0, 100] AND leave the regression test behind.
    """
    return price * (1 - pct / 100)
