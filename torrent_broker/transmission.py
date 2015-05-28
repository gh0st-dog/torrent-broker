import logging
import urllib2
import httplib
import pprint
import json

from torrent_broker import util

__author__ = 'buyvich'

log = logging.getLogger()


class TransmissionRpc(object):

    def __init__(self, host='127.0.0.1', port=9091):
        self.port = port
        self.host = host
        self.csrf_token = None

    def _send_response(self, method, arguments=None):
        httplib.HTTPConnection.debuglevel = 1
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
            log.debug('sending response to %s:', request.get_full_url())
            res = opener.open(request)
            body = json.loads(res.read())
            log.debug('response body: %s', pprint.pformat(body))
            return body
        except urllib2.HTTPError as ex:
            if ex.getcode() == 409:
                self.csrf_token = ex.headers['X-Transmission-Session-Id']
                return self._send_response(method, arguments)
            raise

    def torrent_add(self, torrent):
        """
        :type torrent: util.Torrent
        """
        log.debug('Stub; adding torrent: %s',
                  torrent.get_transmission_payload())

    def torrent_info(self):
        pass

    def session_stats(self):
        resp = self._send_response('session-stats')
        if resp['result'] != 'success':
            raise RuntimeError('Transmission daemon is not available')

    def port_test(self):
        resp = self._send_response('port-test')
        if resp['result'] != 'success':
            raise RuntimeError('Transmission daemon is not available')


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    util.configure_logger()
    res = TransmissionRpc().session_stats()
    pprint.pprint(res)