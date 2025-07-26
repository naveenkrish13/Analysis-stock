#!/usr/bin/env python3
"""Compute best entry and exit times from intraday CSV data."""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import time
import argparse


def load_data(folder: Path) -> pd.DataFrame:
    """Load all csv files in folder and return concatenated DataFrame."""
    frames = []
    for csv_file in folder.glob('*.csv'):
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Failed to read {csv_file}: {e}")
            continue
        if 'datetime_ist' not in df.columns or 'close' not in df.columns:
            print(f"Skipping {csv_file}: missing required columns")
            continue
        df['datetime'] = pd.to_datetime(df['datetime_ist'], format='%d-%m-%Y %H:%M')
        df.set_index('datetime', inplace=True)
        frames.append(df[['close']])
    if not frames:
        raise ValueError('No valid CSV files found in folder')
    data = pd.concat(frames).sort_index()
    return data


def find_best_trade_for_day(day_df: pd.DataFrame):
    """Return best trade dict for given day's DataFrame."""
    day_df = day_df.between_time('09:45', '15:30')
    if day_df.empty:
        return None
    prices = day_df['close']
    times = list(prices.index)
    best = None
    for i in range(len(times) - 1):
        entry_time = times[i]
        entry_price = prices.iloc[i]
        future_prices = prices.iloc[i + 1:]
        if future_prices.empty:
            continue
        exit_idx = future_prices.idxmax()
        profit = future_prices.loc[exit_idx] - entry_price
        if best is None or profit > best['profit']:
            best = {
                'date': entry_time.date(),
                'entry_time': entry_time.time(),
                'exit_time': exit_idx.time(),
                'profit': float(profit)
            }
    return best


def compute_metrics(trades):
    """Compute performance metrics for list of trades."""
    profits = np.array([t['profit'] for t in trades])
    total = len(profits)
    wins = profits[profits > 0]
    losses = profits[profits <= 0]
    win_rate = len(wins) / total * 100 if total else 0
    avg_profit = wins.mean() if len(wins) else 0
    avg_loss = losses.mean() if len(losses) else 0
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) else float('inf')
    sharpe = (profits.mean() / profits.std() * np.sqrt(total)) if profits.std() else float('inf')
    return {
        'Total Trades': total,
        'Win Rate (%)': win_rate,
        'Average Profit per Winning Trade': avg_profit,
        'Average Loss per Losing Trade': avg_loss,
        'Profit Factor': profit_factor,
        'Sharpe Ratio': sharpe,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find best entry/exit times in intraday data')
    parser.add_argument('data_folder', type=Path, help='Folder containing csv files')
    args = parser.parse_args()

    data = load_data(args.data_folder)

    trades = []
    for day, day_df in data.groupby(data.index.date):
        best_trade = find_best_trade_for_day(day_df)
        if best_trade:
            trades.append(best_trade)

    if not trades:
        print('No trades found')
        exit(0)

    metrics = compute_metrics(trades)
    best_overall = max(trades, key=lambda x: x['profit'])

    print('Best trade overall:')
    print(best_overall)
    print('\nPerformance metrics across all days:')
    for k, v in metrics.items():
        print(f"{k}: {v}")
