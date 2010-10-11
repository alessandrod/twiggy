##############################
Reference Guide
##############################


.. _dynamic-messages:

******************
Dynamic logging
******************

Any functions in message args/fields are called and the value substitued:

>>> import os
>>> from twiggy.lib import thread_name
>>> thread_name()
'MainThread'
>>> log.fields(pid=os.getpid).info("I'm in thread {0}", thread_name) #doctest:+ELLIPSIS
INFO:pid=...:I'm in thread MainThread

This can be useful with partially-bound loggers, which let's us do some cool stuff:

>>> class ThreadTracker(object):
...     """a proxy that logs attribute access"""
...     def __init__(self, obj):
...         self.__obj = obj
...         # a partially bound logger
...         self.__log = log.name("tracker").fields(obj_id=id(obj), thread=thread_name)
...         self.__log.debug("started tracking")
...     def __getattr__(self, attr):
...         self.__log.debug("accessed {0}", attr)
...         return getattr(self.__obj, attr)
...
>>> class Bunch(object):
...     pass
...
>>> foo = Bunch()
>>> foo.bar = 42
>>> tracked = ThreadTracker(foo) #doctest:+ELLIPSIS
DEBUG:tracker:obj_id=...:thread=MainThread:started tracking
>>> tracked.bar #doctest:+ELLIPSIS
DEBUG:tracker:obj_id=...:thread=MainThread:accessed bar
42
>>> import threading
>>> t=threading.Thread(target = lambda: tracked.bar * 2, name = "TheDoubler")
>>> t.start(); t.join() #doctest:+ELLIPSIS
DEBUG:tracker:obj_id=...:thread=TheDoubler:accessed bar

If you really want to log a callable, ``repr()`` it or wrap it in lambda.

*******************
Features!
*******************
Features are optional additons of logging functionality to the magic :data:`log`. They encapsulate common logging patterns. Code can be written using a feature, enhancing what information is logged. The feature can be disabled at :ref:`runtime <twiggy-setup>` if desired.

.. doctest::

    >>> import twiggy.features.socket
    >>> twiggy.quickSetup()
    >>> twiggy.log.addFeature(twiggy.features.socket.socket)
    >>> import socket
    >>> s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #doctest:+ELLIPSIS
    <socket._socketobject object at 0x...>
    >>> s.connect(('www.python.org', 80))
    >>> twiggy.log.socket(s).debug("connected")
    DEBUG:host=dinsdale.python.org:ip_addr=82.94.164.162:port=80:service=http:connected
    >>> # turn off the feature - the name is still available
    ... twiggy.log.disableFeature('socket')
    >>> twiggy.log.socket(s).debug("connected")
    DEBUG:connected
    >>> # use a different implementation
    ... twiggy.log.addFeature(twiggy.features.socket.socket_minimal, 'socket')
    >>> twiggy.log.socket(s).debug("connected")
    DEBUG:ip_addr=82.94.164.162:port=80:connected

.. _never-raises:

***********************
Stays Out of Your Way
***********************
Twiggy tries to stay out of your way.  Specifically, an error in logging should **never** propogate outside the logging subsystem and cause your main application to crash. Instead, errors are trapped and reported by the  :data:`~twiggy.internal_log`.

Instances of :class:`~twiggy.logger.InternalLog` only have a single :class:`~twiggy.outputs.Output` - they do not use emitters. By default, these messages are sent to standard error. You may assign an alternate ouput (such as a file) to ``twiggy.internal_log.output`` if desired, with the following conditions:

* the output should be failsafe - any errors that occur during internal logging will *not* be caught and will cause your application to crash.
* accordingly, networked or asynchronous outputs are not recommended.
* make sure someone is reading these log messages!

****************
Concurrency
****************
Locking in twiggy is as fine-grained as possible. Each individual output has its own lock (if necessary), and only holds that lock when writing. Using redundant outputs (ie, pointing to the same file) is not supported and will cause logfile corruption.

Asynchronous loggers never lock.

*******************
Use by Libraries
*******************
Libraries require special care to be polite and usable by application code.  The library should have a single bound in its top-level package that's used by modules. Library logging should generally be silent by default::

    # in mylib/__init__.py
    log = twiggy.log.name('mylib')
    log.min_level = twiggy.levels.DISABLED

    # in mylib/some_module.py
    from . import log
    log.debug("hi there")

