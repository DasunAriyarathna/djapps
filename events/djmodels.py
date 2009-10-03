
from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import admin as djangoadmin
from django.utils.translation import ugettext_lazy as _
from djapps.dynamo import djmodels as djmod
import djapps.auth.external.models as djauth
import datetime

# 
# A task that will be queued to be performed by the server asynchronously.
# The parameters for the task will be the "extendible" data.
#
# Also another issue is who access to the task results?  We dont want
# "hidden" tasks to be visible to everyone.
#
class DJTask(models.Model):
    # 
    # Types of allowable task statusii
    #
    TASK_QUEUED     = 0
    TASK_PROCESSING = 1
    TASK_COMPLETED  = 2
    TASK_KILLED     = 3

    # 
    # Primary key = task_queue + "/" + index
    #
    key_name        = models.CharField(max_length = 266, primary_key = True)

    # 
    # Which queue does this task belong to?
    #
    task_queue      = models.CharField(max_length = 256)

    # 
    # Index of the task
    #
    task_index      = models.IntegerField(default = 0)

    # 
    # The type of task - usually a theme may create a different type of
    # move data dependin on this -eg AttackMove, MovementMove, HealMove etc
    #
    task_type       = models.IntegerField(default = 0)

    # 
    # Status of this move
    #
    task_status     = models.IntegerField(default = TASK_QUEUED)

    # 
    # Result of the task (upon completion)
    #
    task_result     = models.IntegerField(default = 0)

    # 
    # Which user triggered this task?
    #
    task_owner      = models.ForeignKey(djauth.UserAlias, null = True)

    # 
    # When task was created
    #
    task_created    = models.DateTimeField(default = datetime.datetime.now)

    unique_together = ("task_queue", "task_index")

    class Meta: ordering = ('task_queue', 'task_index')
    class Admin: save_on_top = True

class DJSubscription(models.Model):
    # Who is the client subscribing to the channel?
    client          = models.CharField(max_length = 128)

    # name of the channel this client is connected to?
    channel         = models.CharField(max_length = 128)

    # Last message recieved by the client.  For ease, so that the client
    # can only fetch messages from this point onwards.
    lastmsg         = models.IntegerField(default = 0)

    # 
    # When did the client subscribe to this channel?
    #
    subscribed_at   = models.DateTimeField(_('subscribed at'), default=datetime.datetime.now)

    # 
    # When did the client unsubscribe to this channel?
    #
    unsubscribed_at = models.DateTimeField(_('unsubscribed at'), default=datetime.datetime.now)

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

class DJEvent(models.Model):
    # Channel where this event either originates from or is targeted to.
    channel         = models.CharField(max_length = 128)

    # Who is the sender of the message? Can be null
    client          = models.CharField(max_length = 128, null = True)

    # The event type
    event_type  = models.IntegerField(default = 0) 

    # Index of the message.  channel/index is unique.  How to get a unique
    # index?
    index       = models.IntegerField()

    # 
    # The fragment of the event - an event can actually be divided into
    # multiple fragments if they exceed the payload size.
    #
    fragment    = models.IntegerField(default = 0)

    # Date and time this was posted.  Is this necessary or can we remove
    # the index and sort messages by index?
    posted_time = models.DateTimeField(_('posted time'), default=datetime.datetime.now)

    # 
    # Class meta data
    #
    class Meta:
        # order_with_respect_to = "channel"
        ordering = ["channel", "index"]

    unique_together = ("channel", "index")

    # Admin Interface
    class Admin: save_on_top = True

try:
    from django.contrib.admin.sites import AlreadyRegistered
    djangoadmin.site.register(DJSubscription)
    djangoadmin.site.register(DJEvent)
    djangoadmin.site.register(DJTask)
except AlreadyRegistered, ar:
    print "Already registered..."

