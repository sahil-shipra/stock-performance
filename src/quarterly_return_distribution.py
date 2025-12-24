from pandas import DataFrame
import pandas as pd
from src.bucket_classification import bucket_classification
from src.utils.get_sp500_returns import get_sp500_quarterly_returns


def quarterly_return_distribution(df: DataFrame):
    """
    Build a quarterly return distribution with portfolio vs S&P 500 and buckets.
    The function expects the input DataFrame to contain:
    - date
    - equity
    - cash
    - positions_value
    - num_positions
    """
    # Work on a copy to avoid mutating the caller
    df = df.copy()

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by date
    df = df.sort_values('date')

    # Extract year-quarter for grouping
    df['year_quarter'] = df['date'].dt.to_period('Q')

    # Get the last day of each quarter
    quarterly_data = df.groupby('year_quarter').last().reset_index()

    # Calculate quarterly returns
    quarterly_data['quarterly_return'] = quarterly_data['equity'].pct_change() * \
        100

    # Calculate running peak
    quarterly_data['running_peak'] = quarterly_data['equity'].cummax()

    # Calculate drawdown percentage
    quarterly_data['drawdown_pct'] = (
        (quarterly_data['equity'] - quarterly_data['running_peak']) /
        quarterly_data['running_peak'] * 100
    )

    # Calculate available capital percentage
    quarterly_data['available_capital_pct'] = (
        quarterly_data['cash'] / quarterly_data['equity'] * 100
    )

    # Get S&P 500 returns for the entire date range
    start_date = df['date'].min()
    end_date = df['date'].max()

    sp500_returns, _ = get_sp500_quarterly_returns(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
    )

    # Add S&P 500 returns with proper format conversion
    quarterly_data['sp500_return'] = quarterly_data['year_quarter'].apply(
        lambda x: sp500_returns.get(x.strftime("Q%q %Y"))
    )

    # Calculate alpha (portfolio return - benchmark return)
    quarterly_data['alpha'] = (
        quarterly_data['quarterly_return'] -
        quarterly_data['sp500_return'].fillna(0)
    )

    # Format the output
    quarterly_returns = pd.DataFrame({
        'Quarter': quarterly_data['year_quarter'],
        'Total Portfolio Value': quarterly_data['equity'],
        'Running Peak': quarterly_data['running_peak'],
        'Available Capital': quarterly_data['cash'],
        'Available Capital %': quarterly_data['available_capital_pct'],
        'Quarterly Return': quarterly_data['quarterly_return'].fillna(0),
        'S&P 500': quarterly_data['sp500_return'],
        'Alpha': quarterly_data['alpha'],
        'Drawdown %': quarterly_data['drawdown_pct']
    })

    # Pass unformatted data to bucket_classification
    bucket_summary = bucket_classification(
        quarterly_returns, return_col="Quarterly Return", bucket_size=2
    )

    # Create display dataframe with formatted values
    display_df = quarterly_returns.copy()
    display_df["Quarterly Return"] = display_df["Quarterly Return"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%"
    )
    display_df["S&P 500"] = display_df["S&P 500"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
    )
    display_df["Alpha"] = display_df["Alpha"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
    )
    display_df["Total Portfolio Value"] = display_df["Total Portfolio Value"].apply(
        lambda x: f"${x:,.2f}"
    )
    display_df['Available Capital'] = display_df['Available Capital'].apply(
        lambda x: f"${x:,.2f}"
    )
    display_df['Available Capital %'] = display_df['Available Capital %'].apply(
        lambda x: f"{x:.2f}%"
    )
    display_df["Drawdown %"] = display_df["Drawdown %"].apply(
        lambda x: f"{x:.2f}%"
    )
    display_df["Running Peak"] = display_df["Running Peak"].apply(
        lambda x: f"{x:,.0f}"
    )

    # Formatted for the API to send as JSON records.
    row_data = pd.DataFrame({
        'date': quarterly_data['date'],
        'year_quarter': quarterly_data['year_quarter'].dt.strftime("Q%q %Y"),
        'total_portfolio_value': quarterly_data['equity'],
        'running_peak': quarterly_data['running_peak'],
        'drawdown_pct': quarterly_data['drawdown_pct'],
        'quarterly_return': quarterly_data['quarterly_return'],
        'available_capital': quarterly_data['cash'],
        'available_capital_pct': quarterly_data['available_capital_pct'],
        'sp500_return': quarterly_data['sp500_return'],
        'alpha': quarterly_data['alpha']
    }).fillna(0).to_dict(orient="records")

    return display_df, bucket_summary, row_data
