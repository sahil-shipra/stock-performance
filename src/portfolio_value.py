import pandas as pd
import numpy as np


def portfolio_value_table(df):
    df = df.copy()

    # --- Date handling ---
    df["Entry Date"] = pd.to_datetime(df["Entry Date"])
    df["Exit Date"] = pd.to_datetime(df["Exit Date"])

    # --- Initial capital ---
    initial_capital = df.iloc[0]["Total Portfolio Value"]

    # --- Create daily date range ---
    start_date = df["Entry Date"].min()
    end_date = df["Exit Date"].max()
    all_days = pd.date_range(start_date, end_date, freq="D")

    # --- Build daily equity curve ---
    pnl_by_date = (
        df.groupby("Exit Date")["P&L Amount"]
        .sum()
        .reindex(all_days, fill_value=0)
    )

    equity_curve = initial_capital + pnl_by_date.cumsum()

    equity_df = pd.DataFrame({
        "Date": all_days,
        "Portfolio Value": equity_curve.values
    })

    # --- Extract Month & Year ---
    equity_df["Year"] = equity_df["Date"].dt.year
    equity_df["Month"] = equity_df["Date"].dt.month

    # --- Pivot: Average Portfolio Value ---
    pivot = pd.pivot_table(
        equity_df,
        values="Portfolio Value",
        index="Month",
        columns="Year",
        aggfunc="mean"
    )

    # --- Add Grand Total Column (Row-wise Average) ---
    pivot["Grand Total"] = pivot.mean(axis=1)

    # --- Add Grand Total Row (Column-wise Average) ---
    grand_row = pd.DataFrame(
        pivot.mean(axis=0)
    ).T
    grand_row.index = ["Grand Total"]

    pivot = pd.concat([pivot, grand_row])

    # --- Formatting (optional, Excel-like) ---
    pivot = pivot.fillna(0).round(0).astype(int).astype(str)

    # --- Make Month/total the first column instead of an index ---
    pivot = pivot.reset_index().rename(columns={"index": "Month"})

    return pivot
