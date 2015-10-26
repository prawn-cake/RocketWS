# -*- coding: utf-8 -*-


TRANSPORT = {
    'ADAPTER': 'http',
    'HOST': '0.0.0.0',
    'PORT': 59999,
    'USERNAME': 'abc',
    'PASSWORD': '',
}

WEBSOCKETS = {
    'HOST': '0.0.0.0',
    'PORT': 58000,
    'DEBUG': True,
    'LOCATION': '/'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s: %(name)s: %(message)s'
        }
    },
    'filters': {},
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },

    },
    'loggers': {
        # 'myproject.custom': {
        #     'handlers': ['console', 'mail_admins'],
        #     'level': 'INFO',
        #     'filters': ['special']
        # }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}