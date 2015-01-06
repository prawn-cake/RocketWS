# -*- coding: utf-8 -*-


class ImproperlyConfigured(Exception):

    """RocketWS is somehow improperly configured"""

    pass


class RPCMethodError(Exception):

    """Error might be raised during rpc methods processing"""

    pass