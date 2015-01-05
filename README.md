![RocketWsIcon](https://cdn2.iconfinder.com/data/icons/windows-8-metro-style/48/rocket.png) RocketWS
====================================================================================================

RocketWS is open-sourced WebSockets push server based on gevent-websocket library


Features
---------

* Free easy-use asynchronous standalone WebSockets server, allows to build cutting edge web-applications;
* All interactions are based on [JSON-RPC 2.0 Specification](http://www.jsonrpc.org/specification); 
* Unlimited subscribe channels;
* Multiple message sources. RabbitMQ, ZeroMQ, own HTTP API connectors are built-in, just set up it; **[in develop]**
* Supports command-line interface; **[in develop]**


Interactions
-----------
Two main types of server interactions are supported:

* WebSockets - is used by browser-like clients;
* MessagesSources - is used by backend applications;

