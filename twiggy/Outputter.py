import multiprocessing
import threading
import sys
import atexit

class Outputter(object):
    """
    Does the work of formatting and writing a message.

    Multiple implementations are expected.
    """

    def __init__(self, format, async = False):
        self._format = format

        if not async:
            self._lock = threading.Lock()
            self.output = self.__sync_output
            self.close = self._close
            self._open()
        else:
            self.output = self.__async_output
            self.close = self.__async_close
            self.__queue = multiprocessing.JoinableQueue(100)
            self.__child = multiprocessing.Process(target=self.__child_main, args=(self,))
            self.__child.start() # XXX s.b. daemon=True? don't think so, b/c atexit instead

        atexit.register(self.close)

    # use a plain function so Windows is cool
    @staticmethod
    def __child_main(self):
        self._open()
        while True:
            msg = self.__queue.get()
            if msg != "SHUTDOWN":
                x = self._format(msg)
                self._write(x)
                del x, msg
                self.__queue.task_done()
            else:
                assert self.__queue.empty(), "Shutdown but queue not empty"
                self._close()
                self.__queue.task_done()
                break

    def _open(self):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError

    def _write(self, x):
        raise NotImplementedError

    def __sync_output(self, msg):
        x = self._format(msg)
        with self._lock:
            self._write(x)

    def __async_output(self, msg):
        self.__queue.put_nowait(msg)

    def __async_close(self):
        self.__queue.put_nowait("SHUTDOWN") # XXX maybe just put?
        self.__queue.close()
        self.__queue.join()

class FileOutputter(Outputter):
    def __init__(self, format, name, mode='a', buffering=1, async=False):
        self.filename = name
        self.mode = mode
        self.buffering = buffering
        super(FileOutputter, self).__init__(format, async)

    def _open(self):
        self.file = open(self.filename, self.mode, self.buffering)

    def _close(self):
        self.file.close()

    def _write(self, x):
        self.file.write(x)

class StreamOutputter(Outputter):

    def __init__(self, format, stream=sys.stderr):
        self.stream = stream
        super(StreamOutputter, self).__init__(format)

    def _open(self):
        pass

    def _close(self):
        pass

    def _write(self, x):
        self.stream.write(x)