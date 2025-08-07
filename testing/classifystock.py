import pandas as pd
import yfinance as yf
import os

# List of result files
result_files = [
    'd_result/predi_MULTI_real_time_2025_07_29.csv',
    'd_result/predi_MULTI_real_time_2025_07_30.csv',
    'd_result/predi_MULTI_real_time_2025_07_31.csv',
    'd_result/predi_MULTI_real_time_2025_08_01.csv'
]

# Function to safely read and preprocess a single CSV file
def read_single_file(filepath):
    try:
        df = pd.read_csv(filepath)
        
        # Check if required columns exist
        required_columns = ['ticker', 'POS_score', 'NEG_score']
        if not all(col in df.columns for col in required_columns):
            print(f"Warning: Missing required columns in {filepath}. Skipping.")
            return pd.DataFrame()  # Return empty DataFrame
        
        # Select relevant columns and clean data
        df_filtered = df[required_columns].copy()
        df_filtered.dropna(subset=['ticker'], inplace=True)
        df_filtered['ticker'] = df_filtered['ticker'].astype(str).str.strip()
        
        # Convert score columns, handling potential string representations of lists
        def convert_score_column(series):
            def safe_convert(x):
                if pd.isna(x):
                    return 0
                if isinstance(x, (int, float)):
                    return float(x)
                # Handle string representations like '25]' or '[25]'
                x_str = str(x).strip()
                # Remove trailing ']' if present
                if x_str.endswith(']'):
                    x_str = x_str[:-1]
                # Remove leading '[' if present
                if x_str.startswith('['):
                    x_str = x_str[1:]
                try:
                    return float(x_str) if x_str else 0.0
                except ValueError:
                    print(f"Warning: Could not convert '{x}' to float in {filepath}. Setting to 0.0.")
                    return 0.0
            return series.apply(safe_convert)
        
        df_filtered['POS_score'] = convert_score_column(df_filtered['POS_score'])
        df_filtered['NEG_score'] = convert_score_column(df_filtered['NEG_score'])
        
        return df_filtered
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Read and combine all result files
all_data = []
for file in result_files:
    if os.path.exists(file):
        print(f"Reading file: {file}")
        df_temp = read_single_file(file)
        if not df_temp.empty:
            all_data.append(df_temp)
    else:
        print(f"Warning: File {file} not found.")

if not all_data:
    print("Error: No data loaded from any files. Exiting.")
    exit(1)

# Combine all DataFrames
try:
    df_combined = pd.concat(all_data, ignore_index=True)
    print(f"\nCombined data shape: {df_combined.shape}")
except Exception as e:
    print(f"Error combining data: {e}")
    exit(1)

# Get unique tickers
tickers = df_combined['ticker'].unique().tolist()
print(f"Number of unique tickers: {len(tickers)}")

# Function to get sector and industry using yfinance
def get_sector_industry_batch(tickers_batch):
    """
    Fetches sector and industry for a batch of tickers.
    Returns a DataFrame with ticker, sector, industry.
    """
    info_list = []
    for ticker in tickers_batch:
        try:
            # Use yfinance Ticker object
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract sector and industry, defaulting to 'Unknown' if not found
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            info_list.append({
                'ticker': ticker,
                'sector': sector,
                'industry': industry
            })
        except Exception as e:
            print(f"Warning: Could not fetch data for {ticker}: {e}")
            info_list.append({
                'ticker': ticker,
                'sector': 'Unknown',
                'industry': 'Unknown'
            })
    return pd.DataFrame(info_list)

# Process tickers in batches to avoid rate limiting (optional, but good practice)
batch_size = 100
info_all = []
for i in range(0, len(tickers), batch_size):
    batch = tickers[i:i + batch_size]
    print(f"Fetching data for tickers {i+1} to {min(i + batch_size, len(tickers))}...")
    batch_info = get_sector_industry_batch(batch)
    info_all.append(batch_info)

# Combine all batch results
df_info = pd.concat(info_all, ignore_index=True)
print(f"\nFetched info for {len(df_info)} tickers.")

# Save sector and industry mapping to CSV
df_info.to_csv('d_result/ticker_sector_industry_mapping.csv', index=False)
print("Saved 'd_result/ticker_sector_industry_mapping.csv'")

# Merge performance data with sector/industry info
df_merged = pd.merge(df_combined, df_info, on='ticker', how='left')
print(f"Merged data shape: {df_merged.shape}")

# Group by sector and calculate metrics
sector_performance = df_merged.groupby('sector').agg(
    avg_POS_score=('POS_score', 'mean'),
    avg_NEG_score=('NEG_score', 'mean'),
    total_POS_score=('POS_score', 'sum'),
    total_NEG_score=('NEG_score', 'sum'),
    num_stocks=('ticker', 'count')
).reset_index()

sector_performance['net_score'] = sector_performance['total_POS_score'] - sector_performance['total_NEG_score']

# Group by industry and calculate metrics
industry_performance = df_merged.groupby('industry').agg(
    avg_POS_score=('POS_score', 'mean'),
    avg_NEG_score=('NEG_score', 'mean'),
    total_POS_score=('POS_score', 'sum'),
    total_NEG_score=('NEG_score', 'sum'),
    num_stocks=('ticker', 'count')
).reset_index()

industry_performance['net_score'] = industry_performance['total_POS_score'] - industry_performance['total_NEG_score']

# Sort by net score descending
sector_performance = sector_performance.sort_values(by='net_score', ascending=False)
industry_performance = industry_performance.sort_values(by='net_score', ascending=False)

# Save to CSV
sector_performance.to_csv('d_result/performance_by_sector.csv', index=False)
industry_performance.to_csv('d_result/performance_by_industry.csv', index=False)

print("\nPerformance by Sector (sorted by net score):")
print(sector_performance.to_string(index=False))

print("\nPerformance by Industry (sorted by net score):")
print(industry_performance.to_string(index=False))

print("\nAnalysis complete. Results saved to 'd_result/performance_by_sector.csv' and 'd_result/performance_by_industry.csv'.")
