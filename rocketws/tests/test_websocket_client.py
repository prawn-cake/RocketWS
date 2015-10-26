# -*- coding: utf-8 -*-

"""JavaScript websocket-like API example"""

import json
import sys
from datetime import datetime

import websocket
import multiprocessing
import time
import random


class Client(multiprocessing.Process):
    def __init__(self, name, conn_string):
        super(Client, self).__init__()
        self.name = name
        self.conn_string = conn_string
        self.ws = None

    def on_message(self, ws, message):
        print("{}:on_message: {}".format(self, message))

    def on_error(self, ws, error):
        print("{}:on_error: {}".format(self, error))

    def on_close(self, ws):
        print("{}:on_close".format(self))

    def on_open(self, ws):
        print("{}:on_open".format(self))

        if not self.ws:
            self.ws = ws

        # subscribe on open
        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "subscribe",
            "params": {"channel": "client:{}".format(self.name)}
        }
        ws.send(json.dumps(payload))

        while True:
            self.send_data()
            time.sleep(random.randint(1, 15))

    def send_data(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "send_data",
            "params": {
                "channel": "client:{}".format(self.name),
                'data': {'message': 'send data message from {}'.format(self)},
            }
        }

        self.ws.send(json.dumps(payload))
        print("[{}] data is sent".format(datetime.now()))

    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            self.conn_string,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.on_open = self.on_open
        ws.run_forever()

    def __str__(self):
        return "Client({})".format(self.name)

    def __repr__(self):
        return unicode("Client({})".format(self.name))

    def __unicode__(self):
        return unicode("Client({})".format(self.name))


class BackendClient(multiprocessing.Process):
    def run(self):
        pass


if __name__ == "__main__":
    conn_string = sys.argv[1]  # "ws://echo.websocket.org/"
    num_of_clients = int(sys.argv[2])

    jobs = []
    channels = []
    for i in range(num_of_clients):
        client = Client('Client_{}'.format(i + 1), conn_string)
        client.start()
        jobs.append(client)
        channels.append('client:{}'.format(client.name))

    # backend = BackendClient()
    for j in jobs:
        j.join()
