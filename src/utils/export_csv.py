import os
from datetime import datetime


def export_csv(df, filename, output_dir="output", timestamp=False):
    """
    Saves a pandas DataFrame to a CSV file, ensuring the directory exists.

    Parameters:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): Base filename, e.g. 'monthly_returns.csv'.
        output_dir (str): Folder to save into. Default is 'output'.
        timestamp (bool): If True, adds YYYYMMDD-HHMMSS to filename.

    Returns:
        str: Full path to the saved CSV file.
    """
    # Create directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Add timestamp if needed
    if timestamp:
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}"

    # Full path
    full_path = os.path.join(output_dir, filename)

    # Save the DataFrame
    df.to_csv(full_path, index=False)

    return full_path
