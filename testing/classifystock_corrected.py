import pandas as pd
import yfinance as yf
import os
import re

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
        # Read the file line by line to handle malformed rows
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Process lines to fix malformed score columns
        processed_lines = []
        for line in lines:
            # Split by comma but be careful with the score columns
            parts = line.strip().split(',')
            if len(parts) >= 9:  # Ensure we have enough columns
                # Fix POS_score column (index 5)
                pos_score = parts[5].strip()
                if pos_score.endswith(']'):
                    pos_score = pos_score[:-1]  # Remove trailing ']'
                if pos_score.startswith('['):
                    pos_score = pos_score[1:]   # Remove leading '['
                parts[5] = pos_score
                
                # Fix NEG_score column (index 7)
                neg_score = parts[7].strip()
                if neg_score.endswith(']'):
                    neg_score = neg_score[:-1]  # Remove trailing ']'
                if neg_score.startswith('['):
                    neg_score = neg_score[1:]   # Remove leading '['
                parts[7] = neg_score
                
                # Rejoin the line
                processed_line = ','.join(parts)
                processed_lines.append(processed_line)
            else:
                processed_lines.append(line.strip())
        
        # Write processed lines to a temporary file
        temp_filepath = filepath + '.tmp'
        with open(temp_filepath, 'w') as f:
            f.write('\n'.join(processed_lines))
        
        # Read the processed file with pandas
        df = pd.read_csv(temp_filepath)
        
        # Clean up temporary file
        os.remove(temp_filepath)
        
        # Check if required columns exist
        required_columns = ['ticker', 'POS_score', 'NEG_score']
        if not all(col in df.columns for col in required_columns):
            print(f"Warning: Missing required columns in {filepath}. Skipping.")
            return pd.DataFrame()  # Return empty DataFrame
        
        # Select relevant columns and clean data
        df_filtered = df[required_columns].copy()
        df_filtered.dropna(subset=['ticker'], inplace=True)
        df_filtered['ticker'] = df_filtered['ticker'].astype(str).str.strip()
        
        # Convert score columns to numeric
        df_filtered['POS_score'] = pd.to_numeric(df_filtered['POS_score'], errors='coerce').fillna(0)
        df_filtered['NEG_score'] = pd.to_numeric(df_filtered['NEG_score'], errors='coerce').fillna(0)
        
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

# Process tickers in batches to avoid rate limiting
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
