# getstock
# Stock Analysis Pro 📊⏰

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Professional stock analysis tool for intraday data visualization and historical data exploration, featuring interactive charts and detailed trade reports.

## Key Features ✨

- 📅 24-hour historical data analysis for any specified date
- 📈 Interactive time-series chart with price and volume
- 🎨 Three-color volume bars (green/red/gray for up/down/flat)
- 🌐 Automatic time zone conversion (New York/Beijing)
- 📡 Real-time data fetching from Yahoo Finance
- 📜 Scrollable historical data table
- 🖱️ Hover-to-show precise data points

## Tech Stack ⚙️

- GUI Framework: Tkinter
- Data Fetching: yfinance
- Visualization: Matplotlib
- Data Processing: Pandas
- Time Zone Handling: pytz

## Installation 📦

1. Clone repository:
```bash
git clone https://github.com/yourusername/getstock.git
cd getstock



## Usage 🖥️
Run the application:

python stock_app.py
Interface operations:

Enter stock ticker (e.g., AAPL)
Select date (format: YYYY-MM-DD)
Choose display time zone
Click "Generate Report"
Key interactions:

Main chart: Shows price movement and volume
Mouse hover: Displays exact time and price
Data table: Minute-level historical data
Color coding:
Green: Price increase period
Red: Price decrease period
Gray: Price unchanged period

##Notes ⚠️
Requires stable internet connection
Data availability depends on Yahoo Finance API
Complete data only available during NYSE trading hours (09:30-16:00 EST)
No data will be shown for non-trading days

##Contributing 🤝
We welcome contributions! Please follow these steps:


