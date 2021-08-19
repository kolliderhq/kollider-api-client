import requests

class KolliderRestClient(object):

	def __init__(self, base_url, api_key=None):
		self.base_url = base_url
		self.api_key = api_key

	def __authorization_header(self):
		if not self.api_key:
			raise Exception("No api key found!")
		return {
			"Authorization": self.api_key,
		}
	
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

	def get_funding_rates(self):
		''' 
		Returns current funding rates for every perp.
		'''
		endpoint = self.base_url + "market/funding_rates"
		try:
			resp = requests.get(endpoint)
			return resp.json()
		except Exception as e:
			print(e)

	# Private Method (Need valid api key)
	def get_open_orders(self):
		'''Returns all currently open limit orders of a user.'''
		endpoint = self.base_url + "orders/open"
		try:
			resp = requests.get(endpoint, headers=self.__authorization_header())
			return resp.json()
		except Exception as e:
			print(e)

	def get_positions(self):
		'''Returns all active positions of a user.'''
		endpoint = self.base_url + "positions"
		try:
			resp = requests.get(endpoint, headers=self.__authorization_header())
			return resp.json()
		except Exception as e:
			print(e)

	def make_deposit(self, amount, network="Ln"):
		'''Requests a deposit'''
		endpoint = self.base_url + "wallet/deposit"
		body = {
			"type": network,
			"amount": amount
		}
		try:
			resp = requests.post(endpoint, json=body, headers=self.__authorization_header())
			return resp.json()
		except Exception as e:
			print(e)

	def make_withdrawal(self, amount, network="Ln", payment_request=None):
		'''Requests withdrawal'''
		endpoint = self.base_url + "wallet/withdrawal"
		body = {
			"type": network,
			"amount": amount
		}
		if network == "Ln":
			if not payment_request:
				raise Exception("Need to specify a payment request on Lightning Network.")
			body["payment_request"] = payment_request
		try:
			resp = requests.post(endpoint, json=body, headers=self.__authorization_header())
			return resp.json()
		except Exception as e:
			print(e)

	def place_order(self, order):
		endpoint = self.base_url + "orders"
		try:
			resp = requests.post(endpoint, json=order, headers=self.__authorization_header())
			print(resp)
			return resp.json()
		except Exception as e:
			print(e)

	def cancel_order(self, order_id, symbol):
		endpoint = self.base_url + "orders"
		params = "?order_id={}&symbol={}".format(order_id, symbol)
		endpoint += params
		try:
			resp = requests.delete(endpoint, headers=self.__authorization_header())
			print(resp)
			return resp.json()
		except Exception as e:
			print(e)
