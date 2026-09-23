"""Descriptive risk metrics for a portfolio-value series; standard library only."""
import argparse
import csv
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path


def analyze(values: list[float], periods_per_year: int = 252) -> dict:
    """Assumes equally spaced observations and no external cash flows."""
    if type(periods_per_year) is not int or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    if len(values) < 3:
        raise ValueError("at least three observations are required")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError("values must be finite positive numbers")
    returns = [current / previous - 1 for previous, current in zip(values, values[1:])]
    if any(not math.isfinite(value) for value in returns):
        raise ValueError("returns exceed supported numeric range")
    peak, drawdown = values[0], 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = min(drawdown, value / peak - 1)
    ordered = sorted(returns)
    # Historical nearest-rank 5th percentile, converted to a non-negative loss.
    percentile = ordered[max(0, math.ceil(0.05 * len(ordered)) - 1)]
    result = {
        "observations": len(values),
        "periods_per_year": periods_per_year,
        "total_return": values[-1] / values[0] - 1,
        "mean_period_return": statistics.mean(returns),
        "annualized_volatility": statistics.stdev(returns) * math.sqrt(periods_per_year),
        "max_drawdown": drawdown,
        "historical_var_95": max(0.0, -percentile),
    }
    if any(not math.isfinite(value) for value in result.values()):
        raise ValueError("metrics exceed supported numeric range")
    return result


def load_values(path: Path) -> list[float]:
    values = []
    previous = None
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["date", "value"]:
            raise ValueError("CSV header must be exactly date,value")
        for line_no, row in enumerate(reader, 2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("wrong number of fields")
                day = date.fromisoformat(row["date"])
                if previous is not None and day <= previous:
                    raise ValueError("dates must be strictly increasing")
                values.append(float(row["value"]))
                previous = day
            except (ValueError, TypeError) as error:
                raise ValueError(f"record {line_no}: {error}") from error
    return values


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--periods-per-year", type=int, default=252)
    args = parser.parse_args(argv)
    try:
        result = analyze(load_values(args.input), args.periods_per_year)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, UnicodeError, ValueError, OverflowError, csv.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
