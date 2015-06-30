# coding: utf-8

__author__ = 'buyvich'

__all__ = ['BaseTorrentClient']

class BaseTorrentClient(object):

    def check(self):
        raise RuntimeError('torrent client don`t specify')

    def torrent_add(self, torrent):
        """
        :type torrent: util.Torrent
        """
        raise RuntimeError('torrent client don`t specify')

    def torrent_info(self):
        raise RuntimeError('torrent client don`t specify')


# vim:ts=4:sts=4:sw=4:tw=85:et:
