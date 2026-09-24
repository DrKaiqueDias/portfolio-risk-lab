# Portfolio Risk Lab

[![Python checks](https://github.com/DrKaiqueDias/portfolio-risk-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/DrKaiqueDias/portfolio-risk-lab/actions)

A Python project that connects my interest in coding with my background in financial markets. It reads a series of portfolio values and calculates returns, volatility, maximum drawdown and historical VaR.

The formulas and assumptions are documented below so the results can be checked directly.

## Try it

```sh
python risk.py examples/portfolio.csv
python risk.py examples/portfolio.csv --periods-per-year 252
```

Input must use exactly `date,value`, with ISO dates in strictly increasing order and at least three finite, positive values. Output is JSON. Returns and drawdowns are decimal fractions: `0.04` means 4%.

## Calculations

- Period return: current value / previous value − 1.
- Total return: final value / initial value − 1.
- Annualized volatility: sample standard deviation of period returns × square root of periods per year.
- Maximum drawdown: minimum of value / running peak − 1; zero or negative.
- Historical 95% VaR: non-negative loss corresponding to the nearest-rank 5th percentile of observed returns.

The example starts at 10,000 and ends at 10,400: **total return = 4%**. See [expected output](examples/report.json).

## Assumptions and limits

Observations must represent equally spaced periods; dates are checked for ordering, not market-calendar completeness. The default 252 assumes daily trading observations. Values must already account for splits and distributions and must exclude external deposits/withdrawals; otherwise calculated returns are misleading. Tiny samples, including the demo, cannot establish reliable tail risk. No forecasting, investment recommendation or live market connection is provided.

Exit codes: **0** success; **2** invalid input. Computation uses O(n) memory and O(n log n) time because the historical quantile sorts returns.

## Development

Requires **Python 3.11+**. Uses only the standard library; no installation or API keys.

```sh
python -m unittest discover -v
```

Tests run on Python 3.11, 3.12 and 3.13 through GitHub Actions. The sample data is synthetic.

## Design choices

Calculations are separate from CSV parsing and command-line handling. The code uses the standard library so the formulas are easy to inspect without a data-analysis framework.

## License

MIT. Maintained by [Kaique Dias](https://github.com/DrKaiqueDias).

