import os
from datetime import datetime
import pandas as pd


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
        filename = f"{name}_{datetime.now().strftime('%Y_%m_%d-%H%M%S')}{ext}"

    # Full path
    full_path = os.path.join(output_dir, filename)

    # Save the DataFrame
    df.to_csv(full_path, index=False)

    return full_path


def export_file(sheets, filename, output_dir="output", timestamp=False):
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
        filename = f"{name}_{datetime.now().strftime('%Y_%m_%d-%H%M%S')}{ext}"

    # Full path
    full_path = os.path.join(output_dir, filename)

    with pd.ExcelWriter(full_path, engine="xlsxwriter") as writer:

        # Dictionary of sheet names + dataframes

        workbook = writer.book

        # --- HEADER FORMAT (matches your screenshot) ---
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'center',
            'align': 'center',
            'bg_color': '#366092',    # Dark blue header background
            'font_color': 'white',    # White font
            'border': 1
        })

        # Write each sheet
        for sheet_name, df_sheet in sheets.items():

            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]

            # Apply header formatting
            for col_num, col_name in enumerate(df_sheet.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # Apply border + alignment for data rows
            for row in range(1, len(df_sheet) + 1):
                for col in range(len(df_sheet.columns)):
                    worksheet.write(
                        row, col, df_sheet.iloc[row-1, col])

            # Auto column width
            for i, col in enumerate(df_sheet.columns):
                col_width = max(df_sheet[col].astype(
                    str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

    print(f"\n✅ Done! Return distribution calculated!")
    print(f"\n✅ Export completed:", full_path)

    return full_path
