from pandas import DataFrame
import pandas as pd
from datetime import datetime
import numpy as np
import os
from src.utils.get_sp500_returns import (
    get_sp500_monthly_returns,
)
from src.utils.export_csv import export_csv
from dateutil.relativedelta import relativedelta

from src.bucket_classification import bucket_classification


def monthly_return_distribution(df: DataFrame):
    df['Entry Date'] = pd.to_datetime(df['Entry Date'])

    df['Exit Date'] = pd.to_datetime(df['Exit Date'])

    # Create a month column for exit dates (when P&L is realized)
    df['Exit Month'] = df['Exit Date'].dt.to_period('M')

    start_date = df['Entry Date'].min().to_period('M').to_timestamp()
    end_date = df['Exit Date'].max().to_period('M').to_timestamp()
    all_months = pd.period_range(start=start_date, end=end_date, freq='M')

    # Calculate monthly P&L indexed by month
    monthly_pl = (
        df.groupby('Exit Month')['P&L Amount']
        .sum()
        .reindex(all_months, fill_value=0)
    )

    # Starting portfolio value
    initial_portfolio = 100000

    # Cumulative portfolio values without explicit loops
    portfolio_values = initial_portfolio + monthly_pl.cumsum()

    # Monthly returns with vectorized pct_change
    monthly_returns = pd.DataFrame({
        'Month': all_months.strftime('%b-%y'),
        'Total Portfolio Value': portfolio_values,
    })
    monthly_returns['Monthly Return'] = (
        monthly_returns['Total Portfolio Value']
        .pct_change()
        .fillna(0)
        * 100
    )

    one_month_ago = start_date - relativedelta(months=1)
    sp500_returns, _ = get_sp500_monthly_returns(
        start=one_month_ago.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
    )

    # Add S&P 500 returns
    monthly_returns['S&P 500'] = monthly_returns['Month'].map(sp500_returns)

    # Calculate Alpha (Portfolio Return - S&P 500 Return)
    monthly_returns['Alpha'] = monthly_returns['Monthly Return'] - \
        monthly_returns['S&P 500']

    bucket_summary = bucket_classification(
        monthly_returns, return_col='Monthly Return', bucket_size=2)

    # Create a formatted copy for display/export
    display_df = monthly_returns.copy()
    display_df['Monthly Return'] = display_df['Monthly Return'].apply(
        lambda x: f"{x:.2f}%")
    display_df['S&P 500'] = display_df['S&P 500'].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    display_df['Alpha'] = display_df['Alpha'].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    display_df['Total Portfolio Value'] = display_df['Total Portfolio Value'].apply(
        lambda x: f"${x:,.2f}"
    )

    # Save to CSV
    export_csv(
        df=bucket_summary,
        filename="monthly_bucket_summary.csv",
        timestamp=True
    )

    export_csv(
        df=display_df,
        filename="monthly_return_distribution.csv",
        timestamp=True
    )
