# -*- coding: utf-8 -*-
from collections import Mapping


def shorten(s, width=80):
    """
    >>> shorten('a very very very very long sentence', 20)
    'a very very ..(23)..'
    """
    if not isinstance(s, str):
        s = str(s)

    length = len(s)
    if length < width:
        return s

    cut_length = length - width + 6
    x = len(str(cut_length))
    cut_length += x

    # 长度调整
    if x != len(str(cut_length)):
        cut_length += 1

    end_pos = length - cut_length
    return s[:end_pos] + '..(%d)..' % cut_length


def deep_encode(ob, encoding='utf_8', errors='strict'):
    """深入数据结构内部，尽可能把字符串编码
    """
    if isinstance(ob, bytes):
        return ob
    elif isinstance(ob, str):
        return ob.encode(encoding, errors)
    elif isinstance(ob, tuple):
        return tuple(deep_encode(x, encoding, errors) for x in ob)
    elif isinstance(ob, list):
        return [deep_encode(x, encoding, errors) for x in ob]
    elif isinstance(ob, Mapping):
        new = ob.__class__()
        for key, value in ob.items():
            key = deep_encode(key, encoding, errors)
            value = deep_encode(value, encoding, errors)
            new[key] = value
        return new
    else:
        return ob


def deep_decode(ob, encoding='utf_8', errors='strict'):
    """深入数据结构内部，尽可能把 bytes 解码
    """
    if isinstance(ob, bytes):
        return ob.decode(encoding, errors)
    elif isinstance(ob, str):
        return ob
    elif isinstance(ob, tuple):
        return tuple(deep_decode(x, encoding, errors) for x in ob)
    elif isinstance(ob, list):
        return [deep_decode(x, encoding, errors) for x in ob]
    elif isinstance(ob, Mapping):
        new = ob.__class__()
        for key, value in ob.items():
            key = deep_decode(key, encoding, errors)
            value = deep_decode(value, encoding, errors)
            new[key] = value
        return new
    else:
        return ob


def group(seq, chunk_size):
    """Split a sequence into chunks.

    Source: http://stackoverflow.com/a/312464/1158494

    :param seq: sequence to be split.
    :param chunk_size: chunk size.
    """
    for i in range(0, len(seq), chunk_size):
        yield seq[i:i + chunk_size]


def xfind_all(s, sep, start=None, end=None):
    """ 返回所有index
    >>> list(xfind_all('abcdabcdabcd', 'bc'))
    [1, 5, 9]
    >>> 
    """
    _start = start
    while True:
        index = s.find(sep, _start, end)
        if index != -1:
            yield index
        else:
            break
        _start = index + len(sep)


def xsplit(s, sep, maxsplit=None):
    """ split的generator版本
    >>> list(xsplit('abcdabcdabcd', 'bc'))
    ['a', 'da', 'da', 'd']
    >>>
    """
    start = 0
    cnt = 0
    while True:
        pos = s.find(sep, start)
        if pos == -1:
            yield s[start:]
            cnt += 1
            break
        else:
            old_start = start
            start = pos + len(sep)
            yield s[old_start:pos]
            cnt += 1
        if cnt == maxsplit:
            break
    if pos != -1:
        yield s[pos:]


if __name__ == '__main__':
    import doctest

    doctest.testmod()
