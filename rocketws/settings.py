# -*- coding: utf-8 -*-


MESSAGES_SOURCE = {
    'ADAPTER': 'http',  # Possible values: ['rabbitmq', 'http']
    'HOST': '',
    'PORT': 9999,
    'USERNAME': 'abc',
    'PASSWORD': '',

    # rabbitmq specific parameters
    'MESSAGE_TTL': 3600,  # for `rabbitmq` adapter, https://www.rabbitmq.com/ttl.html
    'LISTEN_QUEUE': 'rocketws'  # will be auto-declared if not
}


WEBSOCKETS = {
    'HOST': '0.0.0.0',
    'PORT': 8000,
    'DEBUG': True,
    'LOCATION': '/echo'
}
