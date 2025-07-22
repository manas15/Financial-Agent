import yfinance as yf
import pandas as pd

print('Testing Yahoo Finance data collection...')

print('\n1. Getting AAPL stock info...')
aapl = yf.Ticker('AAPL')
info = aapl.info
print(f'AAPL Price: ${info.get("currentPrice", "N/A")}')
print(f'Company: {info.get("longName", "N/A")}')
print(f'Sector: {info.get("sector", "N/A")}')

print('\n2. Getting historical data...')
hist = aapl.history(period="5d")
if not hist.empty:
    print(f'Historical data shape: {hist.shape}')
    print(f'Latest close: ${hist["Close"].iloc[-1]:.2f}')

print('\n3. Getting batch prices...')
symbols = ['AAPL', 'GOOGL', 'MSFT']
data = yf.download(symbols, period="1d", group_by='ticker', progress=False)

if not data.empty:
    print('Batch prices:')
    for symbol in symbols:
        try:
            if len(symbols) == 1:
                latest_close = data['Close'].iloc[-1]
            else:
                latest_close = data[symbol]['Close'].iloc[-1]
            print(f'  {symbol}: ${latest_close:.2f}')
        except:
            print(f'  {symbol}: No data')

print('\n✅ Data collection system working!')