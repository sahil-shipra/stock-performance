import os
import glob
from src.cash_management import cash_management_table
from src.portfolio_value import portfolio_value_table_from_equity
from src.master_analytics import master_analytics
from src.monthly_return_distribution import monthly_return_distribution
from src.quarterly_return_distribution import quarterly_return_distribution
from src.market_crisis_return_distribution import market_crisis_return_distribution
from src.utils.import_csv import import_csv
from src.utils.export_csv import export_file


def process_file(file_path):
    """Process a single Excel file and generate output."""
    print(f"\n{'='*80}")
    print(f"Processing: {file_path}")
    print(f"{'='*80}")

    try:
        df, original_summary, original_equity_curve = import_csv(file_path)
        print(f"\n✅ Data successfully imported!")
        print(f"Dataframe shape: {df.shape[0]} rows, {df.shape[1]} columns")
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error importing file: {e}")
        return False

    # Calculate and display the monthly return distribution
    try:
        allTrades = df.copy()
        summary = master_analytics(df)
        monthly_return, monthly_return_bucket_summary = monthly_return_distribution(
            df=original_equity_curve)
        quarterly_return, quarterly_return_bucket_summary = quarterly_return_distribution(
            df=original_equity_curve)
        market_crisis_return = market_crisis_return_distribution(
            df=original_equity_curve)

        portfolio_value = portfolio_value_table_from_equity(
            df=original_equity_curve)
        cash_management = cash_management_table(df=original_equity_curve)
        return
        # Create sheets dictionary with proper order
        sheets = {
            "All Trades": allTrades,
        }

        # Add original summary worksheet if it exists (position 2)
        if original_summary is not None:
            sheets["Summary"] = original_summary

        # Add original equity curve worksheet if it exists (position 3)
        if original_equity_curve is not None:
            sheets["Equity Curve"] = original_equity_curve

        # Add remaining sheets
        sheets.update({
            "Monthly Return": monthly_return,
            "Monthly Return Bucket Summary": monthly_return_bucket_summary,
            "Quarterly Return": quarterly_return,
            "Quarterly Return Bucket Summary": quarterly_return_bucket_summary,
            "Market Crisis Return": market_crisis_return,
            "Master Analytics": summary,
            "Portfolio Value": portfolio_value,
            "Cash Management": cash_management,
        })

        # Generate output filename by appending _output before extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{base_name}_output.xlsx"

        export_file(sheets,
                    filename=output_filename,
                    timestamp=False)

        return True

    except Exception as e:
        print(f"\n❌ Error calculating : {e}")
        return False


def main():
    """Main function to process all Excel files in current directory."""
    # Get all Excel files in current directory
    excel_files = glob.glob("*.xlsx")

    if not excel_files:
        print("\n❌ No Excel files found in current directory!")
        exit(1)

    print(f"\n📊 Found {len(excel_files)} Excel file(s) to process")

    # Track results
    successful = 0
    failed = 0

    for file_path in excel_files:
        # Skip already processed output files
        if file_path.endswith("_output.xlsx"):
            print(f"\n⏭️  Skipping output file: {file_path}")
            continue

        if process_file(file_path):
            successful += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"Processing Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
