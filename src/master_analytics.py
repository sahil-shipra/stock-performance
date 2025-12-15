import pandas as pd
import numpy as np


def master_analytics(df, portfolio_name="Portfolio"):
    df = df.copy()

    # --- Date handling ---
    df["Entry Date"] = pd.to_datetime(df["Entry Date"])
    df["Exit Date"] = pd.to_datetime(df["Exit Date"])

    # --- Capital ---
    initial_capital = df.iloc[0]["Total Portfolio Value"]
    total_return_dollar = df["P&L Amount"].sum()
    final_capital = initial_capital + total_return_dollar
    total_return_pct = (final_capital / initial_capital - 1) * 100

    # --- Time in Market ---
    start_date = df["Entry Date"].min()
    end_date = df["Exit Date"].max()
    days_in_market = (end_date - start_date).days
    years_in_market = days_in_market / 365.25

    cagr = ((final_capital / initial_capital)
            ** (1 / years_in_market) - 1) * 100

    # --- Trades ---
    total_trades = len(df)
    wins = df[df["P&L Amount"] > 0]
    losses = df[df["P&L Amount"] < 0]

    win_trades = len(wins)
    loss_trades = len(losses)
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    # --- Trade Stats ---
    best_trade = df["P&L %"].max()
    worst_trade = df["P&L %"].min()

    avg_win = wins["P&L Amount"].mean() if win_trades > 0 else 0
    avg_loss = losses["P&L Amount"].mean() if loss_trades > 0 else 0

    payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.nan
    profit_factor = wins["P&L Amount"].sum(
    ) / abs(losses["P&L Amount"].sum()) if loss_trades > 0 else np.nan

    expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

    # --- Equity Curve & Drawdown ---
    equity_curve = initial_capital + df["P&L Amount"].cumsum()
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_dd = drawdown.min() * 100

    calmar_ratio = cagr / abs(max_dd) if max_dd != 0 else np.nan

    # --- Output ---
    summary = pd.DataFrame([{
        "Portfolio Name": portfolio_name,
        "Total Time in Market": f"{years_in_market:.2f} Years",
        "CAGR % (Time in Market)": round(cagr, 2),
        "Total Return %": round(total_return_pct, 2),
        "Initial Capital": round(initial_capital, 2),
        "Total Return $": round(total_return_dollar, 2),
        "Final Capital": round(final_capital, 2),
        "Max DD %": round(max_dd, 2),
        "Total Trades": total_trades,
        "Win Trades": win_trades,
        "Loss Trades": loss_trades,
        "Win Rate %": round(win_rate, 2),
        "Best Trade %": round(best_trade, 2),
        "Worst Trade %": round(worst_trade, 2),
        "Avg Win $": round(avg_win, 2),
        "Avg Loss $": round(avg_loss, 2),
        "Profit Factor": round(profit_factor, 2),
        "Payoff Ratio": round(payoff_ratio, 2),
        "Expectancy $": round(expectancy, 2),
        "Calmar Ratio": round(calmar_ratio, 2),
        "Total Exits": total_trades,
        "Capital Constrain Exits": 0,
        "Signal Based Exits": total_trades
    }])

    return summary
