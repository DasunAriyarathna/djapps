
import datetime, random, sha
import smtplib

from google.appengine.ext import db
from google.appengine.api import users
from simplejson.encoder import JSONEncoder as jenc
from simplejson.decoder import JSONDecoder as jdec

"""
The bayeux protocol module.

This is done so that we can either have long-polled or comet-ed connections
to the server from a client.  Which one is supported depends on the server
in which this module is used.  eg if used in the AppEngine, this results in
long-polling!
"""

class Field(object):
    CHANNEL                 = "channel"
    VERSION                 = "version"
    MINVERSION              = "minimumVersion"
    SUPPORTED_CONN_TYPES    = "supportedConnectionTypes"
    ID                      = "id"
    CLIENTID                = "clientId"
    EXT                     = "ext"
    ADVICE                  = "advice"
    AUTHSUCCESSFUL          = "authSuccessful"
    SUCCESSFUL              = "successful"
    CONNECTION_TYPE         = "connectionType"
    SUBSCRIPTION            = "subscription"

# 
# An event.
#
# We use events to denote all notifications, chat messages etc.
#
#
# This is the default user profile, applications can replace this with
# their own items, but they MUST define the ProcessPostData function
#
class Client(db.Model):
    STATE_HANDSHAKEN    = 0
    STATE_CONNECTED     = 1
    STATE_DISCONNECTED  = 2

    # A unique alphanumeric string created by the 
    # server to identify the client.
    clientId        = db.StringProperty()

    # 
    # The user with who the client is associated.
    #
    user            = db.UserProperty()

    # 
    # State of the client
    #
    state           = db.IntegerProperty()

    # 
    # Time when the handshake was recieved.
    #
    handshakeTime   = db.DateTimeProperty(auto_now_add=True)

    # 
    # Date and time this client connection started.
    #
    connectTime     = db.DateTimeProperty(auto_now_add=True)

    # 
    # Date and time this client connection ended.
    #
    endTime         = db.DateTimeProperty(auto_now_add=True)

    # 
    # Version supported by the client.
    #
    version         = db.StringProperty()

    # 
    # Minimum version supported by the client
    #
    minVersion      = db.StringProperty()

    # 
    # A coma separated list of connection type supported by the client
    #
    supportedConnectionType = db.StringProperty()


# 
# An event.
#
# We use events to denote all notifications, chat messages etc.
#
#
# This is the default user profile, applications can replace this with
# their own items, but they MUST define the ProcessPostData function
#
class Event(db.Model):
    # 
    # Which channel does this message belong to?
    #
    channel         = db.StringProperty()

    # 
    # The index of the message.  The channel/index is unique
    #
    index           = db.IntegerProperty()

    # 
    # The actual message.
    #
    payload         = db.StringProperty(default = "")

    # 
    # Who posted the message?
    #
    # null messages are unlabelled messages.
    #
    poster          = db.ReferenceProperty(Client)

    # 
    # Date and time this was posted.  Is this necessary?
    #
    posted_time     = db.DateTimeProperty(auto_now_add=True)

    # 
    # Get the next available index for a message in a given channel
    #
    def get_next_event(channel):
        events  = Event.all()
        index   = 0
        if events.count() > 0:
            events.filter("channel = ", channel)
            events.order("index")
            index = events[:-1].index

        event = Event(channel = channel, index = index)
        event.put()
        return event

    # 
    # TODO: Run this as a transaction
    #
    def dispatch_event(channel, msg_type = 0, message = "", client = None):
        events  = Event.all()
        index   = 0
        if events.count() > 0:
            events.filter("channel = ", channel)
            events.order("index")
            index = events[:-1].index

        event = Event(channel = channel, index = index, payload = message, poster = client)
        event.put()
        return event

# 
# Holds info about a bayeux channel
#
class Channel(db.Model):
    # 
    # Several handshake types
    #
    HANDSHAKE_CHANNEL   =   "/meta/handshake"
    CONNECT_CHANNEL     =   "/meta/connect"
    DISCONNECT_CHANNEL  =   "/meta/disconnect"
    SUBSCRIBE_CHANNEL   =   "/meta/subscribe"
    UNSUBSCRIBE_CHANNEL =   "/meta/unsubscribe"

    # 
    # Name of the channel (including all its segments)
    #
    name    = db.StringProperty()

# 
# For the lack of a better term, this allows us to keep track of a client's
# relationship with a channel.
# This allows us to keep track of the status of events recieved by a
# client, so when new events arrive, only those after a certain point 
# will be resent
#
class ChannelClientInfo(db.Model):
    # 
    # Client whose info we are maintaining
    #
    client  = db.ReferenceProperty(Client)

    # 
    # The channel whose info we are storing
    #
    channel = db.ReferenceProperty(Channel)

    # 
    # The last event recieved by this client 
    # on this channel.  Only updated when a client 
    # calls a "getevents" method
    #
    lastevent   = db.IntegerProperty()

    # 
    # When did the client subscribe to this channel?
    #
    subscribed_at   = db.DateTimeProperty(default = None)

    # 
    # When did the client unsubscribe to this channel?
    #
    unsubscribed_at = db.DateTimeProperty(default = None)

