# -*- coding: utf-8 -*-
import argparse
import sys
import urlparse


class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.exit(2)


if __name__ == '__main__':
    parser = DefaultHelpParser(description='RocketWS management interface')
    parser.add_argument(
        'method',
        help='Execute `method_name`',
        type=str,
        choices=['runserver', 'tests', 'shell']
    )

    # parser.add_argument('--log', help='Set log path', type=str)

    parser.add_argument(
        '--ws-conn',
        help='Set WebSockets server host and port in format 0.0.0.0:58000',
        type=str
    )
    parser.add_argument(
        '--transport',
        help='Set MessagesSource server host and port in format 0.0.0.0:59000',
        type=str
    )

    args = parser.parse_args()

    from rocketws import settings

    if args.method == 'runserver':
        from rocketws.server import run_server

        ws_host, ws_port = None, None
        transport_host, transport_port = None, None

        if args.ws_conn:
            ws_host, ws_port = args.ws_conn.split(':')
            try:
                ws_port = int(ws_port)
            except ValueError:
                print('\nERROR: Wrong WebSockets server port value: '
                      '{}'.format(ws_port))
                sys.exit(99)
            else:
                settings.WEBSOCKETS['HOST'] = ws_host
                settings.WEBSOCKETS['PORT'] = ws_port
        if args.transport:
            transport_host, transport_port = args.transport.split(':')
            try:
                transport_port = int(transport_port)
            except ValueError:
                print('\nERROR: Wrong transport port value: '
                      '{}'.format(transport_port))
                sys.exit(99)
            else:
                settings.TRANSPORT['HOST'] = transport_host
                settings.TRANSPORT['PORT'] = transport_port

        run_server(ws_host=ws_host,
                   ws_port=ws_port,
                   transport_host=transport_host,
                   transport_port=transport_port)
    elif args.method == 'tests':
        import unittest
        unittest.main(module='rocketws.tests', argv=sys.argv[:1], verbosity=2)
    elif args.method == 'shell':
        from rocketws.shell import RocketWSShell

        conn_url = None
        if args.transport:
            url = urlparse.urlparse(args.transport)
            transport_host, transport_port = '', ''
            if url.scheme:
                conn_url = url.geturl()
            else:
                conn_url = 'http://' + url.path

        RocketWSShell(conn_url).cmdloop()
    else:
        parser.print_help()
