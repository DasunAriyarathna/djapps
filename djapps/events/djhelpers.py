
import sys, settings
from django.db.models import Q
import djapps.events.djmodels as evmod
import djapps.dynamo.djmodels as dnmod
import djmodels as evtmod


#################################################################################
#                     Task and Queue realted helper methods                     #
#################################################################################
def get_current_task(queue):
    """ Get the current task in the queue that has not been processed.  """
    tasks = evtmod.DJTask.objects.filter(task_queue = queue).filter(Q(task_status = evtmod.DJTask.TASK_QUEUED) | Q(task_status = evtmod.DJTask.TASK_PROCESSING))
    tasks = tasks.order_by("task_index")

    if tasks: return tasks[0]
    else: return None

def get_task(queue, index):
    """ Get a task in a queue at a particular index. """
    try:
        return evtmod.DJTask.objects.get(task_queue = queue, task_index = index)
    except evtmod.DJTask.DoesNotExist:
        return None

def get_last_task(queue):
    """ Returns the last completed/cancelled queue. """
    tasks = evtmod.DJTask.objects.filter(task_queue = queue).filter(task_status = evtmod.DJTask.TASK_PROCESSING)
    tasks = tasks.order_by("-task_index")

    if tasks: return tasks[0]
    else: return None

