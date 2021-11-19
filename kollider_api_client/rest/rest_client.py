import requests
import time
from kollider_api_client.auth import auth_header

BASE_URL = "http://127.0.0.1:8443"
API_KEY = ""
API_SECRET = ""
API_PASSPHRASE = ""

class KolliderRestClient(object):

	def __init__(self, base_url, api_key=None, secret=None, passphrase=None):
		self.base_url = base_url
		self.api_key = api_key
		self.secret = secret
		self.passphrase = passphrase

	def __authorization_header(self, method, path, body=None):
		header = auth_header(self.secret, method, path, body)
		header["k-passphrase"] = self.passphrase
		header["k-api-key"] = self.api_key
		if not self.api_key:
			raise Exception("No api key found!")
		return header
	
	# Public Methods
	def get_tradeable_symbols(self):
		''' Returns all symbols and their specification that are availble to trade.'''
		endpoint = self.base_url + "market/products"
		try:
			resp = requests.get(endpoint)
			return resp.json()
		except Exception as e:
			print(e)

	def get_orderbook(self, symbol, level="Level2"):
		''' 
		Returns the orderbook for a specific symbol. NOTE: Don't long poll this. Use the
		Websockets for any real time state keeping of the Orderbook.
		params:
			symbol: <Product Symbol>
			level: Level2 | Level3
		'''
		endpoint = self.base_url + "market/orderbook?symbol={}&level={}".format(symbol, level)
		try:
			resp = requests.get(endpoint)
			return resp.json()
		except Exception as e:
			print(e)

	def get_ticker(self, symbol):
		''' 
		Returns the ticker for a given symbol
		params:
			symbol: <Product Symbol>
		'''
		endpoint = self.base_url + "market/ticker?symbol={}".format(symbol)
		try:
			resp = requests.get(endpoint)
			return resp.json()
		except Exception as e:
			print(e)

	def get_average_funding_rates(self, start=None, end=None):
		''' 
		Returns current funding rates for every perp.
		'''
		endpoint = self.base_url + "market/average_funding_rates"
		if start is None:
			start = int(time.time() * 1000) - 60 * 60
		if end is None:
			end = int(time.time() * 1000)
		if end < start:
			raise Exception
		endpoint += "?start={}&end={}".format(start, end)
		try:
			resp = requests.get(endpoint)
			return resp.json()
		except Exception as e:
			print(e)

	# Private Method (Need valid api key)
	def get_open_orders(self):
		'''Returns all currently open limit orders of a user.'''
		route = "/orders/open"
		endpoint = self.base_url + route
		try:
			headers = self.__authorization_header("GET", route, None)
			resp = requests.get(endpoint, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def get_positions(self):
		'''Returns all active positions of a user.'''
		route = "/positions"
		endpoint = self.base_url + route
		try:
			headers = self.__authorization_header("GET", route, None)
			resp = requests.get(endpoint, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def make_deposit(self, amount, network="Ln"):
		'''Requests a deposit'''
		route = "/wallet/deposit"
		endpoint = self.base_url + route
		body = {
			"type": network,
			"amount": amount
		}
		try:
			headers = self.__authorization_header("POST", route, body)
			resp = requests.post(endpoint, json=body, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def make_withdrawal(self, amount, network="Ln", payment_request=None):
		'''Requests withdrawal'''
		route = "/wallet/withdrawal"
		endpoint = self.base_url + route
		body = {
			"type": network,
			"amount": amount
		}
		if network == "Ln":
			if not payment_request:
				raise Exception("Need to specify a payment request on Lightning Network.")
			body["payment_request"] = payment_request
		try:
			headers = self.__authorization_header("POST", route, body)
			resp = requests.post(endpoint, json=body, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def change_margin(self, action, symbol, amount):
		'''Requests withdrawal'''
		route = "/change_margin"
		endpoint = self.base_url + route
		body = {
			"amount": amount,
			"action": action,
			"symbol": symbol,
		}
		try:
			headers = self.__authorization_header("POST", route, body)
			resp = requests.post(endpoint, json=body, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def place_order(self, order):
		route = "/orders"
		endpoint = self.base_url + route
		body = order.to_dict()
		try:
			headers = self.__authorization_header("POST", route, body)
			resp = requests.post(endpoint, json=body, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

	def cancel_order(self, order_id, symbol):
		route = "/orders"
		endpoint = self.base_url + route
		params = "?order_id={}&symbol={}".format(order_id, symbol)
		auth_body = {
			"order_id": order_id,
			"symbol": symbol,
		}
		endpoint += params
		try:
			headers = self.__authorization_header("DELETE", route, auth_body)
			resp = requests.delete(endpoint, headers=headers)
			return resp.json()
		except Exception as e:
			print(e)

if "__main__" in __name__:
	cli = KolliderRestClient(BASE_URL, API_KEY, API_SECRET, API_PASSPHRASE)
	resp = cli.change_margin("Add", "BTCUSD.PERP", 100)
	print(resp)