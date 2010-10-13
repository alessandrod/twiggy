__all__=['log', 'emitters', 'addEmitters', 'devel_log', 'filters', 'formats', 'outputs', 'levels', 'quickSetup']
import time
import sys

import logger
import filters
import formats
import outputs
import levels

## a useful default fields
__fields = {'time':time.gmtime}

log = logger.Logger(__fields)

emitters = log._emitters

__internal_format = formats.LineFormat(conversion = formats.line_conversion)
__internal_output = outputs.StreamOutput(format = __internal_format, stream=sys.stderr)

internal_log = logger.InternalLogger(fields = __fields, output=__internal_output).name('twiggy.internal')

devel_log = logger.InternalLogger(fields = __fields, output = outputs.NullOutput()).name('twiggy.devel')

def quickSetup(min_level=levels.DEBUG, file = None, msg_buffer = 0):
    """Quickly set up `emitters`.

    :arg `.LogLevel` min_level: lowest message level to cause output
    :arg string file: filename to log to, or ``sys.stdout``, or ``sys.stderr``. ``None`` means standard error.
    :arg int msg_buffer: number of messages to buffer, see `.outputs.AsyncOutput.msg_buffer`
    """

    if file is None:
        file = sys.stderr

    if file is sys.stderr or file is sys.stdout:
        output = outputs.StreamOutput(formats.shell_format, stream=file)
    else:
        output = outputs.FileOutput(file, format=formats.line_format, msg_buffer=msg_buffer, mode='a')

    emitters['*'] = filters.Emitter(min_level, True, output)

def addEmitters(*tuples):
    """Add multiple emitters.
    ``tuples`` should be ``(name_of_emitter, min_level, filter, output)``. The last three are passed to :class:`.Emitter`.
    """
    for name, min_level, filter, output in tuples:
        emitters[name] = filters.Emitter(min_level, filter, output)
