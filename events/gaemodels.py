
from google.appengine.ext import db
from google.appengine.api.users import User
import datetime, settings
from djapps.gaeutils.sessions import Session
import djapps.auth.external.models as djauth

# 
# A task that will be queued to be performed by the server asynchronously.
# The parameters for the task will be the "extendible" data.
#
# Also another issue is who access to the task results?  We dont want
# "hidden" tasks to be visible to everyone.
#
class DJTask(db.Model):
    # 
    # Types of allowable task statusii
    #
    TASK_QUEUED     = 0
    TASK_PROCESSING = 1
    TASK_COMPLETED  = 2
    TASK_KILLED     = 3

    # 
    # Which queue does this task belong to?
    #
    task_queue  = db.StringProperty(required = True)

    # 
    # Index of the task
    #
    task_index  = db.IntegerProperty(default = 0)

    # 
    # The type of task - usually a theme may create a different type of
    # move data dependin on this -eg AttackMove, MovementMove, HealMove etc
    #
    task_type   = db.IntegerProperty(default = 0)

    # 
    # When task was created
    #
    task_status = db.IntegerProperty(default = TASK_QUEUED)

    # 
    # Result of the task (upon completion)
    #
    task_result  = db.IntegerProperty(default = 0)

    # 
    # Which user triggered this task?
    #
    task_owner  = db.ReferenceProperty(djauth.UserAlias)

    # 
    # When task was created
    #
    task_created    = db.DateTimeProperty(auto_now_add = True)

# 
# A messaging channel.
#
# Clients subscribe to this channel and recieve and send messages to it.
#
class DJChannel(db.Model):
    # 
    # Several builting channels.
    #
    HANDSHAKE_CHANNEL   =   "/meta/handshake"
    CONNECT_CHANNEL     =   "/meta/connect"
    DISCONNECT_CHANNEL  =   "/meta/disconnect"
    SUBSCRIBE_CHANNEL   =   "/meta/subscribe"
    UNSUBSCRIBE_CHANNEL =   "/meta/unsubscribe"

    # 
    # Name of the channel - unique
    #
    name    =   db.StringProperty()

    # 
    # Number of events/messages in this channel.  Will be incremented by
    # one each time a new event is added.
    #
    numevents   = db.IntegerProperty(default = 0)

    def increment_events(self, incr = 1):
        """ Increments the event counter by a given number of events. """
        def tx(channel, incr):
            channel.numevents += incr
            channel.put()
        db.run_in_transction(self, incr)

    # 
    # String representation
    #
    def __str__(self):
        return "Channel: %s, NumEvents: %d" % (self.name, self.numevents)

    @classmethod
    def create(cls, name):
        Unique.check("name", name)
        channel = DJChannel(name = name)
        channel.put()
        return channel

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

class DJClient(db.Model):
    # name of the client - unique
    name        = db.StringProperty()

    @classmethod
    def create(cls, name):
        Unique.check("name", name)
        client = DJClient(name = name)
        client.put()
        return client

    # 
    # String representation
    #
    def __str__(self):
        return "Client: %s" % self.name

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

class DJSubscription(db.Model):
    # 
    # Who is the client subscribing to the channel?
    #
    client          = db.ReferenceProperty(DJClient)

    # 
    # Which channel is this client connected to?
    #
    channel         = db.ReferenceProperty(DJChannel)

    # 
    # Last message recieved by the client.  For ease, so that the client
    # can only fetch messages from this point onwards.
    #
    lastmsg         = db.IntegerProperty(default = 0)

    # 
    # When did the client subscribe to this channel?
    #
    subscribed_at   = db.DateTimeProperty(auto_now_add = True)

    # 
    # When did the client unsubscribe to this channel?
    #
    unsubscribed_at = db.DateTimeProperty(auto_now_add = True)

    # 
    # client/channel is unique
    #
    unique_together = ("client", "channel")

    # 
    # String representation
    #
    def __str__(self):
        return "%s -> %s" % (self.client, self.channel)

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

class DJEvent(db.Model):
    # 
    # Maximum size of the event payload
    #
    MAX_PAYLOAD_SIZE = 512
    
    # 
    # Channel where this event either originates from or is targeted to.
    #
    channel = db.ReferenceProperty(DJChannel);

    # 
    # Who is the sender of the message? Can be null
    #
    sender      = db.ReferenceProperty(DJClient)

    # 
    # Index of the message.  channel/index is unique.  How to get a unique
    # index?
    #
    index       = db.IntegerProperty()

    # 
    # The fragment of the event - an event can actually be divided into
    # multiple fragments if they exceed the payload size.
    #
    fragment    = db.IntegerProperty(default = 0)

    # 
    # The dependent event.  This event cannot have happend without the
    # parnet happening!
    #
    # Is this necessary?  Idea is that to have moves/events that can be
    # "undone", so if a parent is null then the event can be undone.  Or
    # should it be the case that an event cannot be undone if it has child
    # events, which means we wanna have another table for this
    # relationship?
    #
    # parent      = db.ReferenceProperty(DJEvent)

    # 
    # Date and time this was posted.  Is this necessary or can we remove
    # the index and sort messages by index?
    #
    posted_time = db.DateTimeProperty(auto_now_add = True)

    #
    # The event type or id - must be unique for each event type (within a
    # channel) for identification purposes.
    #
    # Only rule of thumb is -ve for system events and >= 0 for game/theme
    # specific messages
    #
    event_type  = db.IntegerProperty(default = 0) 

    # 
    # The payload!  Events cannot be longer than 512 chars. otherwise
    # resort to bob and attributes.
    #
    payload     = db.StringProperty(default = "")

    # 
    # Class meta data
    #
    class Meta:
        order_with_respect_to = "channel"
        ordering = ["index", "fragment"]

    unique_together = ("channel", "index", "fragment")

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

