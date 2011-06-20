
from django.contrib.auth import REDIRECT_FIELD_NAME

def login(request, redirect_field_name = REDIRECT_FIELD_NAME):
    """
    This URL is what facebook first calls when it first shows in its
    canvas.  FB will send the signature and other authentication parameters
    here.  Note that this same URL can be sent by our own non-iframed app
    when we are using FB Connect.
    """
    pass

def post_auth(request):
    """
    Called by FB when a user first autherizes the application.
    """
    pass

def post_remove(request):
    """
    Pinged by FB when a user removes the application.
    """
    pass

def info_update(request):
    """
    Pinged by FB when a user changes data in the application's info section
    on their profile.
    """
    pass

def publish(request):
    """
    Facebook pulls the content for your users' friends' Publisher interface
    from here.
    """
    pass

def self_publish(request):
    """
    Facebook pulls the content for your user's Publisher interface from
    here.
    """
    pass
