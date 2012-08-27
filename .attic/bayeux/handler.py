import logging
import datetime, random, sha
import smtplib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from simplejson.encoder import JSONEncoder as jenc
from simplejson.decoder import JSONDecoder as jdec

import bayeux

class BayeuxHandler(webapp.RequestHandler):
    """
    The bayeux server.
    """
    def __init__(self):
        """ Constructor """
        self.supportedConnectionTypes   = ["long-polling","callback-polling"]
        self.version                    = "0.1"
        self.publish_handlers           = [self.pre_publish, self.publish, self.post_publish]
        self.request_handlers           =   \
            {bayeux.Channel.HANDSHAKE_CHANNEL:
                {'handlers':
                    [self.pre_handshake, self.handshake, self.post_handshake],
                 'post_handler': self.post_handshake,
                 'attribs':
                    [bayeux.Field.VERSION, bayeux.Field.SUPPORTED_CONN_TYPES]},
             bayeux.Channel.CONNECT_CHANNEL:
                {'handlers':
                    [self.pre_connect, self.connect, self.post_connect],
                 'post_handler': self.post_connect,
                 'attribs':
                    [bayeux.Field.CLIENTID, bayeux.Field.CONNECTION_TYPE,
                    bayeux.Field.SUPPORTED_CONN_TYPES]},
             bayeux.Channel.DISCONNECT_CHANNEL:
                {'handlers':
                    [self.pre_disconnect, self.connect, self.post_disconnect],
                 'attribs': [bayeux.Field.CLIENTID ]},
             bayeux.Channel.SUBSCRIBE_CHANNEL:
                {'handlers':
                    [self.pre_subscribe, self.connect, self.post_subscribe],
                 'attribs': [bayeux.Field.CLIENTID, bayeux.Field.SUBSCRIPTION]},
             bayeux.Channel.UNSUBSCRIBE_CHANNEL:
                {'handlers':
                    [self.pre_unsubscribe, self.connect, self.post_unsubscribe],
                 'attribs': [bayeux.Field.CLIENTID, bayeux.Field.SUBSCRIPTION]}
            }

    def get(self):
        """ Handles GET messages.  The message is stored in the url
        parameter 'message' """

        result, response = self.handle_request(self.request.get('message'))

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(jenc().encode({'success': result, 'value': response}))

    def post(self):
        """ Handles POST messages.  Here the message is either the body of
        the POST request if the encoding type is "text/json" or as the
        value of the 'message' parameter if the encoding is
        "application/x-www-form".  If neither of these are found, then we
        have an error. """

        contenttype = self.request.headers['Content-Type']
        if contenttype == 'application/x-www-form':
            result, response = self.handle_request(self.request.get('message'))
        elif contenttype == 'text/json':
            result, response = self.handle_request(self.request.body)
        else:
            result, response = False, "Invalid encoding: " + contenttype 

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(jenc().encode({'success': result, 'value': response}))

    def error_response(self, channel, msg):
        """
        Creates and formats an error response.
        """
        return {'channel': channel, 'version': self.version, 'successful': False, 'error': msg}


    def handle_request(self, message):
        """ 
        Handle a request and return a response.
        This method calls respective handlers for each handler.  Child
        classes inheriting the BayeuxServer can override the behaviour of
        the request handlers.
        """

        if type(message) is str:
            try:
                message = jdec().decode(message)
            except:
                return False, "Invalid JSON Object"

        if not message:
            return False, "Invalid or empty message"

        if Field.CHANNEL not in message:
            return False, "Channel not found in message"

        channel = message[Field.CHANNEL]

        handlers = self.publish_handlers

        if channel in self.request_handlers:
            handler = self.request_handlers[channel]

        # 
        # Check for mandatory attributes
        #
        attribs = handler['attribs']
        attribs = filter(lambda x: attribs[x] in request, attribs)
        if attribs:
            return self.error_response("Missing fields: " + ", ".join(attribs))

        # 
        # Run the pre handlers
        #
        result, response = True, ""
        for handler in handlers:
            result, response = handler(channel, clientid, request)
            if not result:
                break
        
        return result, response

    def pre_handshake(self, channel, clientid, request):
        """
        Called before a handshake is performed.
        """
        return True, ""

    def handshake(self, channel, clientid, request):
        """
        Handle a request to handshake by a user.
        """
        return True, ""

    def post_handshake(self, channel, clientid, request):
        """
        Called after a handshake is successfully handled.
        """
        return True, ""

    def pre_connect(self, channel, clientid, request):
        """
        Called before a connection is performed.
        """
        return True, ""

    def connect(self, channel, clientid, request):
        """
        Handle a request to connect a user.
        """
        return True, ""

    def post_connect(self, channel, clientid, request):
        """
        Called after a connection is successfully handled.
        """
        return True, ""

    def pre_disconnect(self, channel, clientid, request):
        """
        Called before a disconnection is performed.
        """
        return True, ""

    def disconnect(self, channel, clientid, request):
        """
        Handle a request to disconnect a user.
        """
        return True, ""

    def post_disconnect(self, channel, clientid, request):
        """
        Called after a disconnection is successfully handled.
        """
        return True, ""

    def pre_subscribe(self, channel, clientid, request):
        """
        Called before an subscription is performed.
        """
        return True, ""

    def subscribe(self, channel, clientid, request):
        """
        Handle a request subscribe to a channel.
        """
        return True, ""

    def post_subscribe(self, channel, clientid, request):
        """
        Called after the subscribe is successfully handled.
        """
        return True, ""

    def pre_unsubscribe(self, channel, clientid, request):
        """
        Called before an unsubscription is performed.
        """
        return True, ""

    def unsubscribe(self, channel, clientid, request):
        """
        Handle a request subscribe to a channel.
        """
        return True, ""

    def post_unsubscribe(self, channel, clientid, request):
        """
        Called after the unsubscribe is successfully handled.
        """
        return True, ""

    def pre_publish(self, channel, clientid, request):
        """
        Called before an event is published.
        """
        return True, ""

    def publish(self, channel, clientid, request):
        """
        Handle a request to publish a message to a channel.
        """
        return True, ""

    def post_publish(self, channel, clientid, request):
        """
        Called after the publish handler is successfully called.
        """
        return True, ""

    def deliver(self, channel, clientid, request):
        """
        Deliver a message to all recievers.  This will actually be called
        by the client on a non-cometed server.
        """
        return True, ""

