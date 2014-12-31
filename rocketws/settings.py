# -*- coding: utf-8 -*-


MESSAGES_SOURCE = {
    'ADAPTER': 'rabbitmq',  # Possible values: ['rabbitmq', 'http']
    'HOST': '',
    'PORT': 9999,
    'USERNAME': '',
    'PASSWORD': '',

    # rabbitmq specific parameters
    'MESSAGE_TTL': 3600,  # for `rabbitmq` adapter
    'LISTEN_QUEUE': 'rocketws'
}


WEBSOCKETS = {
    'HOST': '0.0.0.0',
    'PORT': 8000,
    'DEBUG': True
}
