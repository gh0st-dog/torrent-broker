import logging

__author__ = 'buyvich'

log = logging.getLogger()


class TransmissionRpc(object):

    def __init__(self):
        self.port = 9001
        self.host = '127.0.0.1'

    def add_torrent(self, url, meta=None):
        if meta:
            meta = meta[len('meta:'):]
            log.debug('Stub: adding torrent as base64: %s', meta)
        else:
            log.debug('Stub: adding torrent as url: %s', url)
