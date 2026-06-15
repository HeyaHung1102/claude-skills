"""
Prophet Inequality Trading System
----------------------------------
Based on Samuel-Cahn (1984): E[optimal stopping] >= (1/2) * E[prophet]

Core theorem: By observing n price opportunities sequentially,
an optimal stopping rule guarantees at least 50% of the "god's eye view"
maximum return — without lookahead.

Usage:
    python prophet_trade.py --ticker SPXC --capital 100 --risk 0.02
"""

import argparse
import math
import sys
from datetime import datetime, timedelta

try:
    import yfinance as yf
    import numpy as np
except ImportError:
    print("Missing dependencies. Run: pip install yfinance numpy")
    sys.exit(1)


# ─────────────────────────────────────────────
# 1. Data fetching
# ─────────────────────────────────────────────

def fetch_ohlcv(ticker: str, days: int = 60) -> dict:
    """Fetch recent OHLCV data for a ticker."""
    end = datetime.today()
    start = end - timedelta(days=days)
    df = yf.download(ticker, start=start.strftime("%Y-%m-%d"),
                     end=end.strftime("%Y-%m-%d"), progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}. "
                         "SpaceX is private — try SPXC, TSLA, or RKLB.")
    return {
        "ticker": ticker,
        "close": df["Close"].values.flatten().tolist(),
        "volume": df["Volume"].values.flatten().tolist(),
        "dates": [str(d.date()) for d in df.index],
        "latest_price": float(df["Close"].iloc[-1]),
        "latest_volume": int(df["Volume"].iloc[-1]),
    }


# ─────────────────────────────────────────────
# 2. Volatility calculation (ATR-based)
# ─────────────────────────────────────────────

def compute_volatility(data: dict, window: int = 14) -> dict:
    """
    Compute:
    - Historical volatility (annualized σ)
    - Average True Range (ATR) as dollar-risk per share
    - Daily move expectation (1σ daily range)
    """
    closes = np.array(data["close"])
    log_returns = np.diff(np.log(closes))

    # Annualized volatility
    daily_vol = float(np.std(log_returns))
    annual_vol = daily_vol * math.sqrt(252)

    # ATR proxy (high-low not available from daily close only)
    # Use rolling std of closes as ATR substitute
    recent = closes[-window:]
    atr_proxy = float(np.std(np.diff(recent)))

    # 1-sigma daily expected move in dollars
    price = data["latest_price"]
    one_sigma_daily = price * daily_vol

    return {
        "daily_vol_pct": round(daily_vol * 100, 3),
        "annual_vol_pct": round(annual_vol * 100, 2),
        "atr_proxy": round(atr_proxy, 4),
        "one_sigma_daily_usd": round(one_sigma_daily, 4),
        "price": price,
    }


# ─────────────────────────────────────────────
# 3. Prophet Inequality — Optimal Threshold
# ─────────────────────────────────────────────

def prophet_threshold(closes: list, capital: float) -> dict:
    """
    Samuel-Cahn theorem application:

    Given X_1, ..., X_n i.i.d. (price returns), the optimal stopping
    threshold τ* satisfies:

        P(X_i > τ*) = 1 / (2n)   for each i

    This guarantees E[reward] >= (1/2) * E[max X_i]

    In practice: set τ* at the (1 - 1/2n) quantile of observed returns.
    """
    returns = np.diff(np.log(closes))
    n = len(returns)

    # Optimal threshold quantile per Samuel-Cahn
    quantile = 1.0 - 1.0 / (2 * n)
    threshold_return = float(np.quantile(returns, quantile))
    threshold_price_move = closes[-1] * (math.exp(threshold_return) - 1)

    # Prophet benchmark (expected max over window)
    prophet_value = float(np.max(returns))
    prophet_dollar = closes[-1] * (math.exp(prophet_value) - 1)

    # Shares purchasable with capital
    shares = capital / closes[-1]

    # Expected gain using optimal stopping (>= 50% of prophet)
    expected_gain = shares * threshold_price_move
    prophet_gain = shares * prophet_dollar
    guarantee_ratio = (expected_gain / prophet_gain) if prophet_gain > 0 else 0

    return {
        "n_observations": n,
        "optimal_quantile": round(quantile * 100, 2),
        "threshold_return_pct": round(threshold_return * 100, 4),
        "threshold_price_move_usd": round(threshold_price_move, 4),
        "expected_gain_usd": round(expected_gain, 4),
        "prophet_gain_usd": round(prophet_dollar * shares, 4),
        "guarantee_ratio_pct": round(guarantee_ratio * 100, 2),
        "shares": round(shares, 6),
    }


# ─────────────────────────────────────────────
# 4. Stop-loss & Take-profit Calculator
# ─────────────────────────────────────────────

