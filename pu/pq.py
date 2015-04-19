# -*- coding: utf-8 -*-
""" 用cython提升十倍性能
pip install cython
cython -a pq.py
gcc -c -fPIC -I/usr/include/python2.6 pq.c
gcc -shared pq.o -o pq.so
"""

from collections import defaultdict


def query_list(L, query):
    """ 支持类似 mongodb的 $or $in $nin $gt $gte $lt $lte $ne
    """
    for d in L:
        flag = False
        for k, v in query.iteritems():
            if k == '$or':
                op_or = query['$or']
                rr = []
                for dd in op_or:
                    for kk, vv in dd.iteritems():
                        if isinstance(vv, dict):
                            assert len(vv) == 1
                            op = vv.keys()[0]
                            if op == '$gt':
                                if d[kk] > vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$gte':
                                if d[kk] >= vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$lt':
                                if d[kk] < vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$lte':
                                if d[kk] <= vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$ne':
                                if d[kk] != vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$in':
                                if d[kk] in vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            elif op == '$nin':
                                if d[kk] not in vv[op]:
                                    rr.append(True)
                                else:
                                    rr.append(False)
                            else:
                                raise Exception('operation not found')
                        else:
                            if d[kk] == dd[kk]:
                                rr.append(True)
                            else:
                                rr.append(False)
                if not any(rr):
                    flag = True
                    break
            elif k == '$lambda':  # 使用lambda时,不能使用其它操作
                if not v(d):
                    flag = True
                    break
            else:
                if isinstance(v, dict):
                    assert len(v) == 1
                    op = v.keys()[0]
                    if op == '$gt':
                        if not (d[k] > v[op]):
                            flag = True
                            break
                    elif op == '$gte':
                        if not (d[k] >= v[op]):
                            flag = True
                            break
                    elif op == '$lt':
                        if not (d[k] < v[op]):
                            flag = True
                            break
                    elif op == '$lte':
                        if not (d[k] <= v[op]):
                            flag = True
                            break
                    elif op == '$ne':
                        if not (d[k] != v[op]):
                            flag = True
                            break
                    elif op == '$in':
                        if not (d[k] in v[op]):
                            flag = True
                            break
                    elif op == '$nin':
                        if not (d[k] not in v[op]):
                            flag = True
                            break
                    else:
                        raise Exception('operation not found')
                else:
                    if d[k] != v:
                        flag = True
                        break
        if flag:
            continue

        yield d


class PQ(object):
    """ python list(dict) query 类似 mongodb操作 [{}, ..]
    """

    def __init__(self, L):
        self.indexes = defaultdict(lambda: defaultdict(list))
        self.L = L

    def set_index(self, index={}):
        """ 索引,仅适用于 {'name':'fk'} 这种相等查询优化, 索引会加倍内存使用
        """
        key = index['key']
        for _d in self.L:
            self.indexes[key][_d[key]].append(_d)

    def pop_index(self, index={}):
        key = index['key']
        self.indexes.pop(key, None)

    def find(self, query={}, fields=[], sort_key=None, limit=None, reverse=False):
        """
        :param sort: eg. sort=lambda l: (l['name'], l['age'])
        """
        L = self.L
        result = []

        # query
        for i in query:
            if i in self.indexes and not isinstance(query[i], (list, dict)):
                L = self.indexes[i][query[i]]
                break
        for _d in query_list(L, query):
            # fields
            d = {}
            if fields:
                for k in fields:
                    d[k] = _d[k]
            elif _d:
                d.update(_d)

            result.append(d)

        # sort, reverse
        if sort_key:
            result.sort(key=sort_key, reverse=reverse)
        else:
            if reverse:
                result.reverse()

        # limit
        if limit:
            result = result[:limit]

        return result


if __name__ == '__main__':
    l = [{'name': 'gp', 'age': 24}, {'name': 'fk', 'age': 25}]
    print list(query_list(l, {'$or': [{'name': {'$gt': 'zz'}}, {'age': 24}]}))

    pq = PQ(l)
    pq.set_index({'key': 'name'})
    # print pq.find(query={'$or': [{'name': {'$in': ['xx', 'gp']}}, {'age': 25}]}, fields=['name'], limit=2)
    print pq.find(query={'name': 'fk'})
    print pq.find(query={'$lambda': lambda d: d['name'] == 'fk'})
    l = [{'name': 'gp', 'age': 24}] * 1000000 + [{'name': 'gp', 'age': 23}]
    import time

    t0 = time.time()
    print list(query_list(l, {'age': 23, 'name': 'gp'}))
    print time.time() - t0