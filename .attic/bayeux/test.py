
import logging
import os
import cgi
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# YUI_LOC = "http://yui.yahooapis.com/2.5.1"
YUI_LOC = "/ext/yui"

def render_template(page, tmpl_file, template_values = {}):
    path = os.path.join(os.path.dirname(__file__), tmpl_file)
    template_values['yui_loc'] = YUI_LOC
    page.response.out.write(template.render(path, template_values))

class MainPage(webapp.RequestHandler):
    def get(self):
        render_template(self, '../templates/bayeux/index.html')
