# -*- coding: utf-8 -*-
import unittest
import mock
from rocketws.shell import RocketWSShell
from requests import Response

mock_resp = mock.Mock(spec=Response)
mock_resp.status_code = 200


class TestShell(unittest.TestCase):
    @mock.patch('requests.post', return_value=mock_resp)
    @mock.patch('cmd.Cmd.cmdloop')
    def test_shell(self, mock_cmdloop, mock_post):
        shell = RocketWSShell()
        shell.cmdloop()
        self.assertTrue(mock_cmdloop.called)
        self.assertTrue(mock_post.called)
        mock_post.assert_called_once_with(
            'http://0.0.0.0:59999/',
            json={'jsonrpc': '2.0', 'id': 0, 'method': 'heartbeat'})