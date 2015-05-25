# coding: utf-8

import time
import signal
import logging
import threading

from torrent_broker import util
from torrent_broker import config
from torrent_broker import modules
from torrent_broker import daemonize

__author__ = 'buyvich'

log = logging.getLogger()
log.setLevel(logging.DEBUG)

WORKER_CHECK_TIMEOUT = 10  # sec


class TorrentDaemon(object):

    def __init__(self):
        self.configure_signals()
        self.workers = []

    def process(self):
        modules = config.Modules
        for m_name, m_params in modules.iteritems():
            params = m_params.copy()
            module_class = self._load_module(params['class'])
            params.pop('class')
            worker = module_class(**params)
            worker.setName(m_name)
            log.debug('Configure worker %s (module %s) with params: %s',
                m_name, module_class.__name__, params)
            self.workers.append(worker)
            worker.start()

        while self.workers_alive():
            time.sleep(WORKER_CHECK_TIMEOUT)

    def workers_alive(self):
        return any(worker.is_alive() for worker in self.workers)

    def configure_signals(self):
        signal.signal(signal.SIGINT, self.stop_workers)
        signal.signal(signal.SIGTERM, self.stop_workers)

    def stop_workers(self, *args):
        log.debug('Stop all workers')
        for worker in self.workers:
            if worker.is_alive():
                worker.running = False
        while self.workers_alive():
            time.sleep(WORKER_CHECK_TIMEOUT)

    def _load_module(self, module_name):
        try:
            return getattr(modules, module_name)
        except AttributeError:
            log.exception('Cant import module %s', module_name)
            raise


def configure_logger():
    for logger_name, params in config.Loggers.iteritems():
        if params.get('enabled', False):
            l_class = getattr(logging, params['class'])
            if isinstance(params['args'], list):
                lh = l_class(*params['args'])
            else:
                lh = l_class(**params['args'])
            lh.setLevel(getattr(logging, params['level']))
            lh.setFormatter(logging.Formatter(params['formatter']))
            log.addHandler(lh)

if __name__ == '__main__':
    util.set_main_thread_name()
    configure_logger()
    daemonize.daemonize()
    TorrentDaemon().process()
