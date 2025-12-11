from pandas import DataFrame
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.bucket_classification import bucket_classification
from src.utils.export_csv import export_csv
from src.utils.get_sp500_returns import get_sp500_quarterly_returns


def quaterly_return_distrubition(df: DataFrame):
    """
    Build a quarterly return distribution with portfolio vs S&P 500 and buckets.
    The function expects the input DataFrame to contain:
    - Entry Date
    - Exit Date
    - P&L Amount
    """
    # Work on a copy to avoid mutating the caller
    df = df.copy()
    df["Entry Date"] = pd.to_datetime(df["Entry Date"])
    df["Exit Date"] = pd.to_datetime(df["Exit Date"])

    # Quarter where P&L is realized
    df["Exit Quarter"] = df["Exit Date"].dt.to_period("Q")

    start_quarter = df["Entry Date"].min().to_period("Q")
    end_quarter = df["Exit Date"].max().to_period("Q")
    all_quarters = pd.period_range(start=start_quarter, end=end_quarter, freq="Q")

    # Aggregate P&L per quarter and ensure full continuity of quarters
    quarterly_pl = (
        df.groupby("Exit Quarter")["P&L Amount"]
        .sum()
        .reindex(all_quarters, fill_value=0)
    )

    initial_portfolio = 100_000
    portfolio_values = initial_portfolio + quarterly_pl.cumsum()

    quarterly_returns = pd.DataFrame(
        {
            "Quarter": [f"Q{p.quarter} {p.year}" for p in all_quarters],
            "Total Portfolio Value": portfolio_values,
        }
    )
    quarterly_returns["Quarterly Return"] = (
        quarterly_returns["Total Portfolio Value"].pct_change().fillna(0) * 100
    )

    # Pull S&P 500 quarterly returns, include one extra quarter for pct_change
    start_date = (start_quarter.start_time - relativedelta(months=3)).strftime(
        "%Y-%m-%d"
    )
    end_date = end_quarter.end_time.strftime("%Y-%m-%d")
    sp500_returns, _ = get_sp500_quarterly_returns(start=start_date, end=end_date)

    quarterly_returns["S&P 500"] = quarterly_returns["Quarter"].map(sp500_returns)
    quarterly_returns["Alpha"] = (
        quarterly_returns["Quarterly Return"] - quarterly_returns["S&P 500"]
    )

    bucket_summary = bucket_classification(
        quarterly_returns, return_col="Quarterly Return", bucket_size=2
    )

    display_df = quarterly_returns.copy()
    display_df["Quarterly Return"] = display_df["Quarterly Return"].apply(
        lambda x: f"{x:.2f}%"
    )
    display_df["S&P 500"] = display_df["S&P 500"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else ""
    )
    display_df["Alpha"] = display_df["Alpha"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else ""
    )
    display_df["Total Portfolio Value"] = display_df["Total Portfolio Value"].apply(
        lambda x: f"${x:,.2f}"
    )

    # Export summaries
    export_csv(df=bucket_summary, filename="quarterly_bucket_summary.csv", timestamp=True)
    export_csv(
        df=display_df,
        filename="quarterly_return_distribution.csv",
        timestamp=True,
    )

    return quarterly_returns, bucket_summary, display_df
