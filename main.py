from src.monthly_return_distribution import monthly_return_distribution
from src.quaterly_return_distrubition import quaterly_return_distrubition
from src.market_crisis_return_distrubition import market_crisis_return_distrubition
from src.utils.import_csv import import_csv

# ========== FILE IMPORT ==========

# Option 1: Specify the file path directly
FILE_PATH = "trading_data.xlsx"  # Change this to your file name

# Option 2: Let user input the file path
# FILE_PATH = input("Enter the path to your trading data file (.xlsx or .csv): ")


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
        monthly_return_distribution(df)
        quaterly_return_distrubition(df)
        market_crisis_return_distrubition(df)
    except Exception as e:
        print(f"\n❌ Error calculating monthly return distribution: {e}")
        exit(1)


if __name__ == "__main__":
    main()
