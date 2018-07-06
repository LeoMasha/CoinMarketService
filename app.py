import argparse
import json
from tornado import web, ioloop, websocket
from vquantutils import log
from .exchange.binance import Binance
from .exchange.huobi import Huobi
from .exchange.okex import OKEx

PORT = 9110
EXCHANGES = [Binance(), Huobi(), OKEx()]

class WebSocketHandler(websocket.WebSocketHandler):
    clients = set()
    ticker = None

    def __init__(self, application, request, **kwargs):
        if WebSocketHandler.ticker is None:
            WebSocketHandler.ticker = True
            for ex in EXCHANGES:
                for symbol in ex.symbols():
                    ex.ws(symbol[0], symbol[1], self.send_updates)
            log('Ticker is started.')
        else:
            log('Ticker is already started.', color='yellow')
        websocket.WebSocketHandler.__init__(self, application, request, **kwargs)

    def open(self):
        if self not in WebSocketHandler.clients:
            WebSocketHandler.clients.add(self)
            log('Client connected.')

    def on_close(self):
        if self in WebSocketHandler.clients:
            WebSocketHandler.clients.remove(self)
            log('Client disconnected.')

    def send_updates(self, message):
        for client in WebSocketHandler.clients:
            try:
                client.write_message(json.dumps(message))
            except Exception as exp:
                log('Cannot send message to client: ' + str(client), 'red')
                print(exp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', metavar='PORT', type=int, default=PORT,
                        help='listening port, default: {0}'.format(PORT))
    args, _ = parser.parse_known_args()
    PORT = args.p
    web.Application([(r'/', WebSocketHandler)]).listen(PORT)  # ssl_options={"certfile": os.path.join("server.pem"),"keyfile": os.path.join("server.key"),}
    log('Server is listening on port {0}.'.format(PORT))
    ioloop.IOLoop.current().start()
