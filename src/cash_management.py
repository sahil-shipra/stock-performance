import pandas as pd
import numpy as np


def cash_management_table(df):
    """
    Build a Month x Year pivot showing the average daily cash.

    Required columns:
      - date
      - cash
    """
    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        required_cols = {"date", "cash"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = df.copy()

        # --- Date handling ---
        df["date"] = pd.to_datetime(df["date"])

        # --- Extract Year & Month ---
        df["Year"] = df["date"].dt.year
        df["Month"] = df["date"].dt.month

        # --- Pivot: Average Cash by Month x Year ---
        pivot = pd.pivot_table(
            df,
            values="cash",
            index="Month",
            columns="Year",
            aggfunc="mean"
        )

        # Ensure all months appear
        pivot = pivot.reindex(index=range(1, 13))

        cp = pivot.copy()

        # --- Clean & round ---
        cp = cp.fillna(0).round(2)

        # --- Add Grand Total & Average columns ---
        pivot["Grand Total"] = cp.sum(axis=1)
        pivot["Average"] = cp.mean(axis=1)

        # --- Grand Total row ---
        grand_row = cp.sum(axis=0).to_frame().T
        grand_row["Grand Total"] = pivot["Grand Total"].sum()
        grand_row["Average"] = pivot["Average"].sum()
        grand_row.index = ["Grand Total"]

        # --- Average row ---
        avg_row = cp.mean(axis=0).to_frame().T
        avg_row["Grand Total"] = pivot["Grand Total"].mean()
        avg_row["Average"] = pivot["Average"].mean()
        avg_row.index = ["Average"]

        pivot = pd.concat([pivot, grand_row, avg_row])

        # --- Formatting (Excel-like) ---
        pivot = pivot.fillna(0).round(0).astype(int).astype(str)

        # --- Month as column ---
        pivot = pivot.reset_index()
        return pivot

    except Exception as e:
        raise RuntimeError(f"Error calculating cash management table: {e}")
