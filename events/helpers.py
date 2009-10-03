
from django.conf import settings
import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Template

from djapps.utils import json as djjson
import djapps.dynamo.helpers    as dynhelpers
import models     as evtmodels

if settings.USING_APPENGINE:
    from gaehelpers import *
else:
    from djhelpers  import *

def get_or_create_channel(name):
    """ Gets a channel with a given name, and creates if it does not exist.  """
    obj, newcreated = dynhelpers.get_or_create_object(evtmodels.DJChannel, name = name)
    return obj


def get_or_create_client(name):
    """ Gets a client with a given name, and creates if it does not exist.  """
    obj, newcreated = dynhelpers.get_or_create_object(evtmodels.DJClient, name = name)
    return obj


def get_or_create_subscription(client, channel):
    """ Gets a subscription between a client and a channel, 
        and creates if it does not exist.
    """
    obj, newcreated = dynhelpers.get_or_create_object(evtmodels.DJSubscription, client = client, channel = channel)
    return obj

def dispatch_event(subscription, evt_type, evt_data):
    """ Creates a new event and puts in our queue. """
    channel     = subscription.channel
    client      = subscription.client
    evt_data    = djjson.json_encode(evt_data)
    evt_len     = len(evt_data)

    # num_events  = (evt_len / evtmodels.DJEvent.MAX_PAYLOAD_SIZE)
    # if evt_len % evtmodels.DJEvent.MAX_PAYLOAD_SIZE != 0:
        # num_events += 1
    # evt_start   = channel.increment_events(num_events)

    evt_start   = 1
    events      = []
    last_event  = None
    front       = evt_data[ : evtmodels.DJEvent.MAX_PAYLOAD_SIZE]
    fragment    = 0
    while front != "":
        event       = evtmodels.DJEvent(channel = channel, sender = client,
                              index = evt_start, fragment = fragment, # prev_event = last_event,
                              event_type = evt_type, payload = front)
        # evt_start   += 1
        evt_data    = evt_data[evtmodels.DJEvent.MAX_PAYLOAD_SIZE : ]
        front       = evt_data[ : evtmodels.DJEvent.MAX_PAYLOAD_SIZE]
        # if last_event:
            # last_event.next_event = event
        # last_event = event
        fragment    += 1
        events.extend([event])

    dynhelpers.save_objects(*events)

    return events

#################################################################################
#                        All task and queue helper methods                      #
#################################################################################

# 
# TODO: should we do a transaction for this?
#
def create_new_task(queue, owner = None, status = evtmodels.DJTask.TASK_QUEUED):
    """ Creates a new task in a given queue. """
    task_index = dynhelpers.increment_counter(queue)
    return dynhelpers.create_object(evtmodels.DJTask,
                                    True, None, queue + "/" + str(task_index),
                                    task_queue = queue,
                                    task_index = task_index,
                                    task_owner = owner,
                                    task_status = status)

def get_task_by_index(queue, index):
    """ Get the current task in the queue.  """
    return dynhelpers.get_first_object(gfmod.DJTask, task_queue = queue, task_index = index)

