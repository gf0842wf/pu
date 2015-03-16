# -*- coding: utf-8 -*-
from collections import OrderedDict as _OrderedDict, Mapping


def repr_dict(d, sort_func=None):
    """更灵活地显示 dict

    repr_dict(d, sorted)
    repr_dict(d, partial(sorted, reverse=True))
    """
    if d:
        if sort_func:
            keys = sort_func(d.keys())
        else:
            keys = d.keys()
        repr_items = ', '.join('%s=%r' % (k, d[k]) for k in keys)
    else:
        repr_items = ''
    return '%s(%s)' % (d.__class__.__name__, repr_items)


class Dot:
    """支持对现有的 dict, OrderedDict 添加 . 方式访问
    """

    def __init__(self, d):
        object.__setattr__(self, '_d', d)

    def __repr__(self):
        return self._d.__repr__()

    def __str__(self):
        return self._d.__str__()

    def __contains__(self, key):
        return self._d.__contains__(key)

    def __getitem__(self, key):
        return self._d.__getitem__(key)

    def __setitem__(self, key, value):
        return self._d.__setitem__(key, value)

    def __delitem__(self, key):
        return self._d.__delitem__(key)

    def __getattr__(self, name):
        try:
            value = self._d[name]
        except KeyError:
            raise AttributeError('%r has not attr %r' % (self, name))
        else:
            if isinstance(value, Mapping):
                return Dot(value)
            return value

    def __setattr__(self, name, value):
        return self._d.__setitem__(name, value)

    def __delattr__(self, name):
        try:
            del self._d[name]
        except KeyError:
            raise AttributeError('%r has not attr %r' % self, name)

    def get(self, key, default=None):
        return self._d.get(key, default)

    def setdefault(self, key, default):
        return self._d.setdefault(key, default)


class OrderedDict(_OrderedDict):
    """改进显示，看起来更符合人们的习惯
    """

    def __repr__(self):
        return repr_dict(self)


class DotDict(dict):
    """允许用 . 访问字典成员
    """
    __setattr__ = dict.__setitem__

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('%r has not attr %r' % (self, name))

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError('%r has not attr %r' % (self, name))


class DotOrderedDict(OrderedDict):
    def __getattr__(self, name):
        if name.startswith('_OrderedDict'):
            raise AttributeError('%s has not attr %r' % (
                self.__class__.__name__, name))
        try:
            return self[name]
        except KeyError:
            raise AttributeError('%r has not attr %r' % (self, name))

    def __setattr__(self, name, value):
        if name.startswith('_OrderedDict'):
            return OrderedDict.__setattr__(self, name, value)
        self.__setitem__(name, value)

    def __delattr__(self, name):
        pass
        try:
            OrderedDict.__delitem__(self, name)
        except KeyError:
            raise AttributeError('%r has not attr %r' % (self, name))


def union_dict(*objs):
    """字典合并,值相加
    :param objs: 多个字典
    :return: 合并后的字典
    >>> union_dict({'a': 2, 'b': 3}, {'a': 3})
    {'a': 5, 'b': 3}
    """
    _keys = set(sum([obj.keys() for obj in objs], []))
    _total = {}
    for _key in _keys:
        _total[_key] = sum([obj.get(_key, 0) for obj in objs])
    return _total