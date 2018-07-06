import json
import operator
import threading
import websocket


class OKEx:
    @classmethod
    def __name__(self):
        return 'OKEx'

    def symbols(self):
        return [
            ['LTC', 'BTC'], ['ETH', 'BTC'], ['ETC', 'BTC'], ['BCH', 'BTC'],
            ['BTC', 'USDT'], ['ETH', 'USDT'], ['LTC', 'USDT'], ['ETC', 'USDT'], ['BCH', 'USDT'], ['EOS', 'USDT'],
            ['ETC', 'ETH'], ['BT1', 'BTC'], ['BT2', 'BTC'], ['BTG', 'BTC'], ['QTUM', 'BTC'], ['HSR', 'BTC'], ['NEO', 'BTC'], ['GAS', 'BTC'],
            ['QTUM', 'USDT'], ['HSR', 'USDT'], ['NEO', 'USDT'], ['GAS', 'USDT']
        ]

    def ws(self, base, quote, callback):
        def on_message(_, msg):
            try:
                msg = json.loads(msg)[0]
                if 'data' in msg and 'timestamp' in msg['data']:
                    r = msg['data']
                    bids = [(float(bid[0]), float(bid[1])) for bid in r['bids']]
                    bids.sort(key=operator.itemgetter(0), reverse=True)
                    asks = [(float(ask[0]), float(ask[1])) for ask in r['asks']]
                    asks.sort(key=operator.itemgetter(0), reverse=False)
                    callback({
                        'symbol': 'okex_{0}_{1}'.format(base.lower(), quote.lower()),
                        'timestamp': r['timestamp'] / 1000,
                        'depth': {
                            'bids': bids,
                            'asks': asks,
                        }
                    })
            except (json.JSONDecodeError, TypeError, IOError):
                pass

        def on_open(ww):
            ww.send(json.dumps({
                'event': 'addChannel',
                'channel': 'ok_sub_spot_{0}_{1}_depth_5'.format(base.lower(), quote.lower())
            }))

        w = websocket.WebSocketApp('wss://real.okcoin.cn:10440/websocket/okcoinapi', on_message=on_message, on_open=on_open)
        self.thread = threading.Thread(target=w.run_forever, daemon=True).start()
        return self.thread

if __name__ == '__main__':
    def callback(msg):
        print(msg)

    ex = OKEx()
    print(ex.__name__())
    print(ex.symbols())
    ex.ws('ETH', 'BTC', callback)
    while True:
        pass