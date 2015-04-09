#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" description
sqlite3 db client
"""

from StringIO import StringIO
import logging
import sqlite3
import os
import time

logger = logging.getLogger(__name__)


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class Sqlite3Connection(object):
    def __init__(self, memorize=False, **kwargs):
        """
        :param memorize: True-把db文件加载到内存,***而且此时向数据库写并不会同步到文件中***
        :param database(或db): 数据库文件,:memory:表示存储在内存中
        """
        self.database = kwargs.get('database') or kwargs.get('db')
        self.memorize = memorize

        if self.memorize:
            self.load()
        else:
            self.conn = sqlite3.connect(self.database)

    def load(self):
        """把文件db load到内存
        """
        _conn = sqlite3.connect(self.database)
        str_buffer = StringIO()
        for line in _conn.iterdump():
            str_buffer.write('%s\n' % line)
        self.conn = sqlite3.connect(':memory:')
        self.conn.executescript(str_buffer.getvalue())
        _conn.close()

    def dump(self):
        """把内存db dump到文件
        : 暂时不再使用
        """
        os.unlink(self.database)
        _conn = sqlite3.connect(self.database)
        str_buffer = StringIO()
        for line in self.conn.iterdump():
            str_buffer.write('%s\n' % line)
        _conn.executescript(str_buffer.getvalue())
        _conn.close()

    def reload(self):
        """重新加载
        """
        self.close()
        if self.memorize:
            self.load()
        else:
            self.conn = sqlite3.connect(self.database)

    def close(self):
        try:
            self.conn.close()
        finally:
            logger.info('connection closed')

    def commit(self):
        self.conn.commit()

    def execute(self, query, *args, **kwargs):
        """
        :return: lastrowid
        """
        return self._execute_lastrowid(query, *args, **kwargs)

    def _execute_lastrowid(self, query, *args, **kwargs):
        try:
            result, cursor = self._execute(query, args, kwargs)
            if result is False:
                return False
            return cursor.lastrowid
        finally:
            if locals().get('cursor'):
                cursor.close()

    def fetchall(self, query, *args, **kwargs):
        try:
            result, cursor = self._execute(query, args, kwargs)
            column_names = [d[0] for d in cursor.description]
            if result is False:
                return False
            return [Row(zip(column_names, row)) for row in cursor]
        finally:
            if locals().get('cursor'):
                cursor.close()

    def fetchone(self, query, *args, **kwargs):
        rows = self.fetchall(query, *args, **kwargs)
        if rows is False:
            return False
        elif not rows:
            return None
        elif len(rows) > 1:
            logger.warn('Multiple rows returned for fetchone')
            return rows[0]
        else:
            return rows[0]

    def executemany(self, query, args, kwargs={'auto_commit': True}):
        """
        :return: lastrowid
        example:
        executemany('insert into book (name, author) values (%s, %s)',
                    [
                        ('a', u'张三'),
                        ('b', u'李四'),
                        ('c', u'王二')])
        """
        return self._executemany_lastrowid(query, args, kwargs)

    def _executemany_lastrowid(self, query, args, kwargs):
        try:
            result, cursor = self._executemany(query, args, kwargs)
            if result is False:
                return False
            return cursor.lastrowid
        finally:
            if locals().get('cursor'):
                cursor.close()

    def _execute(self, query, args, kwargs):
        """
        :return: [result, cursor]
        """
        auto_commit = kwargs.get('auto_commit')
        cursor = self.conn.cursor()
        logger.debug('sql: %s, args: %s', query, str(args))
        ret = [cursor.execute(query, args), cursor]
        if auto_commit:
            self.commit()
        return ret

    def _executemany(self, query, args, kwargs):
        """
        :return: [result, cursor]
        """
        auto_commit = kwargs.get('auto_commit')
        cursor = self.conn.cursor()
        logger.debug('sql: %s, args: %s', query, str(args))
        ret = [cursor.executemany(query, args), cursor]
        if auto_commit:
            self.commit()
        return ret

    def get_fields(self, table_name):
        result, cursor = self._execute('select * from %s limit 0' % table_name, tuple(), {})
        if result is False:
            return False
        return [i[0] for i in cursor.description]

    def __del__(self):
        self.close()


def test_client():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)-15s %(levelname)s:%(module)s] %(message)s')

    options = dict(database='x.db')

    conn1 = Sqlite3Connection(**options)
    conn1.execute('create table book (name varchar(50), author varchar(50))')
    print conn1.fetchall('select * from book where author=?', 'yyyy')
    print conn1.get_fields('book')
    conn1.close()

    conn2 = Sqlite3Connection(**options)
    print conn2.fetchall('select * from book')
    print conn2.execute('insert into book values("abc", ?)', 'zhangsan')
    print conn2.get_fields('book')
    conn2.close()

    conn3 = Sqlite3Connection(**options)
    print conn3.executemany('insert into book (name, author) values (?, ?)',
                            [
                                ('a', 'zhangsan'),
                                ('b', 'lisi'),
                                ('c', 'wanger')])
    print conn3.get_fields('book')
    conn3.execute('insert into book values("abc", ?)', 'yyyy', auto_commit=False)


def test_memorize():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)-15s %(levelname)s:%(module)s] %(message)s')
    c = Sqlite3Connection(database='x.db', memorize=True)
    c.execute('insert into book values("abc", ?)', 'xxxx')  # 不会同步到磁盘,只在内存中
    print c.fetchall('select * from book')


def test_benchmark():
    c = Sqlite3Connection(database='x.db', memorize=True)
    t0 = time.time()
    [c.fetchone('select * from book where author="zhangsan"') for _ in xrange(10000)]
    print 10000 / (time.time() - t0), 'qps'
    c.close()
