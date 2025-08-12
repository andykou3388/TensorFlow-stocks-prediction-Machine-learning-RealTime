# Execution Plan for Stock Prediction System

## Overview
This execution plan outlines the steps to run and maintain a stock prediction system that analyzes HSI index components, leveraged ETFs, and Hong Kong ETFs. The system generates predictions for a weekly period (5 working days) and runs daily at noon.

## System Components

### Stock Categories
1. **HSI Index Components**: 75 stocks (e.g., 00001.HK, 00002.HK, 00003.HK, etc.)
2. **Leveraged ETFs**: 18 stocks (e.g., 07226.HK, 07552.HK, 07200.HK, etc.)
3. **Hong Kong ETFs**: 16 stocks (e.g., 02800.HK, 02835.HK, 03012.HK, etc.)

### Data Files
- Prediction results stored in `/usr/src/appv1/d_result/`
- Historical prediction files for analysis (e.g., `sent_predi_MULTI_real_time_2025_07_14.csv` through `sent_predi_MULTI_real_time_2025_08_07.csv`)
- Analysis reports: `analysis.md`, `analysis_by_sector.md`, `key_findings_and_recommendations.md`
- Sector/industry mapping: `ticker_sector_industry_mapping.csv`
- Performance by sector/industry: `performance_by_sector.csv`, `performance_by_industry.csv`

### Core Scripts
1. `1_Get_technical_indicators.py` - Calculates technical indicators
2. `3_Model_creation_models_for_a_stock.py` - Creates models for individual stocks
3. `4_Model_creation_scoring_multi.py` - Creates scoring models for multiple stocks
4. `5_predict_POOL_enque_Thread.py` - Real-time prediction generation and alert system

## Execution Workflow

### 1. Data Collection and Preparation
- Collect stock data for all 75 HSI components, 18 leveraged ETFs, and 16 Hong Kong ETFs
- Store raw data in appropriate directories (`d_price/`, `d_price/RAW/`, `d_price/RAW_alpha/`)
- Ensure data is updated daily through `yhoo_history_stock.py` and related scripts

### 2. Technical Indicator Calculation
- Run `1_Get_technical_indicators.py` to calculate technical indicators for all stocks
- This script generates:
  - Scaled stock history files (`AMD_SCALA_stock_history_MONTH_3_AD.csv`)
  - Min/max scaling keys (`d_price/min_max/AMD_min_max_stock_MONTH_3_AD.csv`)
  - Pure OHLCV history (`AMD_stock_history_MONTH_3_AD.csv`)
- Store results in `d_price/` directory with appropriate subdirectories

### 3. Model Creation
- Execute `3_Model_creation_models_for_a_stock.py` to create individual stock models
- Run `4_Model_creation_scoring_multi.py` to create multi-stock scoring models
- Models are stored in `Models/` directory with subdirectories:
  - `Models/all_results/`
  - `Models/TF_balance/`
  - `Models/TF_multi/`

### 4. Real-time Prediction System
- Run `5_predict_POOL_enque_Thread.py` for continuous prediction generation
- This script uses threading to:
  - Producer thread: Continuously fetches OHLCV data
  - Consumer threads: Process data, calculate technical parameters, make predictions
- Predictions are registered in `_KEYS_DICT.PATH_REGISTER_RESULT_MULTI_REAL_TIME` (current date file)
- Sent alerts are tracked in `_KEYS_DICT.PATH_REGISTER_RESULT_MULTI_REAL_TIME_SENT` (current date file)

### 5. Prediction Generation and Storage
- Generate predictions for the next 5 working days
- Store predictions in CSV files with date-specific naming in `d_result/` directory
- Files follow the pattern: `sent_predi_MULTI_real_time_YYYY_MM_DD.csv`
- Each file contains:
  - Date and time of prediction
  - Stock ticker
  - Buy/sell point indicator
  - Closing price
  - Volume
  - POS_score and NEG_score (model confidence scores)
  - Model names used for positive and negative predictions

### 6. Analysis and Reporting
- Analyze prediction performance using scripts in `testing/` directory:
  - `testing/classifystock_final.py` - Main analysis script
  - Generates sector/industry mapping and performance metrics
- Generate reports in markdown format:
  - `d_result/analysis.md` - Overall performance analysis
  - `d_result/analysis_by_sector.md` - Detailed sector analysis
  - `d_result/key_findings_and_recommendations.md` - Strategic recommendations
- Additional CSV outputs:
  - `d_result/ticker_sector_industry_mapping.csv`
  - `d_result/performance_by_sector.csv`
  - `d_result/performance_by_industry.csv`

### 7. Alert System
- Telegram alerts are sent via `ztelegram_send_message.py`
- Alert criteria defined in `will_send_alert()` function:
  - More than half of models have a score greater than 93%
  - TF models have a score greater than 93%
- Alerts are sent to users registered in the system
- Images and charts can be included in alerts via `get_traderview_screem_shot()`

### 8. Sentiment Analysis Integration
- News sentiment data collected via `news_sentiment/` directory scripts:
  - `news_sentiment/news_get_data_NUTS.py` - Main sentiment collection
  - `news_sentiment/news_sentiment.py` - Sentiment analysis
