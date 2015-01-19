# -*- coding: utf-8 -*-

from .default import *


LOGGING['root']['handlers'] = ['console', 'file']

LOGGING['handlers']['file'] = {
    'level': 'DEBUG',
    'class': 'logging.handlers.WatchedFileHandler',
    'filename': '/var/log/rocketws/rocketws.log',
    'formatter': 'verbose',
    'encoding': 'utf-8'
}