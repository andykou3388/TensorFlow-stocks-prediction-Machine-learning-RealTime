import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Read the CSV file with custom handling
try:
    # First, let's read the file and fix the header
    with open('d_result/predi_MULTI_real_time_2025_08_01.csv', 'r') as f:
        lines = f.readlines()
    
    # Fix the header line
    header = lines[0].strip()
    # Add spaces to separate column names properly
    fixed_header = "Index\tDate\tticker\tbuy_sell_point\tClose\tVolume\tPOS_score\tPOS_num\tNEG_score\tNEG_num\tPOS_score_list\tNEG_score_list\tPOS_models_name\tNEG_moldel_name\n"
    
    # Write fixed content to a temporary file
    with open('temp_fixed_file.csv', 'w') as f:
        f.write(fixed_header)
        f.writelines(lines[1:])
    
    # Now read with pandas
    df = pd.read_csv('temp_fixed_file.csv', sep='\t')
    print("File read successfully with tab separator")
    
except Exception as e:
    print(f"Error reading with tab separator: {e}")
    try:
        # Try with pandas directly but with error handling
        df = pd.read_csv('d_result/predi_MULTI_real_time_2025_08_01.csv', sep='\t', on_bad_lines='skip')
        print("File read with bad lines skipped")
    except Exception as e2:
        print(f"Error reading with pandas: {e2}")
        # Try reading with space separator
        df = pd.read_csv('d_result/predi_MULTI_real_time_2025_08_01.csv', sep='\s+', on_bad_lines='skip')
        print("File read with space separator")

