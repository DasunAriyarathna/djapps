from django.db import models
from django.contrib.auth.models import User

# 
# A simple chat.
#
class Chat(models.Model):
    # 
    # Who was it started by?
    #
    started_by      = models.ForeignKey(User)

    # 
    # When was the chat started.
    #
    date_started    = models.DateTimeField(default = datetime.datetime.now)

    # 
    # Number of messages in this chat.
    #
    msg_count       = models.IntegerField(default = 0)

    # 
    # The messages in the chat.
    #
    messages        = models.ManyToManyField("ChatMessage")

    # 
    # Topic for the chat
    #
    chat_topic      = models.CharField(maxlength = 256, default = "Yet another Chat")

    # 
    # Is the chat publicly readable
    #
    is_public_readable  = models.BooleanField(default = True)

    # 
    # Join mode - 
    # 0 - Anyone can join without invite
    # 1 - People can only be invited
    # 2 - People can join but only if accepted by the 
    #     starter (or admin) of the chat.
    #
    join_mode           = models.IntegerField(default = 0)

    # 
    # Increment the message count and return the old count.
    # TODO: Check for concurrency and make it a transaction
    #
    def increment_msg_count(self):
        old = self.msg_count
        self.msg_count = self.msg_count + 1
        self.save()
        return old

    # 
    # String representation.
    #
    def __str__(self):
        return self.chat_topic + " by " + str(started_by) + " at " + str(date_started)

    # 
    # Unicode representation.
    #
    def __unicode__(self):
        return self.chat_topic + " by " + str(started_by) + " at " + str(date_started)

    # 
    # Specify model ordering
    #
    class Meta:
        ordering = ['chart_topic', 'date_started']

    # 
    # Class to enable admin access
    #
    class Admin:
        save_on_top = True
        list_display = ('chat_topic', 'started_by', 'date_started', 'is_public_readable')

# 
# A table that maintains which users are in 
# which chat in which capacity
#
class ChatUser(models.Model):
    ROLE_STARTER        = 0
    ROLE_ADMIN          = 1
    ROLE_PARTICIPANT    = 2

    STATUS_NONE                     = 0
    STATUS_PARTICIPATING            = 1
    STATUS_NOT_PARTICIPATING        = 2
    STATUS_INVITED                  = 3
    STATUS_JOIN_REQUESTED           = 4
    STATUS_JOIN_REQUEST_ACCEPTED    = 5
    STATUS_JOIN_REQUEST_REJECTED    = 6
    STATUS_BANNED                   = 7

    # 
    # The chat we are referring to
    #
    chat    = models.ForeignKey(Chat)

    # 
    # The user that is part of the chat
    #
    # Primary key is the chat/user combination
    #
    user    = models.ForeignKey(User)

    # 
    # Role of the user:
    #
    # 0 - Starter
    # 1 - Admin
    # 2 - Participant
    #
    # These are define roles.  Others can be availble in app specific
    # ways.
    # 
    # TODO: We can make higher numbers mean less priviledges.
    #
    role    = models.IntegerField(default = ROLE_PARTICIPANT)

    # 
    # The status of the user in this chat.
    # Look at STATUS_* for values and their meanings.
    #
    status  = models.IntegerField(default = STATUS_NONE)

    # 
    # When did the user join the chat?
    #
    date_joined = models.DateTimeField(
    posted_time     = models.DateTimeField(default = datetime.datetime.now)

    # 
    # String representation.
    #
    def __str__(self):
        return "%s - %s - %s - %s" % (self.chat, self.user, self.role, self.status)

    # 
    # Unicode representation.
    #
    def __unicode__(self):
        return "%s - %s - %s - %s" % (self.chat, self.user, self.role, self.status)

    # 
    # Specify model ordering
    #
    class Meta:
        ordering = ['chat', 'user', 'role', 'status']

    # 
    # Class to enable admin access
    #
    class Admin:
        save_on_top = True
        list_display = ('chat', 'user', 'role', 'status')

#
# This is the default user profile, applications can replace this with
# their own items, but they MUST define the ProcessPostData function
#
class ChatMessage(models.Model):
    MSG_LEN         = 256

    # 
    # Which chat does this message belong to?
    #
    thechat         = models.ForeignKey(Chat)

    # 
    # The index of the message.  The thechat/index/fragment is unique
    #
    index           = models.IntegerField()

    # 
    # Fragment of the message, if the message is broken up into multiple
    # fragements due to its size.
    #
    fragement       = models.IntegerField()

    # 
    # Who posted the message?
    #
    # null messages are unlabelled messages.
    #
    posted_by       = models.ForeignKey(User, null = True)

    # 
    # Format of the message.
    # This is app dependant - 
    # 0 = plain text,
    # anything else is upto the app, eg 1 = html and so on.
    format          = models.IntegerField(default = 0)

    # 
    # The actual message
    #
    message         = models.CharField(maxlength = MSG_LEN, default = "")

    # 
    # Date and time this was posted
    #
    posted_time     = models.DateTimeField(default = datetime.datetime.now)

    # 
    # String representation.
    #
    def __str__(self):
        return "%d/%d - [%s] by (%s @ %s)" % (self.index, self.fragment, self.message , self.posted_by, str(self.posted_time))

    # 
    # Unicode representation.
    #
    def __unicode__(self):
        return "%d/%d - [%s] by (%s @ %s)" % (self.index, self.fragment, self.message , self.posted_by, str(self.posted_time))

    # 
    # Specify model ordering
    #
    class Meta:
        ordering = ['thechat', 'index', 'fragment']

    # 
    # Class to enable admin access
    #
    class Admin:
        save_on_top = True
        list_display = ('thechat', 'index', 'fragment', 'posted_time', 'message')

