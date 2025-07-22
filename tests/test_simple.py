from src.data.collectors import YahooFinanceCollector

print('Testing Yahoo Finance data collection...')
collector = YahooFinanceCollector()

print('\n1. Getting AAPL stock info...')
aapl_info = collector.get_stock_info('AAPL')
print(f'AAPL Price: ${aapl_info.get("current_price", "N/A")}')
if aapl_info.get('market_cap'):
    print(f'Market Cap: ${aapl_info.get("market_cap"):,}')

print('\n2. Getting batch prices...')
batch = collector.get_batch_prices(['AAPL', 'GOOGL', 'MSFT'])
print(f'Batch data shape: {batch.shape}')
if not batch.empty:
    for _, row in batch.head(3).iterrows():
        print(f'{row["symbol"]}: ${row["price"]:.2f}')

print('\n✅ Data collection system working!')