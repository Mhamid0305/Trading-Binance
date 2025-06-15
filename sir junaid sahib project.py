from binance.client import Client
import statistics
import os

# === Initialize Binance client ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# === Download past 1-year BTC/USDT hourly candlestick data ===
data = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 year ago UTC")

# Extract only the closing prices
closing_prices = [float(entry[4]) for entry in data]

# === Initial portfolio ===
balance_usdt = 1000.0
btc_owned = 0.0
in_usdt = True
executed_trades = []

# === Run Bollinger Band strategy on historical data ===
for idx in range(20, len(closing_prices)):
    recent_prices = closing_prices[idx - 20:idx]
    avg_price = statistics.mean(recent_prices)
    deviation = statistics.stdev(recent_prices)

    upper_limit = avg_price + 2 * deviation
    lower_limit = avg_price - 2 * deviation
    market_price = closing_prices[idx]

    # Buying condition
    if in_usdt and market_price < lower_limit:
        btc_owned = balance_usdt / market_price
        balance_usdt = 0
        in_usdt = False
        executed_trades.append(("BUY", market_price, idx))

    # Selling condition
    elif not in_usdt and market_price > upper_limit:
        balance_usdt = btc_owned * market_price
        btc_owned = 0
        in_usdt = True
        executed_trades.append(("SELL", market_price, idx))

# === Final Portfolio Summary ===
final_value = balance_usdt if in_usdt else btc_owned * closing_prices[-1]

print("\n===== TRADING RESULTS =====")
print("Total Trades Made:", len(executed_trades))
print("Final Portfolio Value:", round(final_value, 2), "USDT")
print("\nTrade Log:")
for action, price, index in executed_trades:
    print(f"{action} at ${price:.2f} on candle index {index}")
