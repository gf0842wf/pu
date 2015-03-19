# -*- coding: utf-8 -*-
"""threading event"""

from threading import Condition, Lock


class AsyncResult(object):
    def __init__(self, timeout=None):
        """threading模块提供了Event,但是没提供future/promise模式的异步 AsyncResult
        : AsyncResult类似阻塞channel
        : Queue类似非阻塞channel
        """
        self.__cond = Condition(Lock())
        self.__flag = False
        self.__value = None
        self.__timeout = timeout
        self.__exception = None

    def set(self, value=None):
        self.__cond.acquire()
        try:
            self.__flag = True
            self.__value = value
            self.__cond.notify_all()
        finally:
            self.__cond.release()

    def set_exception(self, exception=None):
        self.__cond.acquire()
        try:
            self.__flag = True
            self.__exception = exception
            self.__cond.notify_all()
        finally:
            self.__cond.release()

    def clear(self):
        self.__cond.acquire()
        try:
            self.__flag = False
        finally:
            self.__cond.release()

    def get(self, block=True, timeout=None):
        if self.__timeout is not None:
            timeout = self.__timeout

        self.__cond.acquire()
        try:
            if not block:
                return self.__value
            if self.__exception is not None:
                raise self.__exception
            if not self.__flag:
                self.__cond.wait(timeout)
            return self.__value
        finally:
            self.__cond.release()


def test_AsyncResult():
    from threading import Thread
    import time

    event1 = AsyncResult()
    event2 = AsyncResult()

    def foo(event):
        time.sleep(2)
        event.set('ooxx')
        # event.set_exception(Exception('ooxx'))

    t1 = Thread(target=foo, args=(event1,))
    t2 = Thread(target=foo, args=(event2,))
    t1.start()
    t2.start()
    print event1.get()
    print event2.get()
    print 'over..'


if __name__ == '__main__':
    test_AsyncResult()