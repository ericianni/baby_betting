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

DUE_DATE = "2017-11-19"
CUT_OFF_DATE = "2017-11-01"
BASE_URL = "https://Ianni-baby-2.appspot.com"

class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    date = ndb.StringProperty()
    time = ndb.StringProperty()
    gender = ndb.StringProperty()
    hair_color = ndb.StringProperty()
    length = ndb.FloatProperty()
    pounds = ndb.IntegerProperty()
    ounces = ndb.IntegerProperty()
    
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
        date_error = session.get('date_error', None)
        time_error = session.get('time_error', None)
        gender_error = session.get('gender_error', None)
        hair_error = session.get('hair_error', None)
        length_error = session.get('length_error', None)
        pound_error = session.get('pound_error', None)
        ounce_error = session.get('ounce_error', None)

        date = session.get('date', None)
        time = session.get('time', None)
        gender = session.get('gender', None)
        hair = session.get('hair', None)
        length = session.get('length', None)
        pounds = session.get('pounds', None)
        ounces = session.get('ounces', None)

        template = JINJA_ENVIRONMENT.get_template('make_bet.html')
        title = "Ianni Baby 2.0 - Make Your Bet"
        if email and user:
            logged_in = True
            # Check to see if the user has already made a bet
            user_query = User.query(User.email==email)
            cur_user = user_query.get()
            if cur_user.date and not new_bet:
                has_prev_bet = True
                date = cur_user.date
                time = cur_user.time
                gender = cur_user.gender
                hair = cur_user.hair_color
                length = cur_user.length
                pounds = cur_user.pounds
                ounces = cur_user.ounces
            else:
                has_prev_bet = False
        else:
            logged_in = False
            has_prev_bet = False

        template_values = {
            'due_date':DUE_DATE,
            'user':user,
            'title':title,
            'logged_in':logged_in,
            'has_prev_bet':has_prev_bet,
            'bet_error':bet_error,
            'bet_success':bet_success,
            'date':date,
            'time':time,
            'gender':gender,
            'hair':hair,
            'length':length,
            'pounds':pounds,
            'ounces':ounces,
            'date_error':date_error,
            'time_error':time_error,
            'gender_error':gender_error,
            'hair_error':hair_error,
            'length_error':length_error,
            'pound_error':pound_error,
            'ounce_error':ounce_error,
        }

        # Clean-up
        if bet_error:
            del session['bet_error']
        if bet_success:
            del session['bet_success']
        if new_bet:
            del session['new_bet']
        if date_error:
            del session['date_error']
        if time_error:
            del session['time_error']
        if gender_error:
            del session['gender_error']
        if hair_error:
            del session['hair_error']
        if length_error:
            del session['length_error']
        if pound_error:
            del session['pound_error']
        if ounce_error:
            del session['ounce_error']
        if session.has_key('date'):
            del session['date']
        if session.has_key('time'):
            del session['time']
        if session.has_key('gender'):
            del session['gender']
        if session.has_key('hair'):
            del session['hair']
        if session.has_key('length'):
            del session['length']
        if session.has_key('pounds'):
            del session['pounds']
        if session.has_key('ounces'):
            del session['ounces']
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
            if not date:
                session['date_error'] = "You must enter a date"
                valid = False
            else:
                session['date'] = date
            if not time:
                session['time_error'] = "You must enter a time"
                valid = False
            else:
                session['time'] = time
            if not gender:
                session['gender_error'] = "You must enter a gender"
                valid = False
            else:
                session['gender'] = gender
            if not hair_color:
                session['hair_error'] = "You must enter a hair color"
                valid = False
            else:
                session['hair'] = hair_color
            if not length:
                session['length_error'] = "You must enter a length"
                valid = False
            else:
                session['length'] = length
            if not pounds:
                session['pound_error'] = "You must enter pounds"
                valid = False
            else:
                session['pounds'] = pounds
            if not ounces:
                session['ounce_error'] = "You must enter ounces"
                valid = False
            else:
                session['ounces'] = ounces
                

            # Get current user's db entry
            user_query = User.query(User.email == email)
            if user_query.count() != 1:
                session['bet_error'] = "Error with retrieving User's profile"
                valid = False
            if not valid:
                self.redirect('/bet')
            else:
                cur_user = user_query.get()
                cur_user.date = date
                cur_user.time = time
                cur_user.gender = gender
                cur_user.hair_color = hair_color
                cur_user.length = float(length)
                cur_user.pounds = int(pounds)
                cur_user.ounces = int(ounces)
                cur_user.put()
                session['bet_success'] = True
                session['new_bet'] = cur_user
                
                self.redirect('/bet')
            

class ResultHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Results")

    def calc_score(self, user_date, actual_data):
        date_multiplier = 65
        gender_multiplier = 20
        hair_multiplier = 5
        length_multiplier = 5
        weight_multiplier = 5
        # Break score down by section
        results = {}
        # Date + Time = 65
        days_off = get_day_diff(user_data.date, user_data.time, actual_data.date, actual_data.time)
        if days_off > 14:
            results['date'] = 0.0
        else:
            results['date'] = (1.0 - days_off / 14.0) * date_multiplier 
        # Gender = 25
        if user_data.gender == actual_data.gender:
            results['gender'] = gender_multiplier
        else:
            results['gender'] = 0.0
        # Hair = 5
        if user_data.hair_color == actual_data.hair_color:
            results['hair'] = hair_multiplier
        else:
            results['hair'] = 0.0
        # Length = 5
        length_off = abs(user_data.length - actual_data.length)
        if length_off > 3.0:
            results['length'] = 0.0
        else:
            resutls['length'] = (1.0 - length_off / 3.0) * length_multipler
        # Weight = 5
        weight_off = get_weight_diff(user_data.pounds, user_data.ounces, actual_data.pounds, actual_data.ounces)
        if weight_off > 48.0:
            results['weight'] = 0.0
        else:
            resutls['weight'] = (1.0 - weight_off / 3.0) * weight_multipler
        return results

    def get_day_diff(self, date0, time0, date1, time1):
        day0 = datetime.datetime.strptime(date0, '%Y-%m-%d')
        day1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
        h0, m0 = time0.split(':')
        partial_day0 = (int(h0) * 60 + int(m0)) / 1440.0
        h1, m1 = time0.split(':')
        partial_day1 = (int(h1) * 60 + int(m1)) / 1440.0
        return abs(day0 - day1).days + abs(partial_day0 - partial_day1)

    def get_weight_diff(self, pounds0, ounces0, pounds1, ounces1):
        weight0 = pounds0 * 16 + ounces
        weight1 = pounds1 * 16 + ounces
        return abs(weight0 - weight1)

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
        self.response.write(template.render(template_values))


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
