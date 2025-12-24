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


def calculate_portfolio_return_for_period(equity_df, period_start, period_end, initial_portfolio):
    """
    Calculate portfolio return for a specific time period.

    Args:
        equity_df: DataFrame with date and equity columns
        period_start: Start date of the period
        period_end: End date of the period
        initial_portfolio: Initial portfolio value (for reference)

    Returns:
        Return percentage for the period
    """
    # Convert to datetime if needed
    period_start = pd.to_datetime(period_start)
    period_end = pd.to_datetime(period_end)

    # Filter equity curve for the period
    period_df = equity_df[
        (equity_df["date"] >= period_start) &
        (equity_df["date"] <= period_end)
    ]

    if len(period_df) == 0:
        return None

    # Get start and end equity values
    start_equity = period_df.iloc[0]["equity"]
    end_equity = period_df.iloc[-1]["equity"]

    # Calculate return percentage
    if start_equity == 0:
        return None

    return ((end_equity - start_equity) / start_equity) * 100


def market_crisis_return_distribution(df: DataFrame):
    """
    Calculate portfolio and S&P 500 returns for each market crisis event period.
    Expects the input DataFrame to contain:
    - date
    - equity
    - cash
    - positions_value
    - num_positions
    """
    # Work on a copy to avoid mutating the caller
    equity_df = df.copy()
    equity_df["date"] = pd.to_datetime(equity_df["date"])
    equity_df = equity_df.sort_values("date")

    # Get market crisis events
    crisis_df = get_market_crisis_events()

    # Get initial portfolio value (first equity value)
    initial_portfolio = equity_df.iloc[0]["equity"]

    # Calculate returns for each event period
    portfolio_returns = []
    sp500_returns = []

    for _, event_row in crisis_df.iterrows():
        period_start = event_row["Period Start"]
        period_end = event_row["Period End"]

        # Calculate portfolio return for this period
        portfolio_return = calculate_portfolio_return_for_period(
            equity_df, period_start, period_end, initial_portfolio
        )
        portfolio_returns.append(portfolio_return)

        # Calculate S&P 500 return for this period
        try:
            sp500_return = get_sp500_return_for_period(
                period_start, period_end
            )
            sp500_returns.append(sp500_return)
        except Exception as e:
            # If data is not available, set to None
            sp500_returns.append(None)
            print(
                f"Warning: Could not calculate S&P 500 return for {event_row['Event']}: {e}"
            )

    # Add calculated returns to the DataFrame
    crisis_df["Portfolio"] = portfolio_returns
    crisis_df["S&P 500"] = sp500_returns

    # Calculate alpha (handle NaN values)
    crisis_df["Alpha"] = crisis_df.apply(
        lambda row: row["Portfolio"] - row["S&P 500"]
        if pd.notna(row["Portfolio"]) and pd.notna(row["S&P 500"])
        else None,
        axis=1
    )

    # Format dates as "Mon-YY"
    crisis_df["Period Start"] = pd.to_datetime(
        crisis_df["Period Start"]).dt.strftime("%b-%y")
    crisis_df["Period End"] = pd.to_datetime(
        crisis_df["Period End"]).dt.strftime("%b-%y")

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

    # Convert Months to int, handling any NaN values
    if "Months" in display_df.columns:
        display_df["Months"] = display_df["Months"].fillna(0).astype(int)

    # Reorder columns to match desired output
    display_df = display_df[[
        "Event",
        "Period Start",
        "Period End",
        "Months",
        "Portfolio",
        "S&P 500",
        "Alpha"
    ]]

    # Formatted for the API to send as JSON records.
    row_data = pd.DataFrame({
        "event": crisis_df['Event'],
        "periodStart": crisis_df['Period Start'],
        "periodEnd": crisis_df['Period End'],
        "months": crisis_df['Months'],
        "portfolio_return": crisis_df['Portfolio'],
        "sP_500": crisis_df['S&P 500'],
        "alpha": crisis_df['Alpha'],
    }).fillna(0).to_dict(orient="records")

    return display_df, row_data
