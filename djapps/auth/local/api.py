
from django.conf import settings
from djapps.utils import mail as djmail
from djapps.dynamo.helpers import get_or_create_object, save_object
from djapps.utils import urls as djurls

if settings.USING_APPENGINE:
    from gaeapi import *
    from gaemodels import LocalUser
else:
    from djapi import *
    from django.contrib.auth.models import User as LocalUser

# 
# Quick way to register a user to the local site.
#
def register_user(username, email, password, 
                 firstname = "", lastname = "", displayname = "",
                 is_active = True, request = None,
                 register_timeout = 2, form_context = {},
                 UserClass = LocalUser, UserRegClass = models.LocalUserRegistration, 
                 email_template     = None, 
                 email_host         = "localhost",
	             email_port         = 25,
	             email_username     = "",
	             email_password     = "",
	             email_from         = "accounts@thisserver.com",
	             email_subject      = "Your Account Confirmation",
                 ):
    reg_info = None
    new_user, newcreated    = get_or_create_object(UserClass, False, username = username, email = email)
    if newcreated:
        new_user.username       = username
        new_user.email          = email
        new_user.first_name     = firstname
        new_user.last_name      = lastname
        new_user.is_active      = is_active
        set_password(new_user, password)

        save_object(new_user)

        # create a registration object whether user is active or not
        # as this is what will hold the user's password
        if not is_active:
            import random, sha
            salt                    = sha.new(str(random.random())).hexdigest()[:5]
            activation_key          = sha.new(salt + new_user.email).hexdigest()
            key_expires             = datetime.datetime.today() + datetime.timedelta(register_timeout)
            reg_info, newcreated    = get_or_create_object(UserRegClass, False, user = new_user, activation_key = activation_key)
            reg_info.user           = new_user
            reg_info.key_expires    = key_expires
            save_object(reg_info)

            if email_template:
                from django.template import Context, RequestContext, loader
                emailtemplate   = loader.get_template(email_template)
                
                if request:
			        email_context    = RequestContext(request,
			                                        {'reg_info': reg_info,
			                                         'site_domain': djurls.get_site_url(),
			                                         'confirm_uri': form_context['href_uri']['confirm'],
			                                         'register_timeout': register_timeout})
                else:
			        email_context    = Context({'reg_info': reg_info,
			                                    'site_domain': djurls.get_site_url(),
			                                    'confirm_uri': form_context['href_uri']['confirm'],
			                                    'register_timeout': register_timeout})
                msgbody         = emailtemplate.render(email_context)

                djmail.send_mail(new_user.email, email_from, email_subject,
                                msgbody, email_host, email_port, email_username,
                                email_password)
    return new_user, reg_info, newcreated

