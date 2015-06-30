# coding: utf-8

import logging
import urllib2
import pprint
import json
import base64
import os

from torrent_broker import util
from torrent_broker.torrent_clients.base import BaseTorrentClient

__author__ = 'buyvich'

log = logging.getLogger()

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9091


class Transmission(BaseTorrentClient):

    def __init__(self, host=None, port=None):
        self.port = port
        self.host = host
        if not self.host:
            self._get_params_from_config()
        if not self.host:
            self.host = DEFAULT_HOST
            self.port = DEFAULT_PORT
        self.csrf_token = None

    def _get_params_from_config(self):
        config = util.get_config()
        self.port = getattr(config, 'TRANSMISSION_HOST', None)
        self.port = getattr(config, 'TRANSMISSION_PORT', None)

    def _send_response(self, method, arguments=None):
        if not arguments:
            arguments = {}
        data = {
            'method': method,
            'arguments': arguments
        }
        data = json.dumps(data)
        log.debug('call %s: %s;', method, data)
        url = 'http://{}:{}/transmission/rpc'.format(self.host, self.port)
        request = urllib2.Request(url, data=data)
        request.add_header('X-Transmission-Session-Id', self.csrf_token)
        opener = urllib2.build_opener()
        try:
            log.debug('sending request to %s:', request.get_full_url())
            res = opener.open(request)
            body = json.loads(res.read())
            log.debug('response body: %s', pprint.pformat(body))
            return body
        except urllib2.HTTPError as ex:
            if ex.getcode() == 409:
                self.csrf_token = ex.headers['X-Transmission-Session-Id']
                return self._send_response(method, arguments)
            raise
        except urllib2.URLError as ex:
            raise RuntimeError(str(ex))

    def _check_result(self, res, error_msg=None):
        if not error_msg:
            error_msg = 'Transmission daemon is not available'
        if res['result'] != 'success':
            raise RuntimeError(error_msg)

    def torrent_add(self, torrent):
        """
        :type torrent: util.Torrent
        """
        config = util.get_config()
        if config.TRANSMISSION_WATCH_DIR and torrent.filename:
            filename = torrent.filename
            log.debug('get file: %s', filename)
            full_name = os.path.join(
                config.TRANSMISSION_WATCH_DIR, filename)
            with open(full_name, mode='w') as f:
                f.write(base64.decodestring(
                    torrent.get_transmission_payload()))
            log.debug('file saved to: %s', full_name)
            return
        data = torrent.get_transmission_payload()
        resp = self._send_response('torrent_add', data)
        self._check_result(resp)

    def torrent_info(self):
        pass

    def session_stats(self):
        self._check_result(self._send_response('session-stats'))

    def port_test(self):
        self._check_result(self._send_response('port-test'))

    def check(self):
        config = util.get_config()
        watch_dir = getattr(config, 'TRANSMISSION_WATCH_DIR', None)
        if watch_dir and not os.path.exists(watch_dir):
            raise RuntimeError('Watch dir %s does not exists' % watch_dir)
        self.session_stats()


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    util.configure_logger()
    res = Transmission().check()
    pprint.pprint(res)
