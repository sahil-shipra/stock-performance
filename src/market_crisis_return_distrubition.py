from pandas import DataFrame
import pandas as pd
from dateutil.relativedelta import relativedelta
from src.utils.export_csv import export_csv
from src.utils.get_sp500_returns import get_sp500_return_for_period


def get_market_crisis_events() -> DataFrame:
    """Return a DataFrame with major market crisis events and periods."""
    events = [
        ("Brexit Referendum", "2016-06", "2016-06"),
        ("2016 Election", "2016-10", "2016-11"),
        ("Volmageddon", "2018-01", "2018-02"),
        ("Trade War Escalation", "2019-05", "2019-08"),
        ("Repo Crisis", "2019-09", "2019-09"),
        ("COVID Crash", "2020-02", "2020-03"),
        ("COVID Recovery", "2020-06", "2020-06"),
        ("Tech Selloff", "2020-09", "2020-09"),
        ("Inflation Fears", "2021-02", "2021-03"),
        ("Omicron Variant", "2021-11", "2021-12"),
        ("2022 Bear Market", "2022-01", "2022-10"),
        ("Banking Crisis", "2023-03", "2023-03"),
        ("Aug 2023 Sell Off", "2023-08", "2023-08"),
        ("Oct 2023 Spike", "2023-10", "2023-10"),
        ("Mag 7 Correction", "2024-04", "2024-04"),
        ("Japan Carry Unwind", "2024-07", "2024-08"),
        ("Election Volatility", "2024-10", "2024-11")
    ]

    df = pd.DataFrame(events, columns=["Event", "Period Start", "Period End"])
    df["Period Start"] = pd.to_datetime(df["Period Start"])
    df["Period End"] = pd.to_datetime(df["Period End"])

    # Normalize dates: Start to first day of month, End to last day of month
    df["Period Start"] = df["Period Start"].dt.to_period("M").dt.start_time
    df["Period End"] = df["Period End"].dt.to_period("M").dt.end_time

    # Calculate duration in months
    def months_diff(start, end):
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months + 1

    df["Months"] = df.apply(lambda row: months_diff(
        row["Period Start"], row["Period End"]), axis=1)
    return df


def calculate_portfolio_return_for_period(
    trading_df: DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    initial_portfolio: float = 100_000
) -> float:
    """
    Calculate portfolio return for a specific date period.

    Parameters:
    -----------
    trading_df : DataFrame
        DataFrame with Entry Date, Exit Date, and P&L Amount
    start_date : pd.Timestamp
        Start date of the period (portfolio value calculated before this date)
    end_date : pd.Timestamp
        End date of the period (portfolio value calculated at end of this date)
    initial_portfolio : float
        Initial portfolio value

    Returns:
    --------
    float
        Total return percentage for the period
    """
    # Calculate portfolio value at start of period
    # Sum all P&L realized strictly before start_date (exclude start_date itself)
    pl_before_start = trading_df[trading_df["Exit Date"]
                                 < start_date]["P&L Amount"].sum()
    portfolio_start = initial_portfolio + pl_before_start

    # Calculate portfolio value at end of period
    # Sum all P&L realized up to and including end_date
    pl_before_end = trading_df[trading_df["Exit Date"]
                               <= end_date]["P&L Amount"].sum()
    portfolio_end = initial_portfolio + pl_before_end

    # Calculate period return
    if portfolio_start == 0:
        return 0.0

    period_return = ((portfolio_end / portfolio_start) - 1) * 100
    return period_return


def market_crisis_return_distrubition(df: DataFrame):
    """
    Calculate portfolio and S&P 500 returns for each market crisis event period.
    Expects the input DataFrame to contain:
    - Entry Date
    - Exit Date
    - P&L Amount
    """
    trading_df = df.copy()
    trading_df["Entry Date"] = pd.to_datetime(trading_df["Entry Date"])
    trading_df["Exit Date"] = pd.to_datetime(trading_df["Exit Date"])

    # Get market crisis events
    crisis_df = get_market_crisis_events()

    # Calculate returns for each event period
    portfolio_returns = []
    sp500_returns = []

    for _, event_row in crisis_df.iterrows():
        period_start = event_row["Period Start"]
        period_end = event_row["Period End"]

        # Calculate portfolio return for this period
        portfolio_return = calculate_portfolio_return_for_period(
            trading_df, period_start, period_end
        )
        portfolio_returns.append(portfolio_return)

        # Calculate S&P 500 return for this period
        try:
            sp500_return = get_sp500_return_for_period(
                period_start, period_end)
            sp500_returns.append(sp500_return)
        except Exception as e:
            # If data is not available, set to None
            sp500_returns.append(None)
            print(
                f"Warning: Could not calculate S&P 500 return for {event_row['Event']}: {e}")

    # Add calculated returns to the DataFrame
    crisis_df["Portfolio"] = portfolio_returns
    crisis_df["S&P 500"] = sp500_returns
    crisis_df["Alpha"] = crisis_df["Portfolio"] - crisis_df["S&P 500"]

    # Format dates as "Mon-YY"
    crisis_df["Period Start"] = crisis_df["Period Start"].dt.strftime("%b-%y")
    crisis_df["Period End"] = crisis_df["Period End"].dt.strftime("%b-%y")

    # Format returns as percentages with 2 decimal places, or empty string if NaN
    def format_percentage(val):
        if pd.isna(val):
            return ""
        return f"{val:.2f}%"

    # Create display DataFrame for export
    display_df = crisis_df.copy()
    display_df["Portfolio"] = display_df["Portfolio"].apply(format_percentage)
    display_df["S&P 500"] = display_df["S&P 500"].apply(format_percentage)
    display_df["Alpha"] = display_df["Alpha"].apply(format_percentage)

    # Convert Months to int, but keep as is for display (some may be empty in image)
    display_df["Months"] = display_df["Months"].astype(int)

    # Reorder columns to match desired output
    display_df = display_df[["Event", "Period Start",
                             "Period End", "Months", "Portfolio", "S&P 500", "Alpha"]]

    return display_df
