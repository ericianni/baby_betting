from google.appengine.ext import ndb
from gaesessions import get_current_session
#from google.appengine.api import mail
from google.appengine.api import app_identity
from google.appengine.ext import vendor
vendor.add('lib')
import os
import webapp2
import jinja2
import urllib
import json
import datetime
import hashlib
import logging
import sendgrid
from sendgrid.helpers import mail

# Globals

SENDGRID_API_KEY = ''
SENDGRID_SENDER = "Ianni Baby 2.0"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DUE_DATE = "2017-11-19"
CUT_OFF_DATE = "2017-11-09"
BASE_URL = "https://Ianni-baby-2.appspot.com"
ADMIN_EMAIL = "admin@admin.com"

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
        message = session.get('message', None)
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        title = "Ianni Baby 2.0"
        if user:
            logged_in = True
        else:
            logged_in = False
        template_values = {
            'user':user,
            'title':title,
            'logged_in':logged_in,
            'message':message,
            'cut_off_date':CUT_OFF_DATE,
        }
        if session.has_key('message'):
            del session['message']
        self.response.write(template.render(template_values))

class BetHandler(webapp2.RequestHandler):
    def get(self):
        today = datetime.datetime.now()
        
        # Session Handling
        session = get_current_session()

        user = session.get('user', None)
        email = session.get('user_email', None)

        admin_query = User.query(User.email==ADMIN_EMAIL)

        if admin_query.count() == 1:
            if admin_query.get().date != None and email != ADMIN_EMAIL:
                session['message'] = "Sorry, the books are closed"
                self.redirect('/')
        if today > datetime.datetime.strptime(CUT_OFF_DATE, '%Y-%m-%d') and email != ADMIN_EMAIL:
            session['message'] = "Sorry, the books are closed"
            self.redirect('/')
            

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


        formatted_due_date = datetime.datetime.strptime(DUE_DATE, '%Y-%m-%d').strftime('%m/%d/%Y')
        formatted_cut_off_date = datetime.datetime.strptime(CUT_OFF_DATE, '%Y-%m-%d').strftime('%m/%d/%Y')
        template_values = {
            'due_date':DUE_DATE,
            'cut_off_date':formatted_cut_off_date,
            'formatted_due_date':formatted_due_date,
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

                if cur_user.email == ADMIN_EMAIL:
                    self.send_results()
                else:
                    self.send_email(cur_user)

                session['bet_success'] = True
                session['new_bet'] = cur_user
                
                self.redirect('/bet')
    def send_email(self, user):

        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = mail.Email("ebianni@gmail.com")
        to_email = mail.Email("ebianni@gmail.com")
        # sender = "ebianni@gmail.com"
        subject = user.name + " has made a bet"
        body = """There is a new bet by {}!



Date/Time: {} {}
Gender: {}
Hair Color: {}
Length: {}"
Weight: {} lbs {} oz""".format(user.name, user.date, user.time, user.gender, user.hair_color, user.length, user.pounds, user.ounces)

        content = mail.Content('text/plain', body)
        message = mail.Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=message.get())
        


    def send_results(self):
        user_query = User.query()
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = mail.Email("ebianni@gmail.com")
        subject = "The baby has landed"
        body = """Ianni Baby 2.0 has Arrived!

Let's see how you did in the betting pool """
        admin = User.query(User.email==ADMIN_EMAIL).get()
        if user_query.count() > 0 and admin:
            results = []
            for user in user_query:
                if user.date and user.email != ADMIN_EMAIL:
                    result = self.calc_score(user, admin)
                    results.append(result)
            results = sorted(results, key=lambda k: k['total'], reverse=True) 
            for result in results:
                body += """

User: {} Score: {}

""".format(result['user'].name, result['total'])

            body += """

        See full results at http://ianni-baby-2.appspot.com/results."""

            for user in user_query:
                to_email = mail.Email(user.email)
                content = mail.Content('text/plain', body)
                message = mail.Mail(from_email, subject, to_email, content)
                if user.email != ADMIN_EMAIL:
                    response = sg.client.mail.send.post(request_body=message.get())
                
    def calc_score(self, user_data, actual_data):

        date_multiplier = 65.0
        gender_multiplier = 20.0
        hair_multiplier = 5.0
        length_multiplier = 5.0
        weight_multiplier = 5.0
        total = 0
        # Break score down by section
        results = {}
        results['user'] = user_data
        # Date + Time = 65
        days_off = self.get_day_diff(user_data.date, user_data.time, actual_data.date, actual_data.time)
        if days_off > 14:
            results['date'] = 0.0
        else:
            results['date'] = round((1.0 - days_off / 14.0) * date_multiplier, 1)
            total += results['date']
        # Gender = 25
        if user_data.gender == actual_data.gender:
            results['gender'] = gender_multiplier
            total += results['gender']
        else:
            results['gender'] = 0.0
        # Hair = 5
        if user_data.hair_color == actual_data.hair_color:
            results['hair'] = hair_multiplier
            total += results['hair']
        else:
            results['hair'] = 0.0
        # Length = 5
        length_off = abs(user_data.length - actual_data.length)
        if length_off > 3.0:
            results['length'] = 0.0
        else:
            results['length'] = round((1.0 - length_off / 3.0) * length_multiplier, 1)
            total += results['length']
        # Weight = 5
        weight_off = self.get_weight_diff(user_data.pounds, user_data.ounces, actual_data.pounds, actual_data.ounces)
        if weight_off > 48.0:
            results['weight'] = 0.0
        else:
            results['weight'] = round((1.0 - weight_off / 48.0) * weight_multiplier, 1)
            total += results['weight']
        results['total'] = round(total, 1)
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
        weight0 = pounds0 * 16 + ounces0
        weight1 = pounds1 * 16 + ounces1
        return abs(weight0 - weight1)
    
class ResultHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        
        admin_query = User.query(User.email==ADMIN_EMAIL)
        if admin_query.count() == 1:
            admin_data = admin_query.get()
            if not admin_data.date:
                all_users = []
                user_query = User.query()
                if user_query.count > 0:

                    for user_data in user_query:
                        all_users.append(user_data.to_dict())
                    all_users = sorted(all_users, key=lambda k: k['date'])

                template = JINJA_ENVIRONMENT.get_template('results.html')
                title = "Ianni Baby 2.0 - Results"
                user = session.get('user', None)
                message = session.get('message', None)
                    
                if user:
                    logged_in = True
                else:
                    logged_in = False
                template_values = {
                    'user':user,
                    'title':title,
                    'logged_in':logged_in,
                    'message':message,
                    'all_users':all_users,
                }
                if session.has_key('message'):
                    del session['message']
                self.response.write(template.render(template_values))
                
                # session['message'] = "The baby hasn't been born yet!"
                # self.redirect('/')
            else:
                template = JINJA_ENVIRONMENT.get_template('results.html')
                title = "Ianni Baby 2.0 - Results"
                user = session.get('user', None)
                message = session.get('message', None)

                results = []
                all_query = User.query()
                if all_query.count() > 0:
                    for user_data in all_query:
                        results.append(self.calc_score(user_data, admin_data))
                    results = sorted(results, key=lambda k: k['total'], reverse=True) 
                
                if user:
                    logged_in = True
                else:
                    logged_in = False
                template_values = {
                    'user':user,
                    'title':title,
                    'logged_in':logged_in,
                    'message':message,
                    'results':results,
                }
                if session.has_key('message'):
                    del session['message']
                self.response.write(template.render(template_values))

        else:
            self.response.write("There is an issue with the Admin account")

    def calc_score(self, user_data, actual_data):

        date_multiplier = 65.0
        gender_multiplier = 20.0
        hair_multiplier = 5.0
        length_multiplier = 5.0
        weight_multiplier = 5.0
        total = 0
        # Break score down by section
        results = {}
        results['user'] = user_data
        # Date + Time = 65
        days_off = self.get_day_diff(user_data.date, user_data.time, actual_data.date, actual_data.time)
        if days_off > 14:
            results['date'] = 0.0
        else:
            results['date'] = round((1.0 - days_off / 14.0) * date_multiplier, 1)
            total += results['date']
        # Gender = 25
        if user_data.gender == actual_data.gender:
            results['gender'] = gender_multiplier
            total += results['gender']
        else:
            results['gender'] = 0.0
        # Hair = 5
        if user_data.hair_color == actual_data.hair_color:
            results['hair'] = hair_multiplier
            total += results['hair']
        else:
            results['hair'] = 0.0
        # Length = 5
        length_off = abs(user_data.length - actual_data.length)
        if length_off > 3.0:
            results['length'] = 0.0
        else:
            results['length'] = round((1.0 - length_off / 3.0) * length_multiplier, 1)
            total += results['length']
        # Weight = 5
        weight_off = self.get_weight_diff(user_data.pounds, user_data.ounces, actual_data.pounds, actual_data.ounces)
        if weight_off > 48.0:
            results['weight'] = 0.0
        else:
            results['weight'] = round((1.0 - weight_off / 48.0) * weight_multiplier, 1)
            total += results['weight']
        results['total'] = round(total, 1)
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
        weight0 = pounds0 * 16 + ounces0
        weight1 = pounds1 * 16 + ounces1
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

            self.send_email(new_user)
            
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

    def send_email(self, new_user):
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = mail.Email("ebianni@gmail.com")
        subject = "New Baby Bet User"
        to_email = mail.Email("ebianni@gmail.com")
        body = """There is a new user for Ianni Baby 2.0 Betting Service!

Name: {}
Email: {}""".format(new_user.name, new_user.email)

        content = mail.Content('text/plain', body)
        message = mail.Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=message.get())

class FAQHandler(webapp2.RequestHandler):
    def get(self):
        # Session Handling
        session = get_current_session()
        user = session.get('user', None)
        message = session.get('message', None)
        
        template = JINJA_ENVIRONMENT.get_template('faq.html')
        title = "Ianni Baby 2.0 - How It Works"
        if user:
            logged_in = True
        else:
            logged_in = False
        template_values = {
            'user':user,
            'title':title,
            'logged_in':logged_in,
            'message':message,
            'cut_off_date':CUT_OFF_DATE,
        }
        if session.has_key('message'):
            del session['message']
        self.response.write(template.render(template_values))

            
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
