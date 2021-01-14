import numpy as np
import json

symbol, id, side, size, price = 0, 1, 2, 3, 4


# Subscribe or unsubscribe to the an stream
def subscribe_to_stream(ws, sub, data, instrument):
    if sub:
        ws.send(json.dumps({"op": "subscribe", "args": [data + ":" + instrument]}))
    else:
        ws.send(json.dumps({"op": "unsubscribe", "args": [data + ":" + instrument]}))


# Test if everything loaded up properly
# First Welcome response and then successful subscription response
def connectionCheck(ws, subscription, instrument):
    everythingOkay = True

    # First response should be a welcome response
    response = json.loads(ws.recv())
    print(response)
    welcome = "Welcome to the BitMEX Realtime API."
    try:
        if not (response["info"] == welcome):
            everythingOkay = False
    except:
        pass

    # second response should be a success response
    response = json.loads(ws.recv())
    print(response)
    try:
        if not (response["success"] == True and response["subscribe"] == subscription + ":" + instrument):
            everythingOkay = False
    except:
        pass

    return everythingOkay


# Get Orderbook (currently orderBookL2_25) in an array bid and array ask with symbol, id, side, size, price each
def get_orderbook(response):
    bid = np.array([])
    ask = np.array([])

    if response["table"] == "orderBookL2_25":
        if response["action"] == "partial":
            data = response["data"]

    for row in data:
        if row["side"] == "Buy":
            if len(np.shape(bid)) == 1 and np.shape(bid)[0] == 0:
                bid = np.append(bid, np.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]]))
            else:
                bid = np.vstack((bid, np.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))

        else:
            if len(np.shape(ask)) == 1 and np.shape(ask)[0] == 0:
                ask = np.append(ask, np.array([row["symbol"], row["id"], row["side"], row["size"], row["price"]]))
            else:
                ask = np.vstack((ask, np.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))

    # Max bid is in bid[0], and Min ask in ask[0]
    bid = bid[np.argsort(bid[:, price])[::-1]]
    ask = ask[np.argsort(ask[:, price])]

    return bid, ask


def update_orderbook_entry(response, bid, ask):
    data = response["data"]
    for row in data:
        rowDictKeys = list(row.keys())
        if row["side"] == "Buy":
            index = np.where(bid[:, id] == str(row["id"]))
            if "size" in rowDictKeys:
                bid[index, size] = row["size"]
        else:
            index = np.where(ask[:, id] == str(row["id"]))
            if "size" in rowDictKeys:
                ask[index, size] = row["size"]
    return bid, ask


def delete_orderbook_entry(response, bid, ask):
    data = response["data"]
    for row in data:
        if row["side"] == "Buy":
            index = np.where(bid[:, id] == str(row["id"]))
            bid = np.delete(bid, index, axis=0)
        else:
            index = np.where(ask[:, id] == str(row["id"]))
            ask = np.delete(ask, index, axis=0)
    return bid, ask


def insert_orderbook_entry(response, bid, ask):
    data = response["data"]
    for row in data:
        if row["side"] == "Buy":
            bid = np.vstack((bid, np.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))
        else:
            ask = np.vstack((ask, np.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))
    return bid, ask
