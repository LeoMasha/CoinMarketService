import datetime
import json
import operator
import requests
import threading
import websocket


class Binance:
    def __name__(self):
        return 'Binance'

    def symbols(self):
        result = list()
        try:
            r = requests.get(
                url='https://api.binance.com/api/v1/exchangeInfo'
            ).json()
            if r is not None and 'symbols' in r:
                for m in r['symbols']:
                    result.append([m['baseAsset'].upper(), m['quoteAsset'].upper()])
        except json.JSONDecodeError:
            pass
        return result

    def ws(self, base, quote, callback):
        def on_message(_, msg):
            try:
                msg = json.loads(msg)
                bids = [(float(bid[0]), float(bid[1])) for bid in msg['bids']]
                bids.sort(key=operator.itemgetter(0), reverse=True)
                asks = [(float(ask[0]), float(ask[1])) for ask in msg['asks']]
                asks.sort(key=operator.itemgetter(0), reverse=False)
                callback({
                    'symbol': 'binance_{0}_{1}'.format(base, quote),
                    'timestamp': datetime.datetime.now().timestamp(),
                    'depth': {
                        'bids': bids,
                        'asks': asks
                    }
                })
            except (json.JSONDecodeError, TypeError, IOError):
                pass

        w = websocket.WebSocketApp('wss://stream.binance.com:9443/ws/{0}{1}@depth5'.format(base.lower(), quote.lower()) + '', on_message=on_message)
        self.thread = threading.Thread(target=w.run_forever, daemon=True, kwargs={
            'sslopt': {
                "cert_reqs": False
            }
        }).start()
        return self.thread


if __name__ == '__main__':
    def callback(msg):
        print(msg)

    ex = Binance()
    print(ex.__name__())
    print(ex.symbols())
    ex.ws('ETH', 'BTC', callback)
    while True:
        pass