- Results stored in `d_sentiment/` directory
- JSON files generated for integration with prediction models

## Daily Execution Sequence

```bash
# At 12:00 PM daily
0. Verify system resources and dependencies
1. Data collection and update:
   - python yhoo_history_stock.py  # Update stock data
2. Technical indicator calculation:
   - python 1_Get_technical_indicators.py
3. Model creation:
   - python 3_Model_creation_models_for_a_stock.py
   - python 4_Model_creation_scoring_multi.py
4. Start real-time prediction system:
   - python 5_predict_POOL_enque_Thread.py
5. Generate daily analysis reports:
   - python testing/classifystock_final.py
6. Performance analysis and reporting
7. Backup critical files
```

## Weekly Review Process

### Monday
- Review previous week's predictions and actual results
- Update models based on performance analysis
- Check sector performance trends
- Review `d_result/analysis_by_sector.md` for insights

### Wednesday
- Mid-week performance check
- Adjust parameters if necessary
- Monitor alert system performance
- Check `d_result/key_findings_and_recommendations.md` for updates

### Friday
- Weekly performance analysis
- Generate comprehensive reports
- Prepare recommendations for the upcoming week
- Review model accuracy and make improvements

## Monitoring and Maintenance

### Log Management
- Regularly check logs in `/Logs/` directory
- Monitor for errors or anomalies
- Clean up old log files periodically
- Key log files:
  - `Logs/Log.log` - Main application log
  - `Logs/Log.log.YYYY-MM-DD_HH` - Timestamped logs

### Performance Tracking
- Track prediction accuracy in `prediction_performance_analysis.png`
- Monitor model performance and update as needed
- Review `d_result/performance_by_sector.csv` and `d_result/performance_by_industry.csv`
- Check alert effectiveness in Telegram messaging

### Data Validation
- Verify data integrity for all stock categories
- Ensure all 75 HSI components, 18 leveraged ETFs, and 16 Hong Kong ETFs are included
- Validate sector/industry classifications
- Check for missing or corrupted data files

### System Health
- Monitor CPU and memory usage during execution
- Ensure sufficient disk space for data storage
- Verify network connectivity for data collection
- Check Python environment and dependencies

## Backup and Recovery

### Daily
- Backup prediction results (`d_result/sent_predi_MULTI_real_time_YYYY_MM_DD.csv`)
- Archive log files
- Backup model files (`Models/` directory)

### Weekly
- Full system backup
- Verify backup integrity
- Test recovery procedures
- Archive historical prediction files

## Troubleshooting

### Common Issues
1. **Data collection failures**
   - Check network connectivity
   - Verify API keys and credentials
   - Review logs for specific error messages
   - Test data sources independently

2. **Model training errors**
   - Check for insufficient data
   - Verify technical indicator calculations
   - Review model configuration in `_KEYS_DICT.py`
   - Ensure sufficient system resources

3. **Prediction generation problems**
   - Validate input data format
   - Check model file integrity
   - Review scaling parameters
   - Monitor thread execution in `5_predict_POOL_enque_Thread.py`

4. **Alert system issues**
   - Verify Telegram bot configuration
   - Check internet connectivity
   - Review alert criteria in `ztelegram_send_message.py`
   - Test message sending independently

5. **Storage space issues**
   - Clean up old log files
   - Archive historical data
   - Monitor disk usage regularly
   - Implement automated cleanup scripts

### Resolution Steps
1. Check logs in `/Logs/` directory for error messages
2. Verify data sources are accessible and returning valid data
3. Ensure sufficient system resources (CPU, memory, disk space)
4. Validate Python environment and dependencies in `requirements.txt`
5. Test individual components in isolation
6. Review configuration files (`CONFIG.py`, `_KEYS_DICT.py`)

## Future Enhancements

### Short-term
- Implement real-time sentiment analysis from `news_sentiment/` directory
- Add more technical indicators to improve prediction accuracy
- Enhance model selection algorithms in `4_Model_creation_scoring_multi.py`
- Improve alert filtering to reduce noise

### Medium-term
- Integrate reinforcement learning models from `Reinforcement_Learning/` directory
- Develop sector-specific models for better performance
- Implement automated model retraining based on performance metrics
- Add web dashboard for visualization using existing `plots_relations/` data

### Long-term
- Expand to other markets and indices beyond HSI
- Develop mobile application for alerts and monitoring
- Implement machine learning model optimization
- Add portfolio management features

## Key Performance Indicators (KPIs)

### Model Performance
- Accuracy of buy/sell predictions
- POS_score and NEG_score distributions
- Sector-wise performance metrics
- Model consistency over time

### System Performance
- Prediction generation time
- Alert delivery success rate
- System uptime and availability
- Resource utilization metrics

### Business Metrics
- Number of actionable alerts generated
- User engagement with alerts
- Prediction-to-actual result correlation
- Sector rotation detection accuracy

## Conclusion
This execution plan provides a structured approach to running the stock prediction system. By following this plan, we can ensure consistent daily operations, accurate predictions, continuous system improvement, and effective alert generation. The system's modular design allows for targeted improvements in specific areas while maintaining overall stability and reliability.
