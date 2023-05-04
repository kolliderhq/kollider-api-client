from kollider_api_client.auth import generate_signature
import sys
import websocket
import threading
import ssl
from time import sleep
import json
import copy
from BTrees.OOBTree import OOBTree

from future.standard_library import hooks
with hooks():
    from urllib.parse import urlparse, urlunparse

BASE_URL = "wss://api.kollider.xyz/v1/ws/"

POSITION_STATE = "position_states"
INDEX_VALUE = "index_values"
FAIR_PRICE = "mark_prices"
ACCOUNT_STATE = "account_state"
TICKER = "ticker"
AUTHENTICATE = "authenticate"
USER_POSITIONS = "positions"
USER_ACCOUNTS = "balances"
OPEN_ORDERS = "open_orders"
RECEIVED = "received"
LEVEL_2_STATE = "level2state"
DONE = "done"
OPEN = "open"
TRADABLE_SYMBOLS = "tradable_symbols"
ERROR = "error"
WHOAMI = "whoami"
ORDER_REJECTION = "order_rejection"

class Orderbook(object):

    def __init__(self):
        self.bids = copy.copy(OOBTree())
        self.asks = copy.copy(OOBTree())
        self.level = "l2"

class KolliderWsClient(object):
    _connection_attempt = 0
    _max_connection_attempts = 5
    is_open = threading.Event()
    wst = None

    def connect(self, base_url=None, api_key=None, api_secret=None, api_passphrase=None, jwt=None):
        '''Connect to the websockets'''

        print("----------- CONNECTING TO WS --------------")

        if not base_url:
            base_url = BASE_URL

        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.jwt = jwt
        self.orderbooks = {}
        self.last_orderbook_seq = None

        self.is_authenticated = False
        self.is_connecting = threading.Event()
        self.__connect(base_url)

    def __connect(self, base_url):
        '''Connect to the websocket in a thread.'''
        if self._connection_attempt == self._max_connection_attempts:
            print("Max connection attempt limit reached")
            sys.exit(1)

        if self._connection_attempt > 0:
            sleep(1)

        self._connection_attempt += 1

        print("Starting thread")

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.ws = websocket.WebSocketApp(base_url,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_open=self.on_open,
                                         on_error=self.on_error,
                                         on_pong=self.on_pong,
                                         )
        self.is_connecting.set()
        self.wst = threading.Thread(
            target=lambda: self.ws.run_forever(ping_interval=10, ping_timeout=5, 
            sslopt={"cert_reqs": ssl.CERT_NONE,
                   "check_hostname": False,
                   "ssl_version": ssl.PROTOCOL_TLSv1}
                                               ))
        self.wst.daemon = True
        self.wst.start()

        print("Started WS thread")
        self.is_connecting.clear()
        self.is_open.set()

    def reconnect(self, base_url):
        self.is_authenticated = False
        self.is_connecting = threading.Event()
        self.__connect(base_url)

    def set_jwt(self, jwt):
        self.jwt = jwt

    def auth(self):
        (timestamp, signature) = generate_signature(self.api_secret, "authentication")
        msg = {
            "type": "authenticate",
            "token": self.api_key,
            "timestamp": str(timestamp),
            "signature": signature,
            "passphrase": self.api_passphrase,
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def jwt_auth(self):
        msg = {
            "type": "authenticate",
            "token": self.jwt,
        }
        json_msg = json.dumps(msg)
        print(json_msg)
        self.ws.send(json_msg)

    def sub_ticker(self, symbols):
        msg = {
            "type": "subscribe",
            "channels": ["ticker"],
            "symbols": symbols,
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def sub_position_states(self):
        msg = {
            "type": "subscribe",
            "channels": ["position_states"],
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def sub_orderbook_l2(self, symbol):
        msg = {
            "type": "subscribe",
            "channels": ["orderbook_level2"],
            "symbols": [symbol]
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def sub_mark_price(self, symbols=["BTCUSD.PERP"]):
        msg = {
            "type": "subscribe",
            "channels": ["mark_prices"],
            "symbols": symbols
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def sub_index_price(self, symbols=[".BTCUSD"]):
        msg = {
            "type": "subscribe",
            "channels": ["index_values"],
            "symbols": symbols
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_tradable_symbols(self):
        msg = {
            "type": "fetch_tradable_symbols",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_positions(self):
        msg = {
            "type": "fetch_positions",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_open_orders(self):
        msg = {
            "type": "fetch_open_orders",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_balances(self):
        msg = {
            "type": "fetch_balances",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_orderbook(self, symbol):
        msg = {
            "type": "fetch_orderbook",
            "timestamp": 0,
            "symbol": symbol,
            "res": "Level2"
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_symbols(self):
        msg = {
            "type": "fetch_tradable_symbols",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def fetch_ticker(self, symbol):
        msg = {
            "type": "fetch_ticker",
            "symbol": symbol,
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def who_am_i(self):
        msg = {
            "type": "whoami",
        }
        json_msg = json.dumps(msg)
        self.ws.send(json_msg)

    def place_order(self, order):
        order["type"] = "order"
        self.ws.send(json.dumps(order))

    def cancel_order(self, cancel_order):
        cancel_order["type"] = "cancel_order"
        self.ws.send(json.dumps(cancel_order))

    def cancel_all(self, cancel_all):
        cancel_all["type"] = "cancel_all"
        self.ws.send(json.dumps(cancel_all))

    def withdrawal_request(self, withrawal_request):
        withrawal_request["type"] = "withdrawal_request"
        self.ws.send(json.dumps(withrawal_request))

    def exit(self):
        sys.exit(1)

    def has_fetched_initial_data(self):
        return self.has_fetched_symbols and self.has_fetched_whoami

    def on_pong(self, _arg1, _arg2):
        print("------------------- RECEIVED PONG -----------------")

    def on_ping(self):
        print("-------------------- RECEIVED PING ----------------")

    def on_close(self, _event, _event2, _event3):
        print("------------------- CLOSE WS -------------------")
        self.is_open.clear()

    def on_open(self, _event):
        '''This is where all the initialisation logic should be. If you don't subscribe to anything
        or don't authenticate to the session the WS will kick you out automatically after 10s.'''
        print("------------------- OPEN WS -------------------")
        if self.api_key and self.api_passphrase and self.api_secret:
            self.auth()
        if self.jwt:
            print('----------------- JET available ------------------------')
            self.jwt_auth()

    def on_error(self, exception_obj, something_else):
        print("------------------- ERROR WS -------------------")
        print("{}".format(something_else))
        self.is_open.clear()

    def on_message(self, _msg, msg):
        msg = json.loads(msg)
        t = msg["type"]
        data = msg["data"]
        if t == AUTHENTICATE:
            if data["message"] == "success":
                print("Authenticated Successfully!")
                self.is_authenticated = True
            else:
                print("Auth Unsuccessful: {}".format(data))
                self.is_authenticated = False
                self.__reset()

        elif t == ERROR:
            print("{}".format(msg["message"]))

        elif t == TICKER:
	        print(data)

        elif t == INDEX_VALUE:
	        print(data)

        elif t == USER_POSITIONS:
            print("Received Positions")
            print(data)

        elif t == OPEN_ORDERS:
            print("Received Open Orders")
            print(data)

        elif t == USER_ACCOUNTS:
            print("Received User Accounts")
            print(data)

        elif t == WHOAMI:
            print("Received WHOAMI")
            print(data)

        elif t == RECEIVED:
            print("Received Order Received.")
            print(data)

        elif t == DONE:
            print("Received Order Done.")
            print(data)

        elif t == OPEN:
            print("Received Order Open.")
            print(data)

        elif t == FAIR_PRICE:
            print("Received Fair Price")
            print(data)

        elif t == TRADABLE_SYMBOLS:
            print("Received Tradable Symbols.")
            print(data)

        elif t == POSITION_STATE:
            print("Received Position State.")
            print(data)

        elif t == ORDER_REJECTION:
            print("Received Order Rejection.")
            print(data)

        elif t == LEVEL_2_STATE:
            if self.last_orderbook_seq and self.last_orderbook_seq != data["seq_number"] - 1:
                print("Seq number missmatch")
                # Fetching orderbook state.
                self.fetch_orderbook(data["symbol"])
            else:
                self.last_orderbook_seq = data["seq_number"]
            if data["update_type"] == "snapshot":
                ob = copy.copy(Orderbook())
                for key, value in data["bids"].items():
                    ob.bids[int(key)] = value

                for key, value in data["asks"].items():
                    ob.asks[int(key)] = value

                if self.orderbooks.get(data["symbol"]) is not None:
                    del self.orderbooks[data["symbol"]]
                self.orderbooks[data["symbol"]] = ob
            else:
                bids = data["bids"]
                asks = data["asks"]
                orderbook = self.orderbooks.get(data["symbol"])
                if not orderbook:
                    return
                if bids:
                    for price, quantity in bids.items():
                        if quantity == 0:
                            del orderbook.bids[int(price)]
                        else:
                            orderbook.bids[int(price)] = quantity
                if asks:
                    for price, quantity in asks.items():
                        if quantity == 0:
                            del orderbook.asks[int(price)]
                        else:
                            orderbook.asks[int(price)] = quantity

        else:
            print("Unhandled type: {}".format(msg))

    def __reset(self):
        self.exited = False
        self._error = None
        self.is_open.clear()

if __name__ in "__main__":
    import time
    ws_client = KolliderWsClient()

    ws_client.connect(BASE_URL)
    time.sleep(1)
    ws_client.fetch_orderbook("BTCUSD.PERP")
    while True:
        time.sleep(1)
