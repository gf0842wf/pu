# -*- coding: utf-8 -*-
"""threading event"""

from threading import Condition, Lock


class AsyncResult(object):
    """threading模块提供了Event,但是没提供future/promise模式的异步 AsyncResult
    : AsyncResult类似阻塞channel
    : Queue类似非阻塞channel
    """

    def __init__(self):
        self.cond = Condition(Lock())
        self.value = None
        self.exception = None

    def set(self, value=None):
        self.cond.acquire()
        self.value = value
        try:
            self.cond.notify_all()
        finally:
            self.cond.release()

    def set_exception(self, exception):
        self.cond.acquire()
        self.exception = exception
        try:
            self.cond.notify_all()
        finally:
            self.cond.release()

    def get(self, block=True, timeout=None):
        self.cond.acquire()
        try:
            if block:
                self.cond.wait(timeout)
        finally:
            self.cond.release()
            if self.exception is not None:
                raise self.exception
            return self.value


def test_AsyncResult():
    from threading import Thread
    import time

    event = AsyncResult()

    def foo(event):
        time.sleep(5)
        event.set('ooxx')
        # event.set_exception(Exception('ooxx'))

    t = Thread(target=foo, args=(event,))
    t.start()
    print event.get()
    print 'over..'