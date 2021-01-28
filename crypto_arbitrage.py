#!/usr/bin/env python3

import requests
from pycoingecko import CoinGeckoAPI
import operator
import random


def get_coin_pair_data(exclude=[], include_exchanges=[], include_coins=[]):
    cg = CoinGeckoAPI()
    coins = []
    if(include_coins == []):
        coins = cg.get_coins_list()
        random.shuffle(coins)
    else:
        coins = include_coins

    print(len(coins))
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
        except:
            continue
    return (coin_data)

# TODO something wrong with spread calculation


def coins_by_spread(coins, min_volume=5000):
    coins_spread = []
    for coin in coins:
        print(coin["name"])
        prices = []
        for m in coin['market data']:
            vol = m['volume']
            if vol >= min_volume:
                prices.append({'price': m['price'], 'market': m['market']})
        if len(prices) > 1:
            max_price = max(list(map(lambda x: x["price"], prices)))
            min_price = min(list(map(lambda x: x["price"], prices)))
            max_market = [x['market']
                          for x in prices if x['price'] == max_price]
            min_market = [x['market']
                          for x in prices if x['price'] == min_price]
            spread = ((max_price - min_price) / min_price) * 100
            coins_spread.append(
                {'name': coin['name'], 'spread': spread, 'max_market': max_market, 'min_market': min_market, 'max_price': max_price, 'min_price': min_price})
    coins_spread.sort(key=operator.itemgetter('spread'))
    return (coins_spread)


def get_coins_with_spread(min_spread=0.01):
    exchanges = ['Bibox',
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
             {'id': 'bitcoin'}
             ]
    print(exchanges)
    coins = get_coin_pair_data(
        include_exchanges=exchanges, include_coins=coins)
    coins = coins_by_spread(coins)
    return (coins)


def main():
    coins_spread = get_coins_with_spread()
    for coin in coins_spread:
        spread = 'spread: ' + str(coin['spread'])[:4] + '%'
        print(coin['name'], spread)
        print(coin)
