import os
import pandas as pd


def import_csv(file_path):
    """
    Import trading data from Excel (.xlsx) or CSV (.csv) file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.xlsx':
        df = pd.read_excel(file_path)
        print(f"✓ Successfully imported Excel file: {file_path}")
    elif file_extension == '.csv':
        df = pd.read_csv(file_path)
        print(f"✓ Successfully imported CSV file: {file_path}")
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. Please use .xlsx or .csv")

    return df
