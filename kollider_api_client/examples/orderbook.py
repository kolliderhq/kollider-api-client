from kollider_api_client.ws import KolliderWsClient

BASE_URL = "wss://api.kollider.xyz/v1/ws/"

if __name__ in "__main__":
    import time
    ws_client = KolliderWsClient()

    ws_client.connect(BASE_URL)
    time.sleep(1)
    ws_client.sub_orderbook_l2("BTCUSD.PERP")
    while True:
        time.sleep(1)
        orderbook = ws_client.orderbooks.get("BTCUSD.PERP")
        if orderbook:
            print(list(orderbook.bids))
            print(list(orderbook.asks))