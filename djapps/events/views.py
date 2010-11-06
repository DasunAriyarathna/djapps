
import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Template

import  djapps.utils.decorators     as  djdecos
import  djapps.utils.request        as  djrequest
from    djapps.utils    import          api_result
import  models                      as  evtmodels


# 
# Gets events from a given channel.
#
@djdecos.ensure_request_type(["GET"])
def get_events(request, channel):
    events      = evtmodels.DJEvent.objects.filter(channel = channel)

    startevent  = 0
    numevents   = -1

    if request.GET:
        startevent  = int(request.GET["start"]) if "start" in request.GET else 0
        numevents   = int(request.GET["count"]) if "count" in request.GET else -1
        

    if numevents == 1:
        events = events.filter(index = startevent)
    else:
        if startevent > 0:
            events = events.filter(index__gte = startevent)

        if numevents > 0:
            events = events.filter(index__lt = startevent + numevents)

    # is this required since we are doing the ordering in the db itself?
    events = events.order_by("index").order_by("fragment")

    return api_result(0, [{'sender': e.sender.clientId, 'index': e.index,
                           'fragment': e.fragment, 'type': e.event_type,
                           'payload': e.payload, 'time': e.posted_time} for e in events])

