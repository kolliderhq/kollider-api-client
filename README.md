## 🤖 Kollider API Client written in Python 🤖

Kollider offers both a REST api as well as a Websocket api. Both apis provide the same basic accessor methods, however, account specific events are only available through websockets and historical data is only available through rest. We are working towards making them identical.

You can install the client package in your environment by running.

```
cd kollider-api-client
pip install -e .
```
Example usage for subscribing to the .BTCUSD index pice:
```python
from kollider_api_client.ws import KolliderWsClient
import json

BASE_URL = "wss://api.kollider.xyz/v1/ws/"

class WSClient(KolliderWsClient):

    ws_is_ready = False

    def on_message(self, _ctx, msg):
        msg = json.loads(msg)
        t = msg["type"]
        data = msg["data"]

        if t == "index_values":
            print(data)

    def on_open(self, event):
        self.ws_is_ready = True


if __name__ in "__main__":

    ws_client = WSClient()
    ws_client.connect(base_url=BASE_URL)

    while not ws_client.ws_is_ready:
        pass

    ws_client.sub_index_price([".BTCUSD"])

    while True:
        pass

```

<a href="https://docs-api.kollider.xyz"> 📕 The docs can be found here.</a>

<code>TODO:</code> <br>
- [ ] Error Handling <br>
- [ ] Add missing methods (see docs)

**Note**: Not all methods have been implemented yet. This is very much a WIP. 
