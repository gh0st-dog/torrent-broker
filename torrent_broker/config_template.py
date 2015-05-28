# coding: utf-8

import sys

__author__ = 'buyvich'

Loggers = {
    'main': {
        'class': 'StreamHandler',
        'args': {'stream': sys.stdout},
        'formatter': u'%(asctime)s  %(threadName)-8s %(levelname)-6s %(message)s',
        'level': 'DEBUG',
        'enabled': True,
    },
    'file': {
        'class': 'FileHandler',
        'args': [u'torrent_daemon.log'],
        'formatter': u'%(asctime)s  %(threadName)-8s %(levelname)-6s %(message)s',
        'level': 'DEBUG',
        'enabled': True,
    }
}


Modules = {
    'mail_1': {
        'class': 'EmailModule',
        'host': u'imap.yandex.ru',
        'login': u'',
        'password': u''
    },
}

TRANSMISSION_WATCH_DIR = ''
TRANSMISSION_HOST = ''
TRANSMISSION_PORT = ''

PID_FILE = 'torrent_broker.pid'

DEBUG = False
