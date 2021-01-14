import numpy as np
import json
import websocket
import BitMEXfunctions

ws = websocket.create_connection("wss://www.bitmex.com/realtime")
symbol, id, side, size, price = 0, 1, 2, 3, 4

BitMEXfunctions.subscribe_to_stream(ws, True, "orderBookL2_25", "XBTUSD")
successfullyConnected = BitMEXfunctions.connectionCheck(ws, "orderBookL2_25", "XBTUSD")

if successfullyConnected:
    print("-Successfully connected-")
    response = json.loads(ws.recv())
    bid, ask = BitMEXfunctions.get_orderbook(response)

    while True:
    #for i in range(100):
        response = json.loads(ws.recv())
        if response["table"] == "orderBookL2_25":
            if response["action"] == "update":
                bid, ask = BitMEXfunctions.update_orderbook_entry(response, bid, ask)
            elif response["action"] == "delete":
                bid, ask = BitMEXfunctions.delete_orderbook_entry(response, bid, ask)
            elif response["action"] == "insert":
                bid, ask = BitMEXfunctions.insert_orderbook_entry(response, bid, ask)

            # Max bid is in bid[0], and Min ask in ask[0]
            bid = bid[np.argsort(bid[:, price])[::-1]]
            ask = ask[np.argsort(ask[:, price])]

        print(bid[0][price], ask[0][price])
    ws.close()

else:
    print("Not successfully connected - closing Websocket and ending program")
    ws.close()
