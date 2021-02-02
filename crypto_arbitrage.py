#!/usr/bin/env python3
# TODO use pairs instead of coins for lookup

import requests
from pycoingecko import CoinGeckoAPI
import operator
import random
import pandas as pd
import crypto_database as crypto_db
import time

# wait in seconds
query_interval = 60

exchanges = [
    'Huobi Global',
    'Poloniex',
    'Kraken',
    'Kucoin',
    'Bittrex',
    'Binance',
    'HitBTC',
    'Upbit',
    'Coineal'
]

coins = [{'id': 'ethereum'},
         {'id': 'monero'},
         {'id': 'chainlink'},
         {'id': 'tether'},
         {'id': 'polkadot'},
         {'id': 'cardano'},
         {'id': 'litecoin'},
         {'id': 'ripple'},
         {'id': 'tron'},
         {'id': 'eos'},
         {'id': 'bitcoin'},
         {'id': 'bitcoin-cash'},
         {'id': 'stellar'},
         {'id': 'the-graph'},
         {'id': 'zcash'},
         ]

pd.set_option('display.max_rows', None)


# get dataframe with all the coins on coingecko


def get_coin_df():
    cg = CoinGeckoAPI()
    coins_list = cg.get_coins_list()
    return pd.json_normalize(coins_list)


# get coin data from selected exchanges
def get_coin_pair_data(exclude=[], include_exchanges=[], include_coins=[]):
    cg = CoinGeckoAPI()
    coins = []
    if(include_coins == []):
        coins = cg.get_coins_list()
        random.shuffle(coins)
    else:
        coins = include_coins

    coin_data = []
    for coin in coins:
        print("Getting coin: " + coin["id"])
        try:
            market_data = cg.get_coin_by_id(coin['id'])['tickers']
            pairs_data = []
            for i in market_data:
                market = i['market']['name']
                price = float(i['converted_last']['usd'])
                volume = float(i['converted_volume']['usd'])
                info = {'market': market,
                        'price': price,
                        'target': i['target'],
                        'volume': volume
                        }
                if len(include_exchanges) == 0:
                    if market not in exclude:
                        pairs_data.append(info)
                else:
                    if market in include_exchanges:
                        pairs_data.append(info)
            coin_data.append({'name': i['base'], 'market data': pairs_data})
        except Exception as e:
            print("ERROR:")
            print(e)
            continue
    return (coin_data)


# filter data by spread
def coins_by_spread(coins, min_volume=5000):
    coins_spread = []
    for coin in coins:
        prices = []
        for m in coin['market data']:
            vol = m['volume']
            if vol >= min_volume:
                prices.append({'price': m['price'], 'market': m['market']})
        if len(prices) > 1:
            max_price = max(list(map(lambda x: x["price"], prices)))
            min_price = min(list(map(lambda x: x["price"], prices)))
            max_market = [x['market']
                          for x in prices if x['price'] == max_price][0]
            min_market = [x['market']
                          for x in prices if x['price'] == min_price][0]
            spread = ((max_price - min_price) / min_price) * 100
            if min_market != max_market:
                coins_spread.append(
                    {'name': coin['name'], 'spread': spread, 'max_market': max_market, 'min_market': min_market, 'max_price': max_price, 'min_price': min_price})
            else:
                continue
    coins_spread.sort(key=operator.itemgetter('spread'))
    return (coins_spread)


def get_coins_with_spread(coins, exchanges, min_spread=0.01):
    print("#######################################")
    print("#######################################")
    print("Exchanges:")
    print(exchanges)
    print("#######################################")
    print("#######################################")
    print("Coins:")
    print(coins)
    print("#######################################")
    print("#######################################")
    coins = get_coin_pair_data(
        include_exchanges=exchanges, include_coins=coins)
    coins = coins_by_spread(coins)
    return (coins)


def run_query():
    global coins
    global exchanges
    coins_spread = get_coins_with_spread(coins, exchanges)
    print("#######################################")
    print("#######################################")
    print("Results:")
    for coin in coins_spread:
        market_string = f"from {coin['max_price']} on {coin['max_market']} to {coin['min_price']} on {coin['min_market']}"
        spread = 'spread: ' + str(coin['spread'])[:4] + '%'
        print(coin['name'], spread, market_string)
    print("#######################################")
    print("#######################################")
    print("Data:")
    for coin in coins_spread:
        print(coin)
    return coins_spread


def query_loop():
    global query_interval
    print("#######################################")
    print("#######################################")
    print(f"Starting main loop. Interval is set to {query_interval}")
    # main loop
    while(True):
        # query spread data
        spread_data = run_query()
        # save it to the database
        crypto_db.insert_rows(crypto_db.table_name, spread_data)
        # wait for set amount to time
        time.sleep(query_interval)
