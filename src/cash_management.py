import pandas as pd
import numpy as np


def cash_management_table(df):
    """
    Build a month/year pivot showing the average available cash.
    The input dataframe must include:
      - Entry Date
      - Exit Date
      - Available Capital After Trade (cash after each trade)
      - Total Portfolio Value (used as a fallback starting cash)
    """
    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        required_cols = {
            "Entry Date",
            "Exit Date",
            "Available Capital After Trade",
            "Total Portfolio Value"
        }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = df.copy()

        # --- Date handling ---
        df["Entry Date"] = pd.to_datetime(df["Entry Date"])
        df["Exit Date"] = pd.to_datetime(df["Exit Date"])

        # --- Create daily date range covering the full trading horizon ---
        start_date = df["Entry Date"].min().normalize()
        end_date = df["Exit Date"].max().normalize()
        all_days = pd.date_range(start_date, end_date, freq="D")

        # --- Daily cash curve ---
        # Use the last cash reading for each exit date and forward-fill so
        # every calendar day has a cash balance.
        daily_cash = (
            df.sort_values("Exit Date")
            .groupby("Exit Date")["Available Capital After Trade"]
            .last()
            .reindex(all_days)
        )

        # Fallback to initial portfolio value when no cash value is present.
        initial_cash = df.iloc[0].get("Available Capital After Trade", np.nan)
        if pd.isna(initial_cash):
            initial_cash = df.iloc[0]["Total Portfolio Value"]

        daily_cash = daily_cash.ffill().fillna(initial_cash)

        cash_df = pd.DataFrame({
            "Date": all_days,
            "Cash": daily_cash.values
        })

        cash_df["Year"] = cash_df["Date"].dt.year
        cash_df["Month"] = cash_df["Date"].dt.month

        # --- Pivot: Average cash by Month x Year ---
        pivot = pd.pivot_table(
            cash_df,
            values="Cash",
            index="Month",
            columns="Year",
            aggfunc="mean"
        )

        # Ensure all 12 months are shown even if empty
        pivot = pivot.reindex(index=range(1, 13))

        cp = pivot.copy()
        # --- Add Grand Total Column (Row-wise Average) ---
        cp = cp.fillna(0).round(2)
        pivot["Grand Total"] = cp.sum(axis=1)
        pivot["Average"] = cp.mean(axis=1)

        # --- Add Grand Total Row ---
        grand_row = cp.sum(axis=0).to_frame().T
        grand_row["Grand Total"] = pivot["Grand Total"].sum()
        grand_row["Average"] = pivot["Average"].sum()
        grand_row.index = ["Grand Total"]

        # --- Add Average Row ---
        avg_row = cp.mean(axis=0).to_frame().T
        avg_row["Grand Total"] = pivot["Grand Total"].mean()
        avg_row["Average"] = pivot["Average"].mean()
        avg_row.index = ["Average"]

        pivot = pd.concat([pivot, grand_row, avg_row])

        # --- Formatting (optional, Excel-like) ---
        pivot = pivot.fillna(0).round(0).astype(int).astype(str)

        # --- Make Month/total the first column instead of an index ---
        pivot = pivot.reset_index().rename(columns={"index": "Month"})

        return pivot
    except Exception as e:
        raise RuntimeError(f"Error calculating cash management table: {e}")
