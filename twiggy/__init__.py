__all__=['log', 'emitters', 'add_emitters', 'devel_log', 'filters', 'formats', 'outputs', 'levels', 'quick_setup']
from datetime import datetime
import sys
import os

import logger
import filters
import formats
import outputs
import levels


## globals creation is wrapped in a function so that we can do sane testing
def _populate_globals():
    global __fields, log, emitters, __internal_format, __internal_output, internal_log, devel_log

    try:
        log
    except NameError:
        pass
    else:
        raise RuntimeError("Attempted to populate globals twice")

    ## a useful default fields
    __fields = {'time':datetime.utcnow}

    log = logger.Logger(__fields)

    emitters = log._emitters

    __internal_format = formats.LineFormat(conversion = formats.line_conversion)
    __internal_output = outputs.StreamOutput(format=__internal_format, stream=sys.stderr)

    internal_log = logger.InternalLogger(fields = __fields, output=__internal_output).name('twiggy.internal').trace('error')

    devel_log = logger.InternalLogger(fields = __fields, output = outputs.NullOutput()).name('twiggy.devel')

def _del_globals():
    global __fields, log, emitters, __internal_format, __internal_output, internal_log, devel_log
    del __fields, log, emitters, __internal_format, __internal_output, internal_log, devel_log

if 'TWIGGY_UNDER_TEST' not in os.environ: # pragma: no cover
    _populate_globals()

def quick_setup(min_level=levels.DEBUG, file=None, msg_buffer=0, use_shell_format=False):
    """Quickly set up `emitters`.

    :arg `.LogLevel` min_level: lowest message level to cause output
    :arg string file: filename to log to, or ``sys.stdout``, or ``sys.stderr``. ``None`` means standard error.
    :arg int msg_buffer: number of messages to buffer, see `.outputs.AsyncOutput.msg_buffer`
    :arg bool use_shell_format: whether to use default shell_format or line_format, see `.formats`
    """

    if file is None:
        file = sys.stderr

    format = formats.shell_format if use_shell_format else formats.line_format

    if file is sys.stderr or file is sys.stdout:
        output = outputs.StreamOutput(format, stream=file, msg_buffer=msg_buffer)
    else:
        output = outputs.FileOutput(file, format=format, msg_buffer=msg_buffer, mode='a')

    emitters['*'] = filters.Emitter(min_level, True, output)

def add_emitters(*tuples):
    """Add multiple emitters.
    ``tuples`` should be ``(name_of_emitter, min_level, filter, output)``. The last three are passed to :class:`.Emitter`.
    """
    for name, min_level, filter, output in tuples:
        emitters[name] = filters.Emitter(min_level, filter, output)
