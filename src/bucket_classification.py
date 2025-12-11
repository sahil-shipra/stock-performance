import pandas as pd
import numpy as np


def bucket_classification(monthly_returns: pd.DataFrame, return_col: str, bucket_size: float = 2.0):
    """
    Classifies monthly returns into buckets.

    Parameters:
    monthly_returns : pd.DataFrame
        DataFrame containing at least the monthly return column.
    return_col : str
        Name of the column in the DataFrame containing monthly returns (as float, e.g., 5.14).
    bucket_size : float
        Size of each bucket in percent (default is 2%).

    Returns:
    pd.DataFrame
        Table with bucket range, count, percentage, and returns in each bucket.
    """
    # Work on a copy to avoid mutating caller's DataFrame
    monthly_returns = monthly_returns.copy()

    # Extract numeric returns even if they arrive as strings with percent signs
    returns_series = monthly_returns[return_col]
    if returns_series.dtype == object:
        cleaned = (
            returns_series.astype(str)
            .str.replace('%', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.strip()
        )
        returns = pd.to_numeric(cleaned, errors='coerce')
    else:
        returns = returns_series.astype(float)

    monthly_returns[return_col] = returns

    # Determine bucket edges
    min_return = np.floor(returns.min() / bucket_size) * bucket_size
    max_return = np.ceil(returns.max() / bucket_size) * bucket_size
    bins = np.arange(min_return, max_return + bucket_size, bucket_size)

    # Labels for the buckets
    labels = []
    for i in range(len(bins)-1):
        labels.append(f"{bins[i]:.2f}% to {bins[i+1]:.2f}%")

    # Categorize returns into buckets
    monthly_returns['Bucket'] = pd.cut(
        returns, bins=bins, labels=labels, right=False)

    # Group by bucket and summarize
    bucket_summary = monthly_returns.groupby('Bucket', observed=True)[return_col].agg(
        Count='count',
        Returns_in_Bucket=lambda x: ', '.join([f"{v:.2f}%" for v in x])
    ).reset_index()

    # Calculate percentage
    total = len(monthly_returns)
    bucket_summary['Percentage'] = (
        bucket_summary['Count'] / total * 100).round(2).astype(str) + '%'

    return bucket_summary
