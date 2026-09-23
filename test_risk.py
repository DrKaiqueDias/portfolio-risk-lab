import math
import tempfile
import unittest
from pathlib import Path
from risk import analyze, load_values


class RiskTests(unittest.TestCase):
    def test_known_returns(self):
        report = analyze([100.0, 110.0, 99.0])
        self.assertAlmostEqual(report["total_return"], -0.01)
        self.assertAlmostEqual(report["max_drawdown"], -0.1)
        self.assertAlmostEqual(report["historical_var_95"], 0.1)
        self.assertAlmostEqual(report["annualized_volatility"], math.sqrt(0.02 * 252))

    def test_peak_recovery(self):
        report = analyze([100, 80, 120, 90])
        self.assertAlmostEqual(report["max_drawdown"], -0.25)

    def test_constant_series(self):
        report = analyze([100, 100, 100])
        self.assertEqual(report["annualized_volatility"], 0)
        self.assertEqual(report["historical_var_95"], 0)

    def test_all_positive_returns(self):
        self.assertEqual(analyze([100, 110, 121])["historical_var_95"], 0)

    def test_invalid_numbers(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                analyze([100, value, 110])

    def test_invalid_frequency_and_sample(self):
        for frequency in (0, -1, True):
            with self.assertRaises(ValueError):
                analyze([100, 110, 120], frequency)
        with self.assertRaises(ValueError):
            analyze([100, 101])

    def test_bad_csv(self):
        for text in ("date,value\n2026-01-02,100\n2026-01-01,101\n",
                     "date,value\n2026-01-01,100\n2026-01-01,101\n",
                     "date,value\n2026-01-01,100,extra\n",
                     "wrong,value\n2026-01-01,100\n"):
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "series.csv"
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_values(path)

    def test_valid_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "series.csv"
            path.write_text("date,value\n2026-01-01,100\n2026-01-02,102\n2026-01-03,101\n", encoding="utf-8")
            self.assertEqual(load_values(path), [100, 102, 101])


if __name__ == "__main__":
    unittest.main()
