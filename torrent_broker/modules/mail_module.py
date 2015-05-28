# coding: utf-8

import os
import email
import base64
import select
import imaplib
import logging
import threading

from torrent_broker import config
from torrent_broker.transmission import TransmissionRpc
from torrent_broker.util import Torrent

__author__ = 'buyvich'

log = logging.getLogger()

class EmailModule(threading.Thread):

    def __init__(self, host, login, password):
        super(EmailModule, self).__init__()
        mail_client = imaplib.IMAP4_SSL(host)
        mail_client.login(login, password)
        mail_client.select(mailbox='torrents', readonly=False)
        self.mail_client = mail_client
        self.transmission_client = TransmissionRpc()

        self.running = True

    def _wait_new_mail(self):
        # Note: do not use recent()
        select.select([], [], [], 15)
        try:
            result, data = self.mail_client.search(None, 'UNSEEN')
            if result != 'OK':
                raise RuntimeError('Cant get posts id')
        except:
            log.exception('Cant get posts')
            return []
        posts_id = filter(None, data[0].split(' '))
        return posts_id

    def _process_torrents(self, torrents):
        self.transmission_client.port_test()  # check transmission
        for torrent in torrents:
            self.transmission_client.torrent_add(torrent)

    def run(self):
        log.debug('Run worker: %s', self.getName())
        while self.running:
            posts_id = self._wait_new_mail()
            if not posts_id:
                continue
            log.debug('Get new posts: %s', len(posts_id))
            success_list = []
            for post_id in posts_id:
                try:
                    torrents = self.fetch(post_id)
                    log.debug('torrents from post %s: %s',
                              post_id, torrents)
                    self._process_torrents(torrents)
                    success_list.append(post_id)
                except:
                    log.exception('Cant process torrents from %s', post_id)
            if success_list:
                self.mail_client.store(
                    ','.join(success_list), '+FLAGS', '\\SEEN')
        log.debug('%s stopped', self.getName())

    def fetch(self, post_id):
        result, data = self.mail_client.fetch(post_id, '(RFC822)')
        email_msg = email.message_from_string(data[0][1])
        torrents = []
        for part in email_msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                for line in part.get_payload().split('\n'):
                    if line.startswith('\r'):
                        break
                    torrents.append(Torrent(url=line.strip()))
            elif content_type == 'application/x-bittorrent':
                if config.TRANSMISSION_WATCH_DIR:
                    filename = part.get_filename()
                    log.debug('get file: %s', filename)
                    full_name = os.path.join(
                        config.TRANSMISSION_WATCH_DIR, filename)
                    with open(full_name, mode='w') as f:
                        f.write(part.get_payload(decode=True))
                    log.debug('file saved to: %s', full_name)
                else:
                    torrent = base64.encodestring(
                        part.get_payload(decode=True))
                    torrents.append(Torrent(metainfo=torrent))
        return torrents
