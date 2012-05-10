import datetime, random, sha
import smtplib

from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# 
# Start a chat by a given user
#
def start_chat(user, topic = "Yet another Chat", ispublic = True):
    # 
    # Create the chat
    #
    chat = Chat(started_by = user, chat_topic = topic, is_public = ispublic)
    chat.save()

    # 
    # Add the chatuser as well
    #
    chatuser = ChatUser.objects.get_or_create(chat = chat,
                                              user = user,
                                              role = ChatUser.ROLE_STARTER,
                                              status = ChatUser.PARTICIPATING)
    chatuser.save()

    return chat

# 
# Join chat, by a user.  Only possible if chat is public or if the user has
# been invited or if the user's join request has been accepted
#
def join_chat(chat, user):
    chatuser = None

    # 
    # A public chat - anyone who is not banned can join
    #
    if chat.is_public_readable:
        # 
        # create a user-chat object if it doesnt exist
        #
        chatuser, newcreated    = ChatUser.objects.get_or_create(chat = chat, user = user)

        # 
        # User banned so dont add them
        #
        if chatuser.status == ChatUser.STATUS_BANNED:
            chatuser = None
    else:
        # 
        # not a public chat so only participating, invited or
        # join_request_accepted users can join in
        #
        chatuser, newcreated    = ChatUser.objects.get_or_create(chat = chat, user = user)

        if chatuser.status != ChatUser.STATUS_INVITED and
           chatuser.status != ChatUser.STATUS_JOIN_ACCEPTED and
           chatuser.stauts != ChatUser.STATUS_PARTICIPATING and
           chatuser.status != ChatUser.STATUS_NOT_PARTICIPATING:
           chatuser = None

    if chatuser is not None:
        chatuser.role   = ChatUser.ROLE_PARTICIPANT
        chatuser.status = ChatUser.STATUS_PARTICIPATING
        chatuser.save()

    return chatuser

# 
# Invite one or more users to a chat
#
def invite_user_to_chat(chat, inviter, *users):
    numinvited = 0

    try:
        chatinviter = ChatUser.object.get(chat = chat, user = inviter)

        for user in users:
            # cannot invite ourselves!
            if inviter != user:
                chatuser, newcreated = ChatUser.objects.get_or_create(chat = chat, user = user)

                if chatuser.status == ChatUser.STATUS_NONE:
                    chatuser.status = ChatUser.STATUS_INVITED
                    chatuser.inviter = inviter
                    chatuser.save()

                    numinvited = numinvited + 1

                    # 
                    # TODO: send email to user with an invite or any other mode of
                    # message - eg FB, MYSPACE, SMS etc.
                    #
    except:
        pass

    return numinvited

# 
# Kick one or more users out of the chat.
#
def kick_user_from_chat(chat, kicker, *user):
    numkicked = 0

    try:
        chatkicker = ChatUser.object.get(chat = chat, user = inviter)
        for user in users:
            # cannot kick ourselves!
            if kicker != user:
                chatuser, newcreated = ChatUser.objects.get_or_create(chat = chat, user = user)

                if chatkicker.role < chatuser.role and
                   chatuser.status == ChatUser.STATUS_NONE:
                    chatuser.status = ChatUser.STATUS_BANNED
                    chatuser.inviter = inviter
                    chatuser.save()

                    numkicked = numkicked + 1
    except:
        pass

    return numkicked

# 
# Request to join the chat by a user
#
def request_to_join_chat(chat, requestor):
    chatuser, newcreated = ChatUser.object.get_or_create(chat = chat, user = inviter)
    if chatuser.status == ChatUser.STATUS_NONE:
        chatuser.status = ChatUser.STATUS_JOIN_REQUESTED
        chatuser.save()
    return chatuser

# 
# Accept or reject the join request by a requestor
#
def accept_or_reject_join_request(chat, admin, requestor, accept):
    chatuser = None
    try:
        chatuser = ChatUser.object.get(chat = chat, user = inviter)
        if chatuser.status == ChatUser.STATUS_JOIN_REQUESTED:
            if accept:
                chatuser.status = ChatUser.STATUS_JOIN_REQUEST_ACCEPTED
            else:
                chatuser.status = ChatUser.STATUS_JOIN_REQUEST_REJECTED
    except:
        pass

    return chatuser

# 
# Posts a chat message by a given user into a chat
#
def post_chat_message(chat, user = None, message = ""):
    try:
        chatuser = ChatUser.object.get(chat = chat, user = user)
        if user.status == ChatUser.STATUS_PARTICIPATING:

            index = chat.increment_msg_count()

            numfrags = len(message) / ChatMessage.MSG_LEN
            for fragment in xrange(0, numfrags, 1):
                head = message[:MSG_LEN]
                tail = message[MSG_LEN:]

                # create the message fragment
                msg = ChatMessage(thechat = chat, posted_by = user, message = message, index = index, fragment = fragment)
                msg.save()
                chat.messages.append(msg)
                chat.save()
    except:
        pass

# 
# Gets the messages in a chat
# 
# \param    chat        Which chat is being queried.
# \param    user        The user who is requesting the info.
# \param    user_filter Get messages by these users 
#                       - if none then all users.
# \param    time_filter Get messages "after" this time.
#                       - if none then get all messages.
#
def get_messages(chat, user, user_filter = None, time_filter):
    pass

