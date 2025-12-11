# Stock Performance Analysis Tool

A Python application for analyzing trading portfolio performance by comparing returns against the S&P 500 benchmark. The tool provides comprehensive analysis across monthly, quarterly, and market crisis periods, with detailed return distribution and bucket classification.

## Features

- **Monthly Return Distribution**: Calculates monthly portfolio returns and compares them against S&P 500 monthly returns
- **Quarterly Return Distribution**: Aggregates returns by quarter for longer-term performance analysis
- **Market Crisis Analysis**: Evaluates portfolio performance during specific market crisis events (e.g., COVID Crash, 2022 Bear Market, Banking Crisis)
- **Alpha Calculation**: Computes portfolio alpha (excess return over S&P 500 benchmark)
- **Bucket Classification**: Categorizes returns into buckets (default: 2% intervals) for distribution analysis
- **CSV Export**: Exports all analysis results to timestamped CSV files

## Requirements

- Python 3.12.3
- pandas
- numpy
- yfinance
- python-dateutil
- openpyxl (for Excel file support)

## Installation

### Create and activate a virtual environment

```sh
python -m venv .venv
source .venv/bin/activate      # On macOS/Linux
.venv\Scripts\activate         # On Windows
```

### Install dependencies

```sh
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install dependencies manually:

```sh
pip install pandas numpy yfinance python-dateutil openpyxl
```

## Usage

1. **Prepare your trading data file**: Create an Excel (`.xlsx`) or CSV (`.csv`) file with the following columns:
   - `Entry Date`: Date when the trade was entered (YYYY-MM-DD format)
   - `Exit Date`: Date when the trade was exited (YYYY-MM-DD format)
   - `P&L Amount`: Profit or loss amount for the trade

2. **Update the file path** in `main.py`:
   ```python
   FILE_PATH = "trading_data.xlsx"  # Change this to your file name
   ```

3. **Run the analysis**:
   ```sh
   python main.py
   ```

4. **Review results**: All output CSV files are saved in the `output/` directory with timestamps:
   - `monthly_return_distribution_YYYYMMDD-HHMMSS.csv`: Monthly returns with S&P 500 comparison and alpha
   - `monthly_bucket_summary_YYYYMMDD-HHMMSS.csv`: Monthly return distribution buckets
   - `quarterly_return_distribution_YYYYMMDD-HHMMSS.csv`: Quarterly returns with S&P 500 comparison and alpha
   - `quarterly_bucket_summary_YYYYMMDD-HHMMSS.csv`: Quarterly return distribution buckets
   - `market_crisis_return_distrubition_YYYYMMDD-HHMMSS.csv`: Portfolio performance during market crisis events

## Input File Format

Your trading data file should contain the following columns:

| Entry Date | Exit Date | P&L Amount |
|------------|-----------|------------|
| 2020-01-15 | 2020-02-10 | 1250.50 |
| 2020-01-20 | 2020-03-05 | -450.25 |
| 2020-02-01 | 2020-02-28 | 875.00 |

**Notes:**
- Dates can be in various formats (pandas will attempt to parse them)
- P&L Amount should be numeric (positive for profits, negative for losses)
- The tool assumes an initial portfolio value of $100,000

## Output Files

All analysis results are exported to the `output/` directory:

- **Monthly/Quarterly Return Distributions**: Include portfolio returns, S&P 500 returns, alpha, and total portfolio value
- **Bucket Summaries**: Show return distribution across different return ranges
- **Market Crisis Analysis**: Compares portfolio and S&P 500 performance during 17+ major market events from 2016-2024

## Project Structure

```
stock-performance/
├── main.py                                    # Main entry point
├── src/
│   ├── monthly_return_distribution.py        # Monthly return analysis
│   ├── quaterly_return_distrubition.py       # Quarterly return analysis
│   ├── market_crisis_return_distrubition.py  # Market crisis analysis
│   ├── bucket_classification.py              # Return bucket classification
│   └── utils/
│       ├── import_csv.py                     # File import utility
│       ├── export_csv.py                     # CSV export utility
│       └── get_sp500_returns.py              # S&P 500 data fetcher
├── output/                                    # Generated CSV files (gitignored)
└── README.md                                  # This file
```

## How It Works

1. **Data Import**: Reads trading data from Excel or CSV files
2. **Return Calculation**: Calculates portfolio returns based on cumulative P&L from trades
3. **Benchmark Comparison**: Fetches S&P 500 returns using `yfinance` for the same time periods
4. **Alpha Calculation**: Computes portfolio alpha (portfolio return - S&P 500 return)
5. **Distribution Analysis**: Classifies returns into buckets to analyze return distribution patterns
6. **Export**: Saves all results to timestamped CSV files in the `output/` directory

## Notes

- The tool uses an initial portfolio value of $100,000 for calculations
- S&P 500 data is fetched in real-time using Yahoo Finance via `yfinance`
- All date ranges are automatically determined from your trading data
- Market crisis events are pre-defined from 2016-2024 (can be modified in `market_crisis_return_distrubition.py`)

## License

This project is provided as-is for analysis purposes.
