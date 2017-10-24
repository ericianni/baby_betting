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

class Bet(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    date = ndb.StringProperty()
    gender = ndb.StringProperty()
    hair_color = ndb.StringProperty()
    length = ndb.IntegerProperty()

class MainPage(webapp2.RequestHanlder):
    pass

class BetHandler(webapp2.RequestHanlder):
    pass

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/bet', Bet),
], debug = True)
