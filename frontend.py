from bottle import route, get, run, post, request, redirect, static_file, template, TEMPLATE_PATH
from Crypto.Hash import MD5
import re
import os, sys
import time
import numpy as np
import hashlib
import requests
import json

#---------------------configurations-------------------
host_addr = "localhost"
frontend_port = 8080
backend_port = 8081
waf_port = 8082

backend_str = "http://{host}:{port}".format(host=host_addr, port=backend_port)
# ----------------------------------------------------------------------

class WAFCaller(object):
    def __init__(self, waf_address, waf_port):
        self.waf_port = waf_port
        self.waf_address = waf_address
        self.waf_string = "http://{address}:{port}".format(address=waf_address, port=waf_port)

    # ----------------------------------------------------------------------

    # Ideally every string sent to the server should first pass through the WAF
    def check_attack(self, attack_vector):
        # Check for malicious code
        response = requests.post("{target}/waf/detect/{attack_vector}"
            .format(target=self.waf_string, attack_vector=attack_vector))

        # Rather than redirecting, you can attempt to sanitise the string
        if response.text != "True":
            redirect('/invalid/{response}'.format(response=response.text))

    # ----------------------------------------------------------------------

    def check_email(self, email):
        # Check for attack strings
        self.check_attack(email)
        # Call the waf
        response = requests.post("{target}/waf/email/{email}"
            .format(target=self.waf_string, email=email))
        return response.text

    def check_password(self, password):
        # Check for attack strings
        self.check_attack(password)
        # Check parsing format
        response = requests.post("{target}/waf/password/{password}"
            .format(target=self.waf_string, password=password))
        return response.text

waf = WAFCaller('localhost', '8082')
#-----------------------------------------------------------------

# Potential attack string detected
@get('/invalid/<response:path>')
def defuse(response):
    return template("invalid", reason=response)

#-----------------------------------------------------------------
#Example
# def useradd():
    # username = request.forms.get("username")
    # password = request.forms.get("password")

    # Call the WAF
    # username_check = waf.check_email(username)		get String 'True', if no problem
    # password_check = waf.check_password(password)
#-----------------------------------------------------------------------------
# This class loads html files from the "template" directory and formats them using Python.
# If you are unsure how this is working, just

# Allow image loading
@route('/img/<picture>')
def serve_pictures(picture):
    return static_file(picture, root='img/')

# Allow CSS
@route('/css/<css>')
def serve_css(css):
    return static_file(css, root='css/')

# Allow javascript
@route('/js/<js>')
def serve_js(js):
    return static_file(js, root='js/')

#-----------------------------------------------------------------------------
# Redirect to login
@route('/')
@route('/login')
def login():
    return template("login")

@get('/logout')
def logout():
    global user_id
    global user_type
    global user_name
    global user_email
    user_id = 0
    user_type = -1
    user_name = ''
    user_email = ''
    return login()
# Display the index page
@get('/indexU')
def indexU():
    return main_page()
@get('/indexR')
def indexR():
    return main_page()
@get('/indexS')
def indexS():
    return main_page()
@get('/indexA')
def indexA():
    return main_page()

def main_page():
    global user_id
    global user_type
    global user_name
    global user_email

    if user_type == 0:
        return template("indexU", user_name=user_name, user_email=user_email)
    if user_type == 1:
        return template("indexR", user_name=user_name, user_email=user_email)
    if user_type == 2:
        return template("indexS", user_name=user_name, user_email=user_email)
    if user_type == 3:
        return template("indexA", user_name=user_name, user_email=user_email)
    return login()

@get('/complete')
def complete():
    global user_type
    global user_id
    global user_name

    if is_login() and user_type == 2:
        response = requests.post("{target}/api/survey_view_completion"
            .format(target=backend_str))
        result = json.loads(response.text)
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"view users' completion"})
        return template("complete",data_list=result['result'])
    else:
        return main_page()

@get('/survey')
def survey():
    global user_type
    global user_id
    if is_login() and user_type == 0:
        response = requests.post("{target}/api/survey_read"
            .format(target=backend_str), data={'user_id':user_id})
        result = json.loads(response.text)
        if result['result'] == False:
            return template("survey")
        else:
            return template("invalid", reason="You have sumbitted the survey before")
    else:
        return main_page()

@get('/edit')
def edit_page():
    if is_login():
        return template("edit")
    else:
        return login()

@get('/data_collection')
def do_data_collection():
    global user_id
    global user_name
    global user_type
    if is_login() and user_type == 1:
        response = requests.post("{target}/api/survey_statics"
            .format(target=backend_str))
        result = json.loads(response.text)
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"view data statics"})
        return template("collection", data_list=result['result'])
    else:
        return login()

