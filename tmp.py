from flask import Flask, request, redirect, make_response                                                                              from cryptography.fernet import Fernet                                                                                                 import subprocess                                                                                                                      import base64                                                                                                                          import time                                                                                                                                                                                                                                                                   key = b'es_sTkQ2pPjGficMIYQ8PL9LWZTpR3WIwr6cTYDVzro='                                                                                  fernet = Fernet(key)                                                                                                                                                                                                                                                          app = Flask(__name__)                                                                                                                                                                                                                                                         SLEEP_TIME = 0.1                                                                                                                       TIMEOUT = 5                                                                                                                                                                                                                                                                   def timeout(proc):                                                                                                                         count = 0                                                                                                                              while proc.poll() == None:                                                                                                                 time.sleep(SLEEP_TIME)                                                                                                                 count += SLEEP_TIME                                                                                                                    if count > TIMEOUT:                                                                                                                        proc.terminate()                                                                                                                                                                                                                                                  def isClean(user_input):                                                                                                                   BLACKLIST = [";"]                                                                                                                      for exp in BLACKLIST:                                                                                                                      if exp in user_input:                                                                                                                      return False                                                                                                                   WHITELIST = ["cat", "ls"]                                                                                                              user_input_tokens = user_input.split()                                                                                                 if len(user_input_tokens) > 2:                                                                                                             return False                                                                                                                       if user_input_tokens[0] not in WHITELIST:                                                                                                  return False                                                                                                                       return True                                                                                                                                                                                                                                                               def execute(user_input):                                                                                                                   p = subprocess.Popen(                                                                                                                      user_input.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE                                                                 )                                                                                                                                      timeout(p)                                                                                                                             output = p.communicate()[0].decode()                                                                                                   return output                                                                                                                                                                                                                                                             @app.route('/', methods=['GET', 'POST'])                                                                                               def hello():                                                                                                                               if request.method == 'GET':                                                                                                                return """                                                                                                                     Hello Applicant!                                                                                                                                                                                                                                                              Welcome to your first mission.                                                                                                         We hope you were able to successfully complete training in communicating like Mr. Robot.                                                                                                                                                                                      This machine holds somewhere a golden flag to, however, the developer has not made it easy to find.                                    Using what you have learnt till now, try to find clues that lead to the flag.                                                                                                                                                                                                 Here is a freebie clue: sending a GET request to "/login" always helps.                                                                """                                                                                                                                                                                                                                                                           @app.route('/login', methods=['GET', 'POST'])                                                                                          def login():                                                                                                                               if request.method == 'GET':                                                                                                                if request.cookies.get('uuid') == None:                                                                                                    response = make_response("""                                                                                               It does not seem like you are logged in.                                                                                               Login with credentials provided in the assignment and use the corresponding cookie appropriately.                                      """, 403)                                                                                                                                          return response                                                                                                                    else:                                                                                                                                      uuid = request.cookies.get('uuid')                                                                                                     username = fernet.decrypt(uuid).decode('utf8')                                                                                         response = make_response("""                                                                                               Welcome {}.                                                                                                                                                                                                                                                                   Note that the system is written in Flask.                                                                                              To proceed further: /cmd/<user_input> serves the function:                                                                                                                                                                                                                    @app.route('/cmd/<path:user_input>', methods=['GET'])                                                                                  def execute(user_input):                                                                                                                   p = subprocess.Popen(                                                                                                                      user_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE                                                             )                                                                                                                                      timeout(p)                                                                                                                             output = p.communicate()[0].decode()                                                                                                   return output                                                                                                                                                                                                                                                             """.format(username), 200)                                                                                                                         return response                                                                                                                                                                                                                                                       if request.method == 'POST':                                                                                                               if request.headers.get('Content-Type') == 'application/json':                                                                              data = request.json                                                                                                                    if 'username' in data and 'password' in data and data['password'] == 'icanbemrrobot':                                                      response = make_response('{} logged in successfully'.format(data['username']), 200)                                                    response.mimetype = "text/plain"                                                                                                       response.set_cookie('uuid', fernet.encrypt(data['username'].encode()).decode('utf8'))                                                  return response                                                                                                                    else:                                                                                                                                      return 'JSON parameters not formed correctly (Need username and password)'                                                                                                                                                                                            if 'username' in request.form and 'password' in request.form and request.form['password'] == 'icanbemrrobot':                              response = make_response('{} logged in successfully'.format(request.form['username']), 200)                                            response.mimetype = "text/plain"                                                                                                       response.set_cookie('uuid', fernet.encrypt(request.form['username'].encode()).decode('utf8'))                                          return response                                                                                                                    else:                                                                                                                                      return 'Form parameters not formed correctly (Need username and password)'                                                                                                                                                                                        @app.route('/cmd/<path:user_input>', methods=['GET'])                                                                                  def cmd(user_input):                                                                                                                       if request.method == 'GET':                                                                                                                if request.cookies.get('uuid') == None:                                                                                                    response = make_response("""                                                                                               It does not seem like you are logged in.                                                                                               Login with credentials provided in the assignment and use the corresponding cookie appropriately.                                      """, 403)                                                                                                                                          return response                                                                                                                    else:                                                                                                                                      if not isClean(user_input):                                                                                                                return 'Sorry! No can do'                                                                                                          output = execute(user_input)                                                                                                           response = make_response(output, 200)                                                                                                  return response                                                                                                                                                                                                                                                                                                                                                                                          if __name__ == "__main__":                                                                                                                 app.run(debug=True)