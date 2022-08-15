import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import *
from functools import wraps

app = Flask(__name__)

config = {
	"apiKey": "AIzaSyCjbdf9d0HE-fu8R4nMzzADBqzbCxC_GCA",
	"authDomain": "webpageflaskfirebase.firebaseapp.com",
	"databaseURL": "",
	"projectId": "webpageflaskfirebase",
	"storageBucket": "webpageflaskfirebase.appspot.com",
	"messagingSenderId": "802274479089",
	"appId": "1:802274479089:web:f034797ed7f99879bdd250",
	"measurementId": "G-BN8N32YXET"
}

cre = credentials.Certificate("firebase-sdk.json")
firebase = firebase_admin.initialize_app(cre)
db = firestore.client()

pyfirebase = pyrebase.initialize_app(config)
pyauth = pyfirebase.auth()

def check_token(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if not request.headers.get('authorization'):
			return {'message': 'No token provided'},400
		try:
			user = auth.verify_id_token(request.headers['authorization'])
			userobj = db.collection('users').document(user['uid']).get().to_dict()
			request.user = user
			request.user["user"] = userobj
		except:
			return {'message':'Invalid token provided.'},400
		return f(*args, **kwargs)
	return wrap


@app.route('/login', methods=['POST'])
def login():
	try:
		email = request.json.get('email')
		password = request.json.get('password')
		user = pyauth.sign_in_with_email_and_password(email, password)
		userobj = db.collection('users').document(user['localId']).get().to_dict()
		return {
			'token':user['idToken'],
			'user' : userobj
		},200
	except Exception as e:
		return {'message':str(e)}


@app.route('/register', methods=['POST'])
def register():
	email = request.json.get('email')
	password = request.json.get('password')
	name = request.json.get('name')
	empid = request.json.get('empid')
	user_type = "nuser"

	if(email.endswith("abccompany.com")):
		try:
			user = pyauth.create_user_with_email_and_password(email=email,password=password)
			userobj={
				"email":email,
				"name":name,
				"empid":empid,
				"user_type":user_type
				}
			db.collection('users').document(user['localId']).set(userobj)
			return {'message': f'Successfully created user {user}'},200
		except Exception as e:
			return {'message': str(e)},400
			
	else:
		return {'message': f'Enter you org email'},400


@app.route('/user', methods=['GET'])
@check_token
def userinfo():
	return {'data':request.user}, 200

@app.route('/logout', methods=['POST'])
@check_token
def logout():
	# uid = request.user["uid"]
	# auth.revoke_refresh_tokens(uid)
	return {'data':'logged out'}, 200


if __name__ == '__main__':
	app.run(debug=True)



























