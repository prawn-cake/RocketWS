![RocketWsIcon](https://www.dropbox.com/s/rkhtagviyjf1bvp/rocket_icon.png?dl=1) RocketWS
====================================================================================================
[![Stories in Ready](https://badge.waffle.io/prawn-cake/RocketWS.png?label=ready&title=Ready)](https://waffle.io/prawn-cake/RocketWS)
[![Build Status](https://travis-ci.org/prawn-cake/RocketWS.svg)](https://travis-ci.org/prawn-cake/RocketWS)
[![Coverage Status](https://img.shields.io/coveralls/prawn-cake/RocketWS.svg)](https://coveralls.io/r/prawn-cake/RocketWS)

RocketWS is open-sourced WebSockets push server based on gevent-websocket library


Features
---------

* Free easy-use asynchronous standalone WebSockets server, allows to build cutting edge web-applications;
* All interactions are based on [JSON-RPC 2.0 Specification](http://www.jsonrpc.org/specification); 
* Unlimited subscribe channels;
* Can support multiple message sources, default is HTTP;
* Scalable software design;
* Supports command-line interface;
* Flexible deployment schemas (direct, with supervisor, with docker);


Workflow
---------
![RocketWSWorkflow](https://www.dropbox.com/s/nz4krowb760tpho/rocketws_workflow.png?dl=1)


Interactions
------------
Several main types of server interactions are supported:

* WebSockets - is used by browser-like clients;
* MessagesSources - is used by backend applications;
* Command line interface - useful for testing;

Request examples
----------------
All requests must be correspond to [JSON-RPC 2.0 Specification](http://www.jsonrpc.org/specification)

* WebSockets
  * **Subscribe** to channel `chat`:
  `{"id": 0, "jsonrpc": "2.0", "method": "subscribe", "params": {"channel": "chat"}}`
  
  * **Unsubscribe** from channel `chat`:
  `{"id": 0, "jsonrpc": "2.0", "method": "unsubscribe", "params": {"channel": "chat"}}`
  
  * **Send data** to channel `chat`:
  `{"id": 0, "jsonrpc": "2.0", "method": "send_data", "params": {"channel": "chat", "data": {"message": "hola!"}}}`
    

* MessagesSources
  * **Emit** message for all subscribers for channel `chat`: `{"id": 0, "jsonrpc": "2.0", "method": "emit", "params": {"channel": "chat", "data": {"message": "hola!"}}}`
  * **Notify all** subscribers (some system messages): `{"id": 0, "jsonrpc": "2.0", "method": "notify_all", "params": {"data": {"message": "Broadcase system message"}}}`


Command line interface (RocketWS shell)
-----------------------

Command line interface is console for WebSockets clients interaction, this feature emulate MessagesSource connector with console.
So you will be able to emulate backend client to send messages to websockets clients

* Run shell: `make shell`
* Type `help` for more information

**NOTE:** For remote shell you need to ensure that port for `MESSAGES_SOURCE` is available on a server.

Run remote shell: `python manage.py shell --ms-conn http://rocketws.domain.com:80/shell`


Configuration
--------------

Common and recommended settings are already predefined.
Otherwise you can configure it with `manage.py` command. See more information in Management section.

There are several parameters:

* `MESSAGES_SOURCE` -- control MessagesSource parameters for backend interaction. Default port: *59999* 

* `WEBSOCKETS` -- control WebSockets server parameters for clients interaction. Default port: *58000*

* `LOGGING` -- logging configuration


Management
----------
Main application management available with `manage.py` script.

Commands:

* `runserver` - Start RocketWS
* `tests`     - Run tests  
* `shell`     - Run command-line interface

Options:

* `--ws-conn`  - WebSockets server connection options. Example: `--ws-conn 0.0.0.0:58000` or `--ws-conn :58000`. Options for `runserver` command. 
* `--ms-conn`  - MessagesSource connection options. Example: `--ms-conn 0.0.0.0:59999`. Options for `runserver` and `shell` command.



Installation/Deployment
------------------------
### Dependencies
Make sure that you have `libevent-2.0-5` or `libev4` in your system.

### Develop way

* Clone repo: `git clone https://github.com/prawn-cake/RocketWS.git {dir}`
* Run it: `make run`


### Supervisor way

* Clone repo: `git clone https://github.com/prawn-cake/RocketWS.git {dir}`
* Install supervisor: `sudo aptitude install supervisor` (Debian-way)
* Add supervisor config: `sudo vim /etc/supervisor/conf.d/rocketws.conf`

**NOTE:** For production using need to create log directory `/var/log/rocketws` 

```

    [program:rocketws]
    command={dir}/.env/bin/python {dir}/manage.py runserver --ws-conn 0.0.0.0:58000 --ms-conn 0.0.0.0:59999
    autostart=false
    autorestart=true
    user={str:user}
    stdout_logfile=/{path_to_log_dir}/rocketws.log
    
```

* Update supervisor configurations: `sudo supervisorctl reread && sudo supervisorctl update`
* Start RocketWS with: `sudo supervisorctl restart rocketws`


### Docker way
**NOTE:** Docker works fine (without any workarounds) only under x86_64 arch

* [Install docker](https://docs.docker.com/installation/ubuntulinux/)
* Add `DOCKER_OPTS="--ip 127.0.0.1"` to `/etc/default/docker` (or `/etc/sysconfig/docker` for RHEL) and restart the docker service

**NOTE:** use `sudo` with the following commands or add your user to a docker group

* `docker pull prawncake/rocketws`
* `docker run --name rocketws -it -p 58000:58000 -p 59999:59999 prawncake/rocketws /bin/bash`
* You will be attached to the container, run application in the background with `make run_bg`
* Detach from the container with `Ctrl+p Ctrl+q`

*NOTE:* For some reasons docket can't run `nohup`, `disown`, `&` shell instructions from command line or within Makefile commands

Container will be started and then you can connect to `tcp:58000` for WebSockets and to `tcp:59999` for MessagesSource

#### Brief docker howto

* Attach to `rocketws` container: `docker attach rocketws`
* Detach from the container: `Ctrl+p Ctrl+q`
* List of running containers: `docker ps -a`
* Stop/start/remove container: `docker {start|stop|rm} rocketws`

*NOTE:* We use exact name because we set it up in run command as a `--name` option otherwise we must use container ID

* [More command-line docs](https://docs.docker.com/reference/commandline/cli/)


### Chef way

* Just use [rocketws chef cookbook](https://github.com/prawn-cake/rocketws-cookbook)


### Nginx proxy
Useful for production

* [Nginx websocket proxying article](http://nginx.org/en/docs/http/websocket.html)

* Add custom `proxy_read_timeout`, because it equals 60s by default, `proxy_read_timeout 604800;  # one-week timeout;` for example

**NOTE:** If you use `https` with **self-signatured** certificate you must use `wss://` schema firstly and before connect you must first visit a regular html page with that certificate so you can accept it.