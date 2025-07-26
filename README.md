# Stock Intraday Analysis

This repository contains utilities for working with intraday stock data. The
`intraday_best_trade.py` script scans CSV files with 1‑minute data and
calculates the most profitable entry and exit times for each day. It also
summarizes the trading performance across all days with common metrics.

## Usage

1. Place your CSV files (each containing columns `close` and `datetime_ist`) in a
   folder, e.g. `data/`.
2. Install the required Python packages:

```bash
pip install pandas numpy
```

3. Run the analysis:

```bash
python3 intraday_best_trade.py data/
```

The script will output the best trade discovered and performance metrics such as
win rate, average profit/loss, profit factor and Sharpe ratio.
