# Stock Performance Analysis by Sector and Industry

## Executive Summary

This analysis examines stock performance data across multiple sectors and industries based on predictive model scores. The analysis reveals significant variations in performance metrics across different sectors, with Energy and Financial sectors showing distinct patterns.

## Methodology

The analysis aggregates POS_score and NEG_score metrics from predictive models across multiple time periods. For each sector and industry, we calculated:
- Average POS_score and NEG_score
- Total POS_score and NEG_score
- Net score (Total POS_score - Total NEG_score)
- Number of stocks analyzed

## Performance by Sector

| Sector | Avg POS Score | Avg NEG Score | Total POS Score | Total NEG Score | Net Score | Number of Stocks |
|--------|---------------|---------------|-----------------|-----------------|-----------|------------------|
| Energy | 88.37 | 42.04 | 65,746 | 31,280 | 34,466 | 744 |
| Consumer Defensive | 135.05 | 102.23 | 25,930 | 19,629 | 6,301 | 192 |
| Utilities | 0.00 | 0.00 | 0 | 0 | 0 | 12 |
| Industrials | 73.46 | 86.09 | 91,819 | 107,607 | -15,788 | 1,250 |
| Consumer Cyclical | 21.15 | 94.31 | 8,163 | 36,403 | -28,240 | 386 |
| Technology | 87.72 | 114.73 | 135,962 | 177,832 | -41,870 | 1,550 |
| Communication Services | 76.89 | 123.99 | 102,719 | 165,644 | -62,925 | 1,336 |
| Financial Services | 91.86 | 107.03 | 430,648 | 501,754 | -71,106 | 4,688 |

## Top Performing Industries

| Industry | Avg POS Score | Avg NEG Score | Total POS Score | Total NEG Score | Net Score | Number of Stocks |
|----------|---------------|---------------|-----------------|-----------------|-----------|------------------|
| Integrated Freight & Logistics | 114.47 | 45.96 | 64,788 | 26,012 | 38,776 | 566 |
| Thermal Coal | 88.37 | 42.04 | 65,746 | 31,280 | 34,466 | 744 |
| Banks - Diversified | 138.65 | 120.20 | 183,012 | 158,662 | 24,350 | 1,320 |
| Electronic Gaming & Multimedia | 167.61 | 110.36 | 63,690 | 41,936 | 21,754 | 380 |
| Banks - Regional | 74.68 | 62.27 | 83,192 | 69,370 | 13,822 | 1,114 |

## Underperforming Industries

| Industry | Avg POS Score | Avg NEG Score | Total POS Score | Total NEG Score | Net Score | Number of Stocks |
|----------|---------------|---------------|-----------------|-----------------|-----------|------------------|
| Internet Content & Information | 40.83 | 129.40 | 39,029 | 123,708 | -84,679 | 956 |
| Conglomerates | 39.52 | 119.29 | 27,031 | 81,595 | -54,564 | 684 |
| Insurance - Life | 83.38 | 117.29 | 154,094 | 216,760 | -62,666 | 1,848 |
| Financial Data & Stock Exchanges | 19.03 | 138.13 | 7,230 | 52,490 | -45,260 | 380 |
| Auto Manufacturers | 21.15 | 94.31 | 8,163 | 36,403 | -28,240 | 386 |

## Key Insights

1. **Energy Sector Strength**: The Energy sector, particularly Thermal Coal, shows strong positive net scores, indicating favorable predictive performance.

2. **Financial Sector Complexity**: While Banks - Diversified show positive net scores, other financial segments like Insurance - Life show significant negative net scores.

3. **Technology Challenges**: The Technology sector shows substantial negative net scores, suggesting potential challenges in predictive accuracy for this sector.

4. **Industry Variations**: Significant performance variations exist within sectors, highlighting the importance of industry-level analysis.

## Data Sources

- 16 CSV files containing predictive model scores
- 25 unique tickers analyzed
- Yahoo Finance data for sector and industry classification

## Limitations

- Analysis is based on predictive model scores, not actual market performance
- Limited to specific time periods represented in the data files
- Sector and industry classifications are based on Yahoo Finance categorizations