@get('/view_log')
def do_view_log():
    global user_type
    if is_login() and user_type == 3:
        response = requests.post("{target}/api/view_log"
            .format(target=backend_str))
        result = json.loads(response.text)
        return template("log", data_list=result['result'])
    else:
        return main_page()

@get('/request_list')
def view_request_list():
    global user_type
    if is_login() and user_type == 2:
        response = requests.post("{target}/api/application_read"
            .format(target=backend_str))
        result = json.loads(response.text)
        return template("request", data_list=result['result'])
    else:
        return main_page()

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    err_str = ''
    login = False

	# Call the WAF
    username_check = waf.check_email(username)
    password_check = waf.check_password(password)

    if username_check == 'True' and password_check == 'True':
        err_str, login = check_login(username, encry(password))
    else:
        if username_check == 'True':
            return template("invalid", reason=password_check)
        else:
            return template("invalid", reason=username_check)

    if login:
        return main_page()
    else:
        return template("invalid", reason=err_str)

@post('/registerU')
def do_registerU():
    username = request.forms.get('useremail')
    password = request.forms.get('newpassword')
    email = request.forms.get('email')
    confirm = request.forms.get('confirm')
    if confirm != password:
        return template("invalid", reason="two input password must be consistent")
	# Call the WAF
    username_check = waf.check_attack(username) # return to invalid page directly if not equal to 'True'
    password_check = waf.check_password(password)
    email_check = waf.check_email(email)
    if email_check == 'True' and password_check == 'True':
        #write the data to file
        check_response = requests.post("{target}/api/check_register"
            .format(target=backend_str), data={'email':email})
        check_result = json.loads(check_response.text)
        if check_result['result']:
            register_response = requests.post("{target}/api/register_write"
                .format(target=backend_str), data={'user_name':username, 'email':email, 'password':encry(password), 'user_type':0})
            register_result = json.loads(register_response.text)
            requests.post("{target}/api/log"
                .format(target=backend_str), data={'user_id':register_result['user_id'], 'user_name':register_result['user_name'], 'action':"registered as user"})
            return template("login")
        else:
            return template("invalid", reason=check_result['message'])
    else:
        if email_check == 'True':
            return template("invalid", reason=password_check)
        else:
            return template("invalid", reason=email_check)

@post('/registerR')
def do_registerR():
    username = request.forms.get('useremail')
    password = request.forms.get('newpassword')
    email = request.forms.get('email')
    confirm = request.forms.get('confirm')
    if confirm != password:
        return template("invalid", reason="two input password must be consistent")
	# Call the WAF
    username_check = waf.check_attack(username) # return to invalid page directly if not equal to 'True'
    password_check = waf.check_password(password)
    email_check = waf.check_email(email)
    if email_check == 'True' and password_check == 'True':
        #write the data to file
        check_response = requests.post("{target}/api/check_register"
            .format(target=backend_str), data={'email':email})
        check_result = json.loads(check_response.text)
        if check_result['result']:
            register_response = requests.post("{target}/api/register_write"
                .format(target=backend_str), data={'user_name':username, 'email':email, 'password':encry(password), 'user_type':1})
            register_result = json.loads(register_response.text)
            requests.post("{target}/api/log"
                .format(target=backend_str), data={'user_id':register_result['user_id'], 'user_name':register_result['user_name'], 'action':"registered as researcher"})
            return template("login")
        else:
            return template("invalid", reason=check_result['message'])
    else:
        if email_check == 'True':
            return template("invalid", reason=password_check)
        else:
            return template("invalid", reason=email_check)

@post('/registerS')
def do_registerS():
    username = request.forms.get('useremail')
    password = request.forms.get('newpassword')
    email = request.forms.get('email')
    confirm = request.forms.get('confirm')
    if confirm != password:
        return template("invalid", reason="two input password must be consistent")
	# Call the WAF
    username_check = waf.check_attack(username) # return to invalid page directly if not equal to 'True'
    password_check = waf.check_password(password)
    email_check = waf.check_email(email)
    if email_check == 'True' and password_check == 'True':
        #write the data to file
        check_response = requests.post("{target}/api/check_register"
            .format(target=backend_str), data={'email':email})
        check_result = json.loads(check_response.text)
        if check_result['result']:
            register_response = requests.post("{target}/api/register_write"
                .format(target=backend_str), data={'user_name':username, 'email':email, 'password':encry(password), 'user_type':2})
            register_result = json.loads(register_response.text)
            requests.post("{target}/api/log"
                .format(target=backend_str), data={'user_id':register_result['user_id'], 'user_name':register_result['user_name'], 'action':"registered as staff"})
            return template("login")
        else:
            return template("invalid", reason=check_result['message'])
    else:
        if email_check == 'True':
            return template("invalid", reason=password_check)
        else:
            return template("invalid", reason=email_check)

