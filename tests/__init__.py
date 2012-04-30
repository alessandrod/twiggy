from datetime import datetime

from twiggy.message import Message
import twiggy

# an arbitrary but consistent time
when = datetime(2010, 10, 28, 2, 15, 57, 301)

def make_mesg():
    return Message(twiggy.levels.DEBUG,
                   "Hello {0} {who}",
                   {'shirt':42, 'name': 'jose'},
                   Message._default_options,
                   args=["Mister"],
                   kwargs={'who':"Funnypants"},
                   )
