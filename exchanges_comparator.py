#!/usr/bin/env python3
# TODO add more exchages and possibly graph the data
# plot ohcl data
from binance.client import Client
import os
import requests
import time

tickers = [
    "BTC",
    "ETH"
]

usdt_tickers = [x + "USDT" for x in tickers]

# BINANCE
b_usdt_tickers = usdt_tickers

binance_client = Client(os.environ["BINANCE_API_KEY"],
                        os.environ["BINANCE_API_SECRET_KEY"])

b_prices = [x for x in binance_client.get_all_tickers() if x['symbol']
            in b_usdt_tickers]
# KRAKEN
k_usdt_tickers = [x if x != "BTCUSDT" else "XBTUSDT" for x in usdt_tickers]

kraken_tradable_asset_pairs = "https://api.kraken.com/0/public/AssetPairs"

k_asset_pairs = list(requests.get(
    kraken_tradable_asset_pairs).json()['result'])

k_allowed_pairs = [x for x in k_usdt_tickers if x in k_asset_pairs]

kraken_ticker_url = "https://api.kraken.com/0/public/Ticker?pair=" + \
    ",".join(k_allowed_pairs)

kraken_prices = requests.get(kraken_ticker_url).json()['result']

k_prices = []
for ticker in k_allowed_pairs:
    k_prices.append(
        {'symbol': ticker, 'price': kraken_prices[ticker]['c'][0]})

# BITTREX
bit_usdt_tickers = [x + "-USD" for x in tickers]

bit_prices = []
for ticker in bit_usdt_tickers:
    data = requests.get(
        f"https://api.bittrex.com/v3/markets/{ticker}/ticker").json()

    bit_prices.append(
        {'symbol': data['symbol'], 'price': data['lastTradeRate']})

    time.sleep(0.1)

# POLONIEX
p_usdt_tickers = ["USDT_" + x for x in tickers]

data = requests.get("https://poloniex.com/public?command=returnTicker").json()

p_prices = []
for ticker in p_usdt_tickers:
    p_prices.append({"symbol": ticker, "price": data[ticker]['last']})

# HITBTC
hit_usdt_tickers = [x + "USD" for x in tickers]
data = requests.get("https://api.hitbtc.com/api/2/public/ticker?symbols=" +
                    ','.join(hit_usdt_tickers)).json()

hit_prices = []
for i in data:
    hit_prices.append({"symbol": i['symbol'], "price": i['last']})


# DISPLAY
print("BINANCE")
print(b_prices)
print("KRAKEN")
print(k_prices)
print("BITTREX")
print(bit_prices)
print("POLONIEX")
print(p_prices)
print("HITBTC")
print(hit_prices)
