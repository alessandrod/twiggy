__all__=['log']

import Logger
emitters = Logger.emitters
log = Logger.log

from Levels import *

#log.name('pants').fields(shirt=42, request_id='webtastic').info('Frobbing {0} with great {adj}', 666, 'temptation')
#log.name('structure').fields(numcalls=82, params = someargs).info()