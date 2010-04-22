import time

from .lib import ConversionTable, Converter

# a default converter
line_conversion = ConversionTable([
    Converter(key='time',
              # ISO 8601 - it sucks less!
              convertValue=lambda gmtime: time.strftime("%Y-%m-%dT%H:%M:%S", gmtime),
              convertItem='{1}'.format,
              required=True),
    ('level', str, '{1}'.format, True),
    ('name', str, '{1}'.format),
])

line_conversion.genericValue = str
line_conversion.genericItem = "{0}={1}".format
line_conversion.aggregate = ':'.join

# a converter for use in the shell - no timestamp
shell_conversion = line_conversion.copy()
shell_conversion.get('time').convertItem = lambda k, v: None

class LineFormatter(object):
    """format a message for text-oriented output"""

    def __init__(self, separator=':', traceback_prefix='\nTRACE ',
                 conversion=line_conversion, **kwargs):
        """
        Interesting trick:
        Setting traceback_prefix to '\\n' rolls it up to a single line.

        :ivar conversion: helper to turn a message to a string
        :type conversion: ConversionTable

        """
        self.separator = separator
        self.traceback_prefix = traceback_prefix
        self.conversion = conversion

    def __call__(self, msg):
        fields = self.format_fields(msg)
        text = self.format_text(msg)
        trace = self.format_traceback(msg)
        return "{fields}{self.separator}{text}{trace}\n".format(**locals()) # XXX gross?

    def format_text(self, msg):
        if msg.suppress_newlines:
            return msg.text.replace('\n', '\\n')
        else:
            return msg.text

    def format_traceback(self, msg):
        if msg.traceback is not None:
            # XXX this could be faster
            l = msg.traceback.split('\n')
            l = [""] + l[:-1]
            return self.traceback_prefix.join(l)
        else:
            return ""

    def format_fields(self, msg):
        return self.conversion.convert(msg.fields)