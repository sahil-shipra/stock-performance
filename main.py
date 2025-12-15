from src.cash_management import cash_management_table
from src.portfolio_value import portfolio_value_table
from src.master_analytics import master_analytics
from src.monthly_return_distribution import monthly_return_distribution
from src.quarterly_return_distrubition import quarterly_return_distrubition
from src.market_crisis_return_distrubition import market_crisis_return_distrubition
from src.utils.import_csv import import_csv
from src.utils.export_csv import export_file
# ========== FILE IMPORT ==========

# Option 1: Specify the file path directly
FILE_PATH = "trading_data.xlsx"  # Change this to your file name
# Export to one Excel file with multiple sheets
OUTPUT_FILE = "trading_analysis.xlsx"


def main():
    """Main function to import trading data and calculate monthly return distribution."""
    try:
        df = import_csv(FILE_PATH)
        print(f"\n✅ Data successfully imported!")
        print(f"Dataframe shape: {df.shape[0]} rows, {df.shape[1]} columns")
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("Please make sure your file is in the same directory as this script,")
        print("or provide the full path to the file.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error importing file: {e}")
        exit(1)

    # Calculate and display the monthly return distribution
    try:
        allTrades = df.copy()
        summary = master_analytics(df)
        monthly_return, monthly_return_bucket_summary = monthly_return_distribution(
            df)
        quarterly_return, quarterly_return_bucket_summary = quarterly_return_distrubition(
            df)
        market_crisis_return = market_crisis_return_distrubition(df)
        portfolio_value = portfolio_value_table(df)
        cash_management = cash_management_table(df)

        sheets = {
            "All Trades": allTrades,
            "Monthly Return": monthly_return,
            "Monthly Return Bucket Summary": monthly_return_bucket_summary,
            "Quarterly Return": quarterly_return,
            "Quarterly Return Bucket Summary": quarterly_return_bucket_summary,
            "Market Crisis Return": market_crisis_return,
            "Master Analytics": summary,
            "Portfolio Value": portfolio_value,
            "Cash Management": cash_management,
        }

        export_file(sheets,
                    filename=OUTPUT_FILE,
                    timestamp=True)

    except Exception as e:
        print(f"\n❌ Error calculating : {e}")
        exit(1)


if __name__ == "__main__":
    main()