This allows application code to enable/disable all of library's logging as needed::

    # in twiggy_setup
    import mylib
    mylib.log.min_level = twiggy.levels.INFO

In addition to min_level, loggers also have a :attr:`~twiggy.logger.Logger.filter`. This filter operates *only on the format string*, and is intended to allow users to selectively disable individual messages in a poorly-written library::

    # in mylib:
    for i in xrange(1000000):
        log.warning("blah blah {}", 42)

    # in twiggy_setup: turn off stupidness
    mylib.log.filter = lambda format_spec: format_spec != "blah blah {}"

Note that using a filter this way is an optimization - in general, application code should use :data:`~twiggy.emitters` instead.

********************
Tips And Tricks
********************

.. _alternate-styles:

Alternate Styles
================
In addition to the default new-style (braces) format specs, twiggy also supports old-style (percent, aka printf) and templates (dollar):

.. doctest::

    >>> log.options(style='percent').info('I like %s', "bikes")
    INFO:I like bikes
    >>> log.options(style='dollar').info('$what kill', what='Cars')
    INFO:Cars kill

Use Fields
==========
Use :meth:`~twiggy.logger.Logger.fields` to include key-value data in a message instead of embedding it the human-readable string::

.. testcode::

    # do this:
    log.fields(key1='a', key2='b').info("stuff happenend")

    # not this:
    log.info("stuff happened. key1: {} key2: {}", 'a', 'b')


**********************
Technical Details
**********************

Independence of logger instances
================================
Each log instance created by partial binding is independent from each other. In particular, a logger's :meth:`~twiggy.logger.Logger.name` has no relation to the object; it's just for human use:

.. doctest::

    >>> log.name('bob') is log.name('bob')
    False

Internal optimizations
========================
Twiggy has been written to be fast, minimizing the performance impact on the main execution path. In particular, messages that will cause no output are handled as quickly as possible.  Users are therefore encouraged to add lots of logging for development/debugging purposes and then turn them off in production.

*******************
Extending Twiggy
*******************
When developing extensions to twiggy, use the :data:`~twiggy.devel_log`. An :class:`~twiggy.logger.InternalLogger`, the devel_log is completely separate from the main :data:`~twiggy.log`.  By default, messages logged to the devel_log are discarded; assigning an appropriate :class:`~twiggy.outputs.Ouput` to its ``output`` attribute before using.

Writing Features
===================
Features are used to encapsulate common logging patterns. They are implemented as methods added to the :class:`~twiggy.logger.Logger` class. They receive an instance as the first argument (ie, ``self``). :meth:`~twiggy.logger.Logger.addFeature <Enable the feature>` before using.

Features come in two flavors: those that add information to a message's fields or set options, and those that cause output.

Features which only add fields/set options should simply call the appropriate method on ``self`` and return the resultant object::

    def dimensions(self, shape):
        return self.fields(height=shape.height, width=shape.width)

Features can also emit messages as usual.  Do not return::

    def sayhi(self, lang):
        if lang == 'en':
            self.info("Hello world")
        elif lang == 'fr':
            self.info("Bonjour tout le monde")

.. _wsgi-support:

If the feature should add fields *and* emit in the same step (like :meth:`~twiggy.logger.Logger.struct`), use the :func:`~twiggy.logger.emit` decorators.  Here's a prototype feature that dumps information about a `WSGI environ <http://www.python.org/dev/peps/pep-0333/#environ-variables>`_.

.. testcode::

    from twiggy.logger import emit

    @emit.info
    def dump_wsgi(self, wsgi_environ):
        keys = ['SERVER_PROTOCOL', 'SERVER_PORT', 'SERVER_NAME', 'CONTENT_LENGTH', 'CONTENT_TYPE', 'QUERY_STRING', 'PATH_INFO', 'SCRIPT_NAME', 'REQUEST_METHOD']
        d = {}
        for k in keys:
            d[k] = wsgi_environ.get(k, '')

        for k, v in wsgi_environ.iteritems():
            if k.startswith('HTTP_'):
                k = k[5:].title().replace('_', '-')
                d[k] = v

        return self.name('dumpwsgi').fieldsDict(d)




Writing Outputs
===================
How to do that

Writing Formats
===================
How to do that, including :class:`~twiggy.lib.ConversionTable`