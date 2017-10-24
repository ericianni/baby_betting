import os
import webapp2
import jinja2
import urllib
import json

# Globals

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DUE_DATE = "11-19-2017"
CUT_OFF_DATE = "11-01-2017"
BASE_URL = "https://Ianni-baby-2.appspot.com"

class Bet(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    date = ndb.StringProperty(required=True)
    gender = ndb.StringProperty(required=True)
    hair_color = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)

class MainPage(webapp2.RequestHanlder):
    def get(self):
        self.response.write("Hello")

class BetHandler(webapp2.RequestHanlder):
    pass

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/bet', Bet),
], debug = True)
