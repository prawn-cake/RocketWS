![RocketWsIcon](https://cdn2.iconfinder.com/data/icons/windows-8-metro-style/48/rocket.png) RocketWS
====================================================================================================
[![Stories in Ready](https://badge.waffle.io/prawn-cake/RocketWS.png?label=ready&title=Ready)](https://waffle.io/prawn-cake/RocketWS)
[![Build Status](https://travis-ci.org/prawn-cake/RocketWS.svg)](https://travis-ci.org/prawn-cake/RocketWS)

RocketWS is open-sourced WebSockets push server based on gevent-websocket library


Features
---------

* Free easy-use asynchronous standalone WebSockets server, allows to build cutting edge web-applications;
* All interactions are based on [JSON-RPC 2.0 Specification](http://www.jsonrpc.org/specification); 
* Unlimited subscribe channels;
* Multiple message sources. RabbitMQ, ZeroMQ, own HTTP API connectors are built-in, just set up it; **[in develop]**
* Scalable software design;
* Supports command-line interface; **[in develop]**


Workflow
---------
![RocketWSWorkflow](https://www.dropbox.com/s/nz4krowb760tpho/rocketws_workflow.png?dl=1)


Interactions
------------
Two main types of server interactions are supported:

* WebSockets - is used by browser-like clients;
* MessagesSources - is used by backend applications;


Request examples
----------------
All requests must be correspond to [JSON-RPC 2.0 Specification](http://www.jsonrpc.org/specification)

* WebSockets
  * **Subscribe** to channel `chat`:
  ```{"id": 0, "jsonrpc": "2.0", "method": "subscribe", "params": {"channel": "chat"}}```
  
  * **Unsubscribe** from channel `chat`:
  ```{"id": 0, "jsonrpc": "2.0", "method": "unsubscribe", "params": {"channel": "chat"}}```
    

* MessagesSources
  * **Emit** message for all subscribers for channel `chat`: ```{"id": 0, "jsonrpc": "2.0", "method": "emit", "params": {"channel": "chat", "data": {"message": "hola!"}}}```

