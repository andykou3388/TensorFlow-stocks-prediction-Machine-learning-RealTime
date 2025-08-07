import pandas as pd
import yfinance as yf
import os
import glob

# Find all predi_MULTI_real_time CSV files
result_files = glob.glob('d_result/predi_MULTI_real_time_*.csv')

print(f"Found {len(result_files)} CSV files:")
for file in result_files:
    print(f"  - {file}")

# Function to safely read and preprocess a single CSV file
def read_single_file(filepath):
    try:
        # Read the file with pandas, handling the complex format
        df = pd.read_csv(filepath, sep=',', skipinitialspace=True, encoding='utf-8')
        
        # Display basic info about the dataframe
        print(f"\\nFile: {filepath}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Display first few rows to understand the structure
        print("\\nFirst 3 rows:")
        print(df.head(3))
        
        # Check if required columns exist
        required_columns = ['ticker', 'POS_score', 'NEG_score']
        if not all(col in df.columns for col in required_columns):
            print(f"Warning: Missing required columns in {filepath}. Available columns: {list(df.columns)}")
            return pd.DataFrame()  # Return empty DataFrame
        
        # Select relevant columns and clean data
        df_filtered = df[required_columns].copy()
        df_filtered.dropna(subset=['ticker'], inplace=True)
        df_filtered['ticker'] = df_filtered['ticker'].astype(str).str.strip()
        
        # Convert score columns to numeric, handling various formats
        df_filtered['POS_score'] = pd.to_numeric(df_filtered['POS_score'], errors='coerce').fillna(0)
        df_filtered['NEG_score'] = pd.to_numeric(df_filtered['NEG_score'], errors='coerce').fillna(0)
        
        return df_filtered
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()  # Return empty DataFrame on error

# Read and combine all result files
all_data = []
for file in result_files:
    if os.path.exists(file):
        print(f"\\nReading file: {file}")
        df_temp = read_single_file(file)
        if not df_temp.empty:
            all_data.append(df_temp)
            print(f"Successfully read {len(df_temp)} rows from {file}")
        else:
            print(f"Failed to read data from {file}")
    else:
        print(f"Warning: File {file} not found.")

if not all_data:
    print("\\nError: No data loaded from any files. Exiting.")
    exit(1)

# Combine all DataFrames
try:
    df_combined = pd.concat(all_data, ignore_index=True)
    print(f"\\nCombined data shape: {df_combined.shape}")
    print(f"Unique tickers: {df_combined['ticker'].nunique()}")
except Exception as e:
    print(f"Error combining data: {e}")
    exit(1)

# Display some statistics
print("\\nSample of combined data:")
print(df_combined.head(10))

print("\\nTicker frequency:")
print(df_combined['ticker'].value_counts().head(10))

# Get unique tickers
tickers = df_combined['ticker'].unique().tolist()
print(f"\\nNumber of unique tickers: {len(tickers)}")

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

# Process tickers in batches to avoid rate limiting
batch_size = 100
info_all = []
for i in range(0, len(tickers), batch_size):
    batch = tickers[i:i + batch_size]
    print(f"\\nFetching data for tickers {i+1} to {min(i + batch_size, len(tickers))}...")
    batch_info = get_sector_industry_batch(batch)
    info_all.append(batch_info)

# Combine all batch results
df_info = pd.concat(info_all, ignore_index=True)
print(f"\\nFetched info for {len(df_info)} tickers.")

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

print("\\nPerformance by Sector (sorted by net score):")
print(sector_performance.to_string(index=False))

print("\\nPerformance by Industry (sorted by net score):")
print(industry_performance.to_string(index=False))

print("\\nAnalysis complete. Results saved to 'd_result/performance_by_sector.csv' and 'd_result/performance_by_industry.csv'.")
