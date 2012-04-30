import threading
from datetime import datetime

def thread_name():
    """return the name of the current thread"""
    return threading.currentThread().getName()

def iso8601time(gmtime = None):
    """convert time to ISO 8601 format - it sucks less!

    :arg datetime: datetime object. If None, use ``datetime.utcnow()``
    """
    return gmtime.isoformat() if gmtime else datetime.utcnow().isoformat()
