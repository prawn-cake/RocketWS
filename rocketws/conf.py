# -*- coding: utf-8 -*-
import importlib
from rocketws.exceptions import ImproperlyConfigured


_settings = None


def configure_settings(settings_path):
    """Configure application settings

    :param settings_path: string value, for example: 'rocketws.settings.test'
    :raise ImproperlyConfigured:
    """
    global _settings
    try:
        pkg = importlib.import_module(settings_path)
    except ImportError:
        raise ImproperlyConfigured(
            'No such settings module: {}'.format(settings_path))
    else:
        _settings = pkg


def get_settings(path=None):
    if path is None:
        if not _settings:
            configure_settings('rocketws.settings.default')
    else:
        configure_settings(path)
    return _settings


__all__ = ['configure_settings', 'get_settings']