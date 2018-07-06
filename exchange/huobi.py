import gzip
import json
import operator
import requests
import threading
import websocket


class Huobi:
    def __name__(self):
        return 'Huobi'

    def symbols(self):
        result = list()
        try:
            r = requests.get(
                url='https://api.huobi.pro/v1/common/symbols',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
                }
            ).json()
            if r is not None and r['status'] != 'error':
                for m in r['data']:
                    result.append([m['base-currency'].upper(), m['quote-currency'].upper()])
        except json.JSONDecodeError:
            pass
        return result

    def ws(self, base, quote, callback):
        def on_message(ww, msg):
            try:
                msg = json.loads(gzip.decompress(msg).decode('utf-8'))
                if 'ping' in msg:
                    ww.send(json.dumps({
                        'pong': msg['ping']
                    }))
                elif 'tick' in msg:
                    r = msg['tick']
                    bids = [(float(bid[0]), float(bid[1])) for bid in r['bids']]
                    bids.sort(key=operator.itemgetter(0), reverse=True)
                    asks = [(float(ask[0]), float(ask[1])) for ask in r['asks']]
                    asks.sort(key=operator.itemgetter(0), reverse=False)
                    callback({
                        'symbol': 'huobi_{0}_{1}'.format(base.lower(), quote.lower()),
                        'timestamp': r['ts'] / 1000,
                        'depth': {
                            'bids': bids,
                            'asks': asks,
                        }
                    })
            except (json.JSONDecodeError, TypeError, IOError):
                pass

        def on_open(ww):
            ww.send(json.dumps({
                'sub': 'exchange.' + base.lower() + quote.lower() + '.depth.step0',
                'id': 'TD'
            }))

        w = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_message=on_message, on_open=on_open)
        self.thread = threading.Thread(target=w.run_forever, daemon=True).start()
        return self.thread


if __name__ == '__main__':
    def callback(msg):
        print(msg)

    ex = Huobi()
    print(ex.__name__())
    print(ex.symbols())
    ex.ws('ETH', 'BTC', callback)
    while True:
        pass


