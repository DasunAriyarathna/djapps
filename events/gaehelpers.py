
from google.appengine.ext import db
from google.appengine.api.users import User
import datetime, settings
import djapps.auth.external.models as djauth
import gaemodels as evmodels

#################################################################################
#                     Task and Queue realted helper methods                     #
#################################################################################
def get_current_task(queue):
    """ Get the current task in the queue that has not been processed.  """
    query = evmodels.DJTask.all()
    query.filter("task_queue = ", queue)
    query.filter("task_status <= ", evmodels.DJTask.TASK_PROCESSING)
    query.order("-task_status")
    query.order("task_index")
    if query.count() > 0: return query.fetch(1)
    else: return None

def get_task(queue, index):
    """ Get a task in a queue at a particular index. """
    return evmodels.DJTask.get_by_key_name(queue + "/" + str(index))

def get_last_task(queue):
    """ Returns the last completed/cancelled queue. """
    query = evmodels.DJTask.all()
    query.filter("task_queue = ", queue)
    query.filter("task_status == ", evmodels.DJTask.TASK_PROCESSING)
    query.order("-task_index")
    if query.count() > 0: return query.fetch(1)
    else: return None