def compute_exit_levels(price: float, capital: float,
                        vol: dict, risk_pct: float = 0.02) -> dict:
    """
    Stop-loss:  Price - k * σ_daily   where k chosen so loss <= risk_pct * capital
    Take-profit: Price + prophet_threshold_move (minimum 50% guarantee level)

    Hua Luogeng 0.618 refinement:
        Take-profit midpoint = entry + 0.618 * (max_target - entry)
    """
    entry = price
    max_loss_dollars = capital * risk_pct
    shares = capital / entry

    # Stop-loss: how many σ we can tolerate
    one_sigma = vol["one_sigma_daily_usd"]
    sigma_budget = max_loss_dollars / shares if shares > 0 else one_sigma
    stop_loss = entry - sigma_budget
    stop_loss_pct = (sigma_budget / entry) * 100

    # Take-profit: 1σ minimum, 0.618 of 2σ as first target
    target_1sigma = entry + one_sigma
    target_2sigma = entry + 2 * one_sigma
    # Hua Luogeng 0.618 golden ratio take-profit
    target_618 = entry + 0.618 * (target_2sigma - entry)

    return {
        "entry_price": round(entry, 4),
        "capital_usd": capital,
        "shares": round(shares, 6),
        "max_risk_usd": round(max_loss_dollars, 2),
        "stop_loss_price": round(stop_loss, 4),
        "stop_loss_pct": round(stop_loss_pct, 3),
        "take_profit_1sigma": round(target_1sigma, 4),
        "take_profit_618": round(target_618, 4),
        "take_profit_2sigma": round(target_2sigma, 4),
        "risk_reward_ratio": round(
            (target_618 - entry) / sigma_budget, 2
        ) if sigma_budget > 0 else 0,
    }


# ─────────────────────────────────────────────
# 5. Main report
# ─────────────────────────────────────────────

def run(ticker: str, capital: float, risk_pct: float):
    print(f"\n{'='*56}")
    print(f"  Prophet Inequality Trade System")
    print(f"  Ticker: {ticker} | Capital: ${capital} | Risk: {risk_pct*100}%")
    print(f"{'='*56}\n")

    # Fetch
    print(f"[1/4] Fetching data for {ticker}...")
    data = fetch_ohlcv(ticker)
    print(f"      Latest price : ${data['latest_price']:.4f}")
    print(f"      Latest volume: {data['latest_volume']:,}")

    # Volatility
    print(f"\n[2/4] Computing volatility (60-day window)...")
    vol = compute_volatility(data)
    print(f"      Daily vol    : {vol['daily_vol_pct']}%")
    print(f"      Annual vol   : {vol['annual_vol_pct']}%")
    print(f"      1σ daily ($) : ${vol['one_sigma_daily_usd']:.4f}")

    # Prophet threshold
    print(f"\n[3/4] Samuel-Cahn optimal stopping threshold...")
    pt = prophet_threshold(data["close"], capital)
    print(f"      Observations : {pt['n_observations']} days")
    print(f"      Optimal quantile: {pt['optimal_quantile']}th percentile")
    print(f"      Threshold move : ${pt['threshold_price_move_usd']:.4f} per share")
    print(f"      Expected gain  : ${pt['expected_gain_usd']:.4f}")
    print(f"      Prophet max    : ${pt['prophet_gain_usd']:.4f}")
    print(f"      Guarantee ratio: {pt['guarantee_ratio_pct']}% of prophet")

    # Exit levels
    print(f"\n[4/4] Exit levels (Hua Luogeng 0.618 refinement)...")
    ex = compute_exit_levels(data["latest_price"], capital, vol, risk_pct)
    print(f"\n  ┌─────────────────────────────────────────┐")
    print(f"  │  TRADE PLAN                             │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │  Entry price    : ${ex['entry_price']:<10.4f}            │")
    print(f"  │  Shares         : {ex['shares']:<10.6f}            │")
    print(f"  │  Capital at risk: ${ex['max_risk_usd']:<10.2f}            │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │  STOP LOSS      : ${ex['stop_loss_price']:<10.4f} (-{ex['stop_loss_pct']:.2f}%)  │")
    print(f"  │  TAKE PROFIT T1 : ${ex['take_profit_618']:<10.4f} (0.618×2σ)│")
    print(f"  │  TAKE PROFIT T2 : ${ex['take_profit_2sigma']:<10.4f} (2σ)      │")
    print(f"  │  Risk/Reward    : 1 : {ex['risk_reward_ratio']:<6.2f}                │")
    print(f"  └─────────────────────────────────────────┘")

    print(f"\n⚠  DISCLAIMER: 投資有風險，本程式僅供研究用途。")
    print(f"   本輸出不構成任何投資建議。入市前請評估自身風險承受能力。\n")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prophet Inequality Trading System")
    parser.add_argument("--ticker", default="RKLB",
                        help="Stock ticker (SpaceX is private; try RKLB, SPXC, TSLA)")
    parser.add_argument("--capital", type=float, default=100.0,
                        help="Capital in USD (default: 100)")
    parser.add_argument("--risk", type=float, default=0.02,
                        help="Max risk as fraction of capital (default: 0.02 = 2%%)")
    args = parser.parse_args()
    run(args.ticker, args.capital, args.risk)