@post('/clear')
def do_clear():
    password = request.forms.get('adminpassword')
    waf.check_attack(password)
    if password == "12345":
        requests.post("{target}/api/clear_all_data"
            .format(target=backend_str))
    else:
        err_str = "password incorret"
        return template("invalid", reason=err_str)

@post('/completion')
def do_completion():
    global user_id
    global user_name

    # Call the WAF after get()
    age = request.forms.get('age')
    waf.check_attack(age)

    gender = request.forms.get('gender')
    waf.check_attack(gender)

    lived = request.forms.get('lived')
    waf.check_attack(lived)

    residence = request.forms.get('residence')
    waf.check_attack(residence)

    date = request.forms.get('date')
    waf.check_attack(date)

    origin = request.forms.get('origin')
    waf.check_attack(origin)

    survey = [age, gender, lived, residence, date, origin]
    #comple_num is the numbers of qustions completed
    comple_num = 0
    for i in survey:
        if i != None:
            comple_num += 1
    #is_completed is the statis 0:false 1:truse
    is_completed = '1'
    survey.append(str(comple_num))
    survey.append(is_completed)
    #write data into file
    requests.post("{target}/api/survey_write"
        .format(target=backend_str), data={'user_id':user_id, 'survey':json.dumps(survey)})
    requests.post("{target}/api/log"
        .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"submit a survey"})
    return main_page()

@post('/view_result')
def do_view_result():
    global user_id
    global user_name

    response = requests.post("{target}/api/survey_read"
        .format(target=backend_str), data={'user_id':user_id})
    result = json.loads(response.text)
    if result['result'] != False:
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"view survey result"})
        return template("result", survey=result['survey'])
    else:
        return template("invalid", reason="No data")

@post('/save')
def do_save():
    global user_id
    new_name = request.forms.get('new_name')
    waf.check_attack(new_name)
    old_password = request.forms.get('old_password')
    old_password_check = waf.check_password(old_password)
    if old_password_check != 'True':
        return template("invalid", reason=old_password_check)
    old = encry(old_password)
    new_password = request.forms.get('new_password')
    new_password_check = waf.check_password(old_password)
    if new_password_check != 'True':
        return template("invalid", reason=new_password_check)
    new = encry(new_password)
    response = requests.post("{target}/api/details_change"
        .format(target=backend_str), data={'user_id':user_id, 'new_name':new_name, 'old_password':old, 'new_password':new})
    result = json.loads(response.text)
    if result['result']:
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':new_name, 'action':"changes personal details successfully"})
        return template("login")
    else:
        return template("invalid", reason="incorret old password")

@post('/redo_apply')
def redo_survey_apply():
    global user_id
    global user_name
    search_response = requests.post("{target}/api/application_search"
        .format(target=backend_str), data={'user_id':user_id})
    search_result = json.loads(search_response.text)
    if search_result['result'] == False:
        requests.post("{target}/api/application_write"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name})
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"apply to redo the survey"})
        return template("invalid", reason="Your application have submitted")
    else:
        return template("invalid", reason="Your submitted your application before, please wait for process")

@post('/request_approve')
def request_approve():
    global user_id
    global user_name
    user_id_request = request.forms.get('user_id')
    waf.check_attack(user_id_request)
    requests.post("{target}/api/application_approve"
        .format(target=backend_str), data={'user_id_request':user_id_request})
    requests.post("{target}/api/log"
        .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"approve user_id:"+user_id_request+" application"})
    return main_page()

def check_login(email, password):
    global user_type
    global user_id
    global user_name
    global user_email
    login_string = ""
    response = requests.post("{target}/api/check_login"
        .format(target=backend_str), data={'email':email, 'password':password})
    result = json.loads(response.text)
    if result['result'] == True:
        user_id = int(result['user_id'])
        user_type = int(result['user_type'])
        user_name = result['user_name']
        user_email = result['email']
        login_string = "Logged in!"
        requests.post("{target}/api/log"
            .format(target=backend_str), data={'user_id':user_id, 'user_name':user_name, 'action':"login"})
        return login_string, True
    else:
        login_string = "This combination is invalid."
        return login_string, False

def is_login():
    global user_id
    if user_id == 0:
        return False
    else:
        return True

def encry(text):
    salt = "!@#$%"
    to_hash = text+salt
    encoded_string = to_hash.encode()
    hash_hex = hashlib.sha256(encoded_string).hexdigest()
    return hash_hex

#------------------------global variables--------------------------------------------
#0:general user 1:researcher 2:stuff 3:administrator
user_type = -1
#user_id start from 1
user_id = 0
#username
user_name = ''
#user_email
user_email = ''

TEMPLATE_PATH.insert(0, 'templates')
run(host='localhost', port=8080, debug=True)
