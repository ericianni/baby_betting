from google.appengine.ext import ndb
from gaesessions import get_current_session
import os
import webapp2
import jinja2
import urllib
import json
import datetime
import hashlib

# Globals

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DUE_DATE = "11-19-2017"
CUT_OFF_DATE = "11-01-2017"
BASE_URL = "https://Ianni-baby-2.appspot.com"

class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    date = ndb.StringProperty()
    time = ndb.StringProperty()
    gender = ndb.StringProperty()
    hair_color = ndb.StringProperty()
    length = ndb.IntegerProperty()
    pounds = ndb.IntegerProperty
    ounces = ndb.IntegerProperty
    
class MainPage(webapp2.RequestHandler):
    def get(self):

        # Session Handling
        session = get_current_session()
        user = session.get('user', None)
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        title = "Ianni Baby 2.0"
        if user:
            logged_in = True
        else:
            logged_in = False
        template_values = {
            'user':user,
            'title':title,
            'logged_in':logged_in
        }
        self.response.write(template.render(template_values))

class BetHandler(webapp2.RequestHandler):
    def get(self):
        # Session Handling
        session = get_current_session()
        user = session.get('user', None)
        email = session.get('user_email', None)
        bet_error = session.get('bet_error', None)
        bet_success = session.get('bet_success', None)
        new_bet = session.get('new_bet', None)

        # Variables to populate the form if a previous  bet exists
        date = None
        time = None
        gender = None
        hair = None
        length = None
        pounds = None
        ounces = None

        template = JINJA_ENVIRONMENT.get_template('make_bet.html')
        title = "Ianni Baby 2.0 - Make Your Bet"
        if email and user:
            logged_in = True
            # Check to see if the user has already made a bet
            user_query = User.query(User.email==email)
            cur_user = user_query.get()
            if cur_user.date:
                has_prev_bet = True
                date = cur_user.date
                time = cur_user.time
                gender = cur_user.gender
                hair = cur_user.hair_color
                pounds = cur_user.pounds
                ounces = cur_user.ounces
            else:
                has_prev_bet = False
        else:
            logged_in = False
            has_prev_bet = False

        template_values = {
            'user':user,
            'title':title,
            'logged_in':logged_in,
            'has_prev_bet':has_prev_bet,
            'bet_error':bet_error,
            'bet_success':bet_success,
            'date':cur_user.date,
            'time':cur_user.time,
            'gender':cur_user.gender,
            'hair':cur_user.hair_color,
            'pounds':cur_user.pounds,
            'ounces':cur_user.ounces,
        }

        # Clean-up
        if bet_error:
            del session['bet_error']
        if bet_success:
            del session['bet_success']
        
        self.response.write(template.render(template_values))

    def post(self):
        session = get_current_session()
        date = self.request.get('date')
        time = self.request.get('time')
        gender = self.request.get('gender')
        hair_color = self.request.get('hair')
        length = self.request.get('length')
        pounds = self.request.get('pounds')
        ounces = self.request.get('ounces')
        email = session.get('user_email', None)

        valid = True
        
        if not email:
            self.redirect('/')
        else:

            # Get current user's db entry
            user_query = User.query(User.email == email)
            if user_query.count() != 1:
                session['bet_error'] = "Error with retrieving User's profile"
                valid = False
            else:
                cur_user = user_query.get()
                cur_user.date = date
                cur_user.time = time
                cur_user.gender = gender
                cur_user.hair_color = hair_color
                cur_user.length = int(length)
                cur_user.pounds = int(pounds)
                cur_user.ounces = int(ounces)
                cur_user.put()
                session['bet_success'] = True
                session['new_bet'] = cur_user
                
            self.redirect('/bet')
            

class ResultHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Results")

class FAQHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("FAQ")

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        # Session Handling
        session = get_current_session()
        if session.has_key('user'):
            del session['user']
        login_error = session.get('login_error', None)
        email_error = session.get('email_error', None)
        password_error = session.get('pwd_error', None)
        email = session.get('email', None)
        
        template = JINJA_ENVIRONMENT.get_template('login.html')
        title = "Ianni Baby 2.0 - Login"
        logged_in = False
        template_values = {
            'title':title,
            'logged_in':logged_in,
            'login_error':login_error,
            'pwd_error':password_error,
            'email':email
        }
        if session.has_key('login_error'):
            del session['login_error']
        if session.has_key('email_error'):
            del session['email_error']
        if session.has_key('pwd_error'):
            del session['pwd_error']
        if session.has_key('email'):
             del session['email']
        self.response.write(template.render(template_values))

    def post(self):
        session = get_current_session()
        email = self.request.get('email')
        if email:
            session['email'] = email
        if len(self.request.get('password')) == 0:
            password = None
        else:
            password = hashlib.md5(self.request.get('password')).hexdigest()
        if not email:
            session['email_error'] = "Please provide an email"
        if not password:
            session['pwd_error'] = "Please provide a password"
        if not email or not password:
            session['login_error'] = "Login Error"
            self.redirect('/login')
        else:
            user_query = User.query(User.email == email, User.password == password)
            if user_query.count() > 0:
                user = user_query.get()
                session['user'] = user.name
                session['user_email'] = session['email']
                del session['email']
                self.redirect('/')
            else:
                session['login_error'] = "Email and Password do not match"
                self.redirect('/login')

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.has_key('user'):
            del session['user']
        if session.has_key('user_email'):
            del session['user_email']
        self.redirect('/')

class AccountHandler(webapp2.RequestHandler):
    def get(self):
        # Session Handling
        session = get_current_session()
        user = session.get('user', None)

        pwd_error = session.get('pwd_error', None)
        email_error = session.get('email_error', None)
        name_error = session.get('name_error', None)
        name = session.get('name', None)
        email = session.get('email', None)
        create_error = session.get('create_error', None)
        
        template = JINJA_ENVIRONMENT.get_template('account.html')
        title = "Ianni Baby 2.0 - Create Account"
        if user:
            logged_in = True
        else:
            logged_in = False
        template_values = {
            'pwd_error':pwd_error,
            'email_error':email_error,
            'name_error':name_error,
            'name':name,
            'email':email,
            'title':title,
            'logged_in':logged_in,
            'create_error':create_error
        }
        self.response.write(template.render(template_values))
        if session.has_key('name'):
            del session['name']
        if session.has_key('email'):
            del session['email']
        if session.has_key('name_error'):
            del session['name_error']
        if session.has_key('email_error'):
            del session['email_error']
        if session.has_key('pwd_error'):
            del session['pwd_error']
        if session.has_key('create_error'):
            del session['create_error']

    def post(self):
        session = get_current_session()
        
        name = self.request.get('name')
        email= self.request.get('email')
        password1= self.request.get('password1')
        password2 = self.request.get('password2')
        session['name'] = name
        session['email'] = email
        valid = True
        
        if not name:
            session['name_error'] = "Name is a required field"
            valid = False
        if not email:
            session['email_error'] = "Email is a required field"
            valid = False
        if password1 != password2:
            session['pwd_error'] = "Passwords don't match"
            valid = False
        if not password1 or not password2:
            session['pwd_error'] = "Passwords are required fields"
            valid = False
        if valid:
            # Check to ensure email isn't already taken
            user_query = User.query(User.email == email)
            if user_query.count() > 0:
                valid = False
                session['email_error'] = "Email is already taken"
        if not valid:
            session['create_error'] = "Account Creation Error"
            self.redirect('/account')
        else:
            # Everything seems to be in order so lets create an account
            password = hashlib.md5(password1).hexdigest()
            new_user = User(name=name,
                            email=email,
                            password=password)
            new_user.put()
            if session.has_key('name_error'):
                del session['name_error']
            if session.has_key('email_error'):
                del session['email_error']
            if session.has_key('pwd_error'):
                del session['pwd_error']
            if session.has_key('user'):
                del session['user']
            if session.has_key('name'):
                del session['name']
            if session.has_key('email'):
                del session['email']
            self.redirect('/login')

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/bet', BetHandler),
    ('/results', ResultHandler),
    ('/faq', FAQHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/account', AccountHandler),
], debug = True)
