from distutils.core import setup

setup(name="Djapps",
      version="0.0.1",
      description="A few utility apps to be used with django in class mode and in appengine mode",
      author="Sri Panyam",
      author_email="sri.panyam@gmail.com",
      url="http://code.google.com/p/djapps/",
      packages = [
          "djapps", 
          "djapps/auth", 
          "djapps/auth/external", 
          "djapps/auth/external/hosts", 
          "djapps/auth/external/hosts/fb", 
          "djapps/auth/external/hosts/iphone", 
          "djapps/auth/external/hosts/myspace", 
          "djapps/auth/external/hosts/twitter", 
          "djapps/auth/external/sites", 
          "djapps/auth/local", 
          "djapps/auth/openid", 
          "djapps/dynamo", 
          "djapps/events", 
          "djapps/gaeutils", 
          "djapps/gaeutils/contrib", 
          "djapps/gaeutils/contrib/auth", 
          "djapps/payments", 
          "djapps/payments/paypal", 
          "djapps/utils", 
          "djapps/utils/gae", 
          "djapps/utils/templatetags", 
      ]
      )
    
