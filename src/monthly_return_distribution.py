from pandas import DataFrame
import pandas as pd
from src.utils.get_sp500_returns import (
    get_sp500_monthly_returns,
)
from src.bucket_classification import bucket_classification


def monthly_return_distribution(df: DataFrame):
    df = df.copy()
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by date
    df = df.sort_values('date')

    # Extract year-month for grouping
    df['year_month'] = df['date'].dt.to_period('M')

    # Get the last day of each month
    monthly_data = df.groupby('year_month').last().reset_index()

    # Calculate monthly returns
    monthly_data['monthly_return'] = monthly_data['equity'].pct_change() * 100

    # Calculate running peak
    monthly_data['running_peak'] = monthly_data['equity'].cummax()

    # Calculate drawdown percentage
    monthly_data['drawdown_pct'] = ((monthly_data['equity'] - monthly_data['running_peak']) /
                                    monthly_data['running_peak'] * 100)

    # Calculate available capital percentage
    monthly_data['available_capital_pct'] = (
        monthly_data['cash'] / monthly_data['equity'] * 100)

    # Get S&P 500 returns for the entire date range
    start_date = df['date'].min()
    end_date = df['date'].max()

    sp500_returns, _ = get_sp500_monthly_returns(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
    )

    # Add S&P 500 returns with proper format conversion
    monthly_data['sp500_return'] = monthly_data['year_month'].apply(
        lambda x: sp500_returns.get(x.strftime('%b-%y'))
    )

    # Calculate alpha (portfolio return - benchmark return)
    monthly_data['alpha'] = monthly_data['monthly_return'] - \
        monthly_data['sp500_return'].fillna(0)

    # Format the output
    monthly_returns = pd.DataFrame({
        'Month': monthly_data['year_month'].dt.strftime('%b-%y'),
        'Total Portfolio Value': monthly_data['equity'].apply(lambda x: f'${x:,.2f}'),
        'Running Peak': monthly_data['running_peak'].apply(lambda x: f'{x:,.0f}'),
        'Drawdown %': monthly_data['drawdown_pct'].apply(lambda x: f'{x:.2f}%'),
        'Monthly Return': monthly_data['monthly_return'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '0.00%'),
        'Available Capital': monthly_data['cash'].apply(lambda x: f'${x:,.2f}'),
        'Available Capital %': monthly_data['available_capital_pct'].apply(lambda x: f'{x:.2f}%'),
        'S&P 500': monthly_data['sp500_return'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else 'N/A'),
        'Alpha': monthly_data['alpha'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else 'N/A')
    })

    # Formatted for the API to send as JSON records.
    row_data = pd.DataFrame({
        'date': monthly_data['date'],
        'month': monthly_data['year_month'].dt.strftime('%b-%y'),
        'total_portfolio_value': monthly_data['equity'],
        'running_peak': monthly_data['running_peak'],
        'drawdown_pct': monthly_data['drawdown_pct'],
        'monthly_return': monthly_data['monthly_return'],
        'available_capital': monthly_data['cash'],
        'available_capital_pct': monthly_data['available_capital_pct'],
        'sp500_return': monthly_data['sp500_return'],
        'alpha': monthly_data['alpha']
    }).fillna(0).to_dict(orient="records")

    bucket_summary = bucket_classification(
        monthly_returns, return_col='Monthly Return', bucket_size=2)

    return monthly_returns, bucket_summary, row_data
