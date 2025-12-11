import yfinance as yf
import pandas as pd


def _get_adj_close(data: pd.DataFrame) -> pd.Series:
    """
    Extract a single Adjusted Close (or Close) price series from a yfinance
    download result, handling both MultiIndex and flat column structures.
    """
    if isinstance(data.columns, pd.MultiIndex):
        series = data["Adj Close"].iloc[:, 0] if isinstance(
            data["Adj Close"], pd.DataFrame) else data["Adj Close"]
    else:
        if "Adj Close" in data.columns:
            series = data["Adj Close"]
        else:
            series = data["Close"]

    if isinstance(series, pd.DataFrame):
        series = series.squeeze()
    return series


def get_sp500_returns(interval="1d"):
    """
    Downloads historical S&P 500 data (^GSPC) from Yahoo Finance
    and returns price history, daily returns, and cumulative returns.

    Parameters
    ----------
    interval : str
        Data interval. Common options: "1d", "1wk", "1mo"

    Returns
    -------
    data : pd.DataFrame
        Raw historical OHLCV price data
    daily_returns : pd.Series
        Daily percentage returns
    cumulative_returns : pd.Series
        Cumulative returns from the start
    """

    # Download full available history
    # Add auto_adjust=True to simplify column structure
    data = yf.download("^GSPC", period="max",
                       interval=interval, auto_adjust=False)

    if data.empty:
        raise ValueError("No data downloaded. Check internet or yfinance.")

    adj_close = _get_adj_close(data)

    # Daily returns
    daily_returns = adj_close.pct_change()

    # Cumulative returns (growth of $1)
    cumulative_returns = (1 + daily_returns).cumprod()

    return data, daily_returns, cumulative_returns


def get_sp500_monthly_returns(start=None, end=None, decimals=2):
    """
    Convenience wrapper to return month-over-month percentage returns
    for the S&P 500 between the provided dates.

    Returns
    -------
    formatted : dict
        Keys like 'Jan-16', values rounded percentage returns.
    monthly_returns : pd.Series
        Unrounded monthly percentage returns.
    """
    data, _, _ = get_sp500_returns(interval="1mo")
    adj_close = _get_adj_close(data)

    monthly_returns = adj_close.loc[start:end].pct_change().dropna() * 100
    formatted = {dt.strftime("%b-%y"): round(val, decimals)
                 for dt, val in monthly_returns.items()}

    return formatted, monthly_returns


def get_sp500_quarterly_returns(start=None, end=None, decimals=2):
    """
    Convenience wrapper to return quarter-over-quarter percentage returns
    for the S&P 500 between the provided dates.

    Parameters
    ----------
    start : str or pd.Timestamp, optional
        Start date for the data (inclusive).
    end : str or pd.Timestamp, optional
        End date for the data (inclusive).
    decimals : int, default=2
        Number of decimal places to round the returns.

    Returns
    -------
    formatted : dict
        Keys like 'Q1 2016', values rounded quarterly percentage returns.
    quarterly_returns : pd.Series
        Unrounded quarterly percentage returns.
    """
    # Get the raw monthly data
    data, _, _ = get_sp500_returns(interval="1mo")
    adj_close = _get_adj_close(data)

    # Filter by date
    adj_close = adj_close.loc[start:end]

    # Resample to quarterly frequency and calculate returns
    quarterly_close = adj_close.resample('QE').last()
    quarterly_returns = quarterly_close.pct_change().dropna() * 100

    # Format the keys like 'Q1-16'
    formatted = {
        f"Q{((dt.month-1)//3)+1} {dt.year}": round(val, decimals)
        for dt, val in quarterly_returns.items()
    }

    return formatted, quarterly_returns


def get_sp500_return_for_period(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
    """
    Calculate total S&P 500 return for a specific date period.

    Parameters:
    -----------
    start_date : pd.Timestamp
        Start date of the period (will use first trading day on or after this date)
    end_date : pd.Timestamp
        End date of the period (will use last trading day on or before this date)

    Returns:
    --------
    float
        Total return percentage for the period
    """
    # Get daily S&P 500 data
    data, _, _ = get_sp500_returns(interval="1d")
    adj_close = _get_adj_close(data)

    # Find the actual trading dates closest to our requested dates
    # For start: use first trading day on or after start_date
    # For end: use last trading day on or before end_date
    available_dates = adj_close.index

    # Get dates in the range
    period_data = adj_close.loc[start_date:end_date]

    if len(period_data) == 0:
        # Try to get closest dates if exact range has no data
        start_price = adj_close.loc[:start_date].iloc[-1] if len(
            adj_close.loc[:start_date]) > 0 else None
        end_price = adj_close.loc[:end_date].iloc[-1] if len(
            adj_close.loc[:end_date]) > 0 else None

        if start_price is None or end_price is None:
            return None

        period_return = ((end_price / start_price) - 1) * 100
        return period_return

    # Get first and last prices in the period
    start_price = period_data.iloc[0]
    end_price = period_data.iloc[-1]

    # Calculate period return
    if start_price == 0:
        return None

    period_return = ((end_price / start_price) - 1) * 100
    return period_return
