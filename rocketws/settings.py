# -*- coding: utf-8 -*-


MESSAGES_SOURCE = {
    'ADAPTER': 'http',  # Possible values: ['rabbitmq', 'http']
    'HOST': '0.0.0.0',
    'PORT': 59999,
    'USERNAME': 'abc',
    'PASSWORD': '',

    # rabbitmq specific parameters
    'MESSAGE_TTL': 3600,  # for `rabbitmq` adapter, https://www.rabbitmq.com/ttl.html
    'LISTEN_QUEUE': 'rocketws'  # will be auto-declared if not
}


WEBSOCKETS = {
    'HOST': '0.0.0.0',
    'PORT': 58000,
    'DEBUG': True,
    'LOCATION': '/'
}
