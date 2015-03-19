# -*- coding: utf-8 -*-
import binascii


class pretty_bytes(bytes):
    """提供自定义格式
    >>> pb = pretty_bytes('\xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89')
    >>> '{0:hex}'.format(pb)
    'e887aae5ae9ae4b989'
    >>> '{0:HEX}'.format(pb)
    'E887AAE5AE9AE4B989'
    >>> '{0:hex+}'.format(pb)
    'e8 87 aa e5 ae 9a e4 b9 89'
    >>> '{0:HEX+}'.format(pb)
    'E8 87 AA E5 AE 9A E4 B9 89'
    >>> '{0}'.format(pb)
    '\xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89'
    """

    def __format__(self, format_spec):
        if format_spec == 'hex':
            return binascii.hexlify(self).decode()
        elif format_spec == 'HEX':
            return ''.join('%02X' % ord(b) for b in self)
        elif format_spec == 'hex+':
            return ' '.join('%02x' % ord(b) for b in self)
        elif format_spec == 'HEX+':
            return ' '.join('%02X' % ord(b) for b in self)
        else:
            return str(self)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