# Display basic info about the dataframe
print(f"Dataframe shape: {df.shape}")
print("Columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Parse the Date column if it exists
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Convert POS_score and NEG_score to numeric if they exist
if 'POS_score' in df.columns:
    df['POS_score'] = pd.to_numeric(df['POS_score'], errors='coerce')
if 'NEG_score' in df.columns:
    df['NEG_score'] = pd.to_numeric(df['NEG_score'], errors='coerce')

# Calculate net score (POS - NEG) if both columns exist
if 'POS_score' in df.columns and 'NEG_score' in df.columns:
    df['Net_Score'] = df['POS_score'] - df['NEG_score']

# Create visualizations if we have the necessary data
if 'Date' in df.columns and 'POS_score' in df.columns and 'NEG_score' in df.columns and 'ticker' in df.columns:
    fig = plt.figure(figsize=(20, 15))

    # 1. Time series of POS and NEG scores by ticker
    ax1 = plt.subplot(3, 3, 1)
    sample_tickers = df['ticker'].unique()[:5]  # Limit to first 5 tickers for clarity
    for ticker in sample_tickers:
        ticker_data = df[df['ticker'] == ticker].sort_values('Date')
        if len(ticker_data) > 0:
            ax1.plot(ticker_data['Date'], ticker_data['POS_score'], label=f'{ticker} POS', alpha=0.7)
            ax1.plot(ticker_data['Date'], ticker_data['NEG_score'], label=f'{ticker} NEG', alpha=0.7, linestyle='--')
    ax1.set_title('POS and NEG Scores Over Time (Sample Tickers)')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Score')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.tick_params(axis='x', rotation=45)

    # 2. Net Score Distribution
    ax2 = plt.subplot(3, 3, 2)
    if 'Net_Score' in df.columns:
        df['Net_Score'].hist(bins=30, ax=ax2, color='skyblue', edgecolor='black')
        ax2.set_title('Distribution of Net Scores (POS - NEG)')
        ax2.set_xlabel('Net Score')
        ax2.set_ylabel('Frequency')

    # 3. POS vs NEG Scatter Plot
    ax3 = plt.subplot(3, 3, 3)
    if 'Net_Score' in df.columns:
        scatter = ax3.scatter(df['NEG_score'], df['POS_score'], c=df['Net_Score'], cmap='coolwarm', alpha=0.6)
        ax3.set_xlabel('NEG Score')
        ax3.set_ylabel('POS Score')
        ax3.set_title('POS vs NEG Scores (Color = Net Score)')
        plt.colorbar(scatter, ax=ax3, label='Net Score')

    # 4. Average Scores by Ticker (Top 10)
    ax4 = plt.subplot(3, 3, 4)
    if 'Net_Score' in df.columns:
        top_tickers = df.groupby('ticker').agg({
            'POS_score': 'mean',
            'NEG_score': 'mean'
        }).sort_values('POS_score', ascending=False).head(10)

        x = np.arange(len(top_tickers))
        width = 0.35

        ax4.bar(x - width/2, top_tickers['POS_score'], width, label='POS Score', color='green', alpha=0.7)
        ax4.bar(x + width/2, top_tickers['NEG_score'], width, label='NEG Score', color='red', alpha=0.7)
        ax4.set_xlabel('Ticker')
        ax4.set_ylabel('Average Score')
        ax4.set_title('Average POS and NEG Scores by Ticker (Top 10)')
        ax4.set_xticks(x)
        ax4.set_xticklabels(top_tickers.index, rotation=45)
        ax4.legend()

    # 5. Volume vs Net Score
    ax5 = plt.subplot(3, 3, 5)
    if 'Volume' in df.columns and 'Net_Score' in df.columns:
        ax5.scatter(df['Volume'], df['Net_Score'], alpha=0.6)
        ax5.set_xlabel('Volume')
        ax5.set_ylabel('Net Score')
        ax5.set_title('Volume vs Net Score')
        ax5.set_xscale('log')

    # 6. Close Price vs Net Score
    ax6 = plt.subplot(3, 3, 6)
    if 'Close' in df.columns and 'Net_Score' in df.columns:
        ax6.scatter(df['Close'], df['Net_Score'], alpha=0.6)
        ax6.set_xlabel('Close Price')
        ax6.set_ylabel('Net Score')
        ax6.set_title('Close Price vs Net Score')

    # 7. Score Correlation Heatmap
    ax7 = plt.subplot(3, 3, 7)
    corr_columns = []
    if 'POS_score' in df.columns:
        corr_columns.append('POS_score')
    if 'NEG_score' in df.columns:
        corr_columns.append('NEG_score')
    if 'Net_Score' in df.columns:
        corr_columns.append('Net_Score')
    if 'Close' in df.columns:
        corr_columns.append('Close')
    if 'Volume' in df.columns:
        corr_columns.append('Volume')
        
    if len(corr_columns) > 1:
        corr_data = df[corr_columns].corr()
        sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax7)
        ax7.set_title('Correlation Matrix')

    # 8. Distribution of POS_num and NEG_num
    ax8 = plt.subplot(3, 3, 8)
    if 'POS_num' in df.columns or 'NEG_num' in df.columns:
        # Extract numeric values from POS_num and NEG_num
        if 'POS_num' in df.columns:
            df['POS_num_clean'] = df['POS_num'].astype(str).str.extract(r'(\d+)').astype(float)
        if 'NEG_num' in df.columns:
            df['NEG_num_clean'] = df['NEG_num'].astype(str).str.extract(r'(\d+)').astype(float)
        
        if 'POS_num_clean' in df.columns:
            ax8.hist(df['POS_num_clean'].dropna(), bins=20, alpha=0.7, label='POS Models', color='green')
        if 'NEG_num_clean' in df.columns:
            ax8.hist(df['NEG_num_clean'].dropna(), bins=20, alpha=0.7, label='NEG Models', color='red')
        ax8.set_xlabel('Number of Models')
        ax8.set_ylabel('Frequency')
        ax8.set_title('Distribution of Models per Prediction')
        ax8.legend()

    # 9. Net Score by Time of Day
    ax9 = plt.subplot(3, 3, 9)
    if 'Date' in df.columns and 'Net_Score' in df.columns:
        df['Hour'] = df['Date'].dt.hour
        hourly_net = df.groupby('Hour')['Net_Score'].mean()
        ax9.bar(hourly_net.index, hourly_net.values, color='purple', alpha=0.7)
        ax9.set_xlabel('Hour of Day')
        ax9.set_ylabel('Average Net Score')
        ax9.set_title('Average Net Score by Hour')

    plt.tight_layout()
    plt.savefig('prediction_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

# Print summary statistics
print("\n=== PREDICTION PERFORMANCE SUMMARY ===")
print(f"Total predictions: {len(df)}")
if 'ticker' in df.columns:
    print(f"Unique tickers: {df['ticker'].nunique()}")
if 'Date' in df.columns:
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

if 'POS_score' in df.columns:
    print(f"\nPOS Score - Mean: {df['POS_score'].mean():.2f}, Std: {df['POS_score'].std():.2f}")
if 'NEG_score' in df.columns:
    print(f"NEG Score - Mean: {df['NEG_score'].mean():.2f}, Std: {df['NEG_score'].std():.2f}")
if 'Net_Score' in df.columns:
    print(f"Net Score - Mean: {df['Net_Score'].mean():.2f}, Std: {df['Net_Score'].std():.2f}")

# Find best and worst performing tickers
if 'ticker' in df.columns and 'Net_Score' in df.columns:
    ticker_stats = df.groupby('ticker').agg({
        'Net_Score': ['mean', 'count'],
        'POS_score': 'mean',
        'NEG_score': 'mean'
    }).round(2)

    ticker_stats.columns = ['Net_Score_Mean', 'Prediction_Count', 'POS_Score_Mean', 'NEG_Score_Mean']
    best_tickers = ticker_stats.sort_values('Net_Score_Mean', ascending=False).head(5)
    worst_tickers = ticker_stats.sort_values('Net_Score_Mean', ascending=True).head(5)

    print("\n=== TOP 5 BEST PERFORMING TICKERS (BY NET SCORE) ===")
    print(best_tickers)

    print("\n=== TOP 5 WORST PERFORMING TICKERS (BY NET SCORE) ===")
    print(worst_tickers)

    # Save summary to CSV
    ticker_stats.to_csv('ticker_performance_summary.csv')
    print("\nTicker performance summary saved to 'ticker_performance_summary.csv'")

print("Visualization saved to 'prediction_performance_analysis.png'")
