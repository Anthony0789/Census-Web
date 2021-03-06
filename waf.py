from bottle import run, request, post, get
import re
import string

# Important globals
host = "localhost"
port = "8082"

# Debug mode to check whether or not attacks are working
# Start with it as "True", try the attack, flip it to false, try the attack again and see if your WAF blocked it
# Debug should be set to false when launching the final version
debug = False

@post('/waf/detect/<string_in:path>')
def detect_attack(string_in):
    if not debug:
        if "<" in string_in:
            print("Sensitive characters '<' detacted") #XSS Attack
            return "Sensitive characters '<' detacted" #XSS Attack
        if ">" in string_in:
            print("Sensitive characters '>' detacted") #XSS Attack
            return "Sensitive characters '>' detacted" #XSS Attack
        if '\"' in string_in:
            print("Sensitive characters '\"' detacted")
            return "Sensitive characters '\"' detacted"
        if '\'' in string_in:
            print("Sensitive characters '\'' detacted")
            return "Sensitive characters '\'' detacted"
        return 'True'
    return 'False'

@post('/waf/email/<email:path>')
def verify_email(email):
    if re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) != None:
        return 'True'
    else:
        return "Not an email address"

@post('/waf/password/<password:path>')
def verify_password(password):
    pattern_upper = re.compile('[A-Z]+')
    pattern_lower = re.compile('[a-z]+')
    pattern_num =  re.compile('[0-9]+')
    if len(password) < 8:
        return "Password is too short"

    if not pattern_lower.findall(password):
        return "Password must contain at least one lowercase character"

    if not pattern_upper.findall(password):
        return "Password must contain at least one uppercase character"

    if not pattern_num.findall(password):
        return "Password must contain at least one number"

    return 'True'

# Rather than using paths, you could throw all the requests with form data filled using the
# requests module and extract it here. Alternatively you could use JSON objects.

# Custom definition waf
@post('/waf/custom/field=<field:path>%20test=<test:path>')
def custom_waf(field, test):
    if re.search(test, field) is not None:
        return "True"
    return "False"

# Debug toggle
@post('/waf/debug')
def enable_debugger():
    global debug
    if debug:
        debug = False
    else:
        debug = True

# Run the server
run(host=host, port=port)
