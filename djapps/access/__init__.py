
"""
This new authentication module (also) allow access to the site via external
authentication mechanisms.  Previously this was done with the concept of
user aliases.  Using user aliases a user could be logged into a site with
multiple externally authenticated users - eg from FB, google, twitter etc.
While this was good, it had the following problems:

1. It meant the client had to keep track of all logins and this was cumbersome.  
2. This did not extend to permissions for actions.  ie only logins
were allowed by there was no way to manage granular permissions based on
actions.  eg just logging into FB meant we had to request access to
everything (like posting to the wall, feed etc).
3. Perhaps the biggest issue was that it conflicted with django's User
object.  UserAlias was now the main object and instead of having one User
object per request we had multiple ones.  So all django apps that
require(d) a User object would not work as they could not recognise the
UserAlias object (or a User object if it needed to be patched with a
host_site field).

The goal of this module is two things:
1. Simplify the authentication process.  As far as the user is concerned,
login has to be a single action.  No messy management of multiple site
(specific auths) or multiple logouts etc.
2. On Demand Granularity - user must be able to select at all times how
narrow or wide the permissions he/she grants are (as long as the
granularity is allowed by the external site).
3. Bring the focus back to the User object.  This is a goodie for
developers and other apps.  So that we could still do facebook
or twitter sign-ins but still use the admin site with this login!  This
naturally has to work in google AND in django - essentially in any
framework there is a central User object.
"""
