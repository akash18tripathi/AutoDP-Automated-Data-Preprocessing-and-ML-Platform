from distutils.log import debug
from fileinput import filename
from flask import *
import pandas as pd
import requests
import os
# from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from kafka import KafkaProducer
import threading
import time




app = Flask(__name__)
#Fill MONGODB Details here.
app.config['MONGO_URI'] = ''
app.secret_key = '574840d7-bb58-43e2-aab8-58f81ffb20e0'

client = MongoClient(app.config['MONGO_URI'])
db = client['AutoDP-Login-Service']  # Replace with your database name
users_collection = db['users'] 


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
producer = KafkaProducer(bootstrap_servers='localhost:9092')
heartbeat_producer = KafkaProducer(bootstrap_servers='localhost:9092')





class User(UserMixin):
	def __init__(self, username,filename):
		self.id = username
		self.__password = ""
		self.filename=filename
	def setPass(self,password):
		self.__password = password


def send_heartbeat():
	while True:
		print("Sending Heartbeat.......")
		data={"from":"api-gateway"}
		data = json.dumps(data).encode('utf-8')
		heartbeat_producer.send('health-topic',data)
		time.sleep(3)  # Add a delay to avoid busy-waiting

@app.route('/hello')
def hello():
	return {"message":"hello world"}

@app.route('/register', methods=['POST'])
def register():
	data = request.json
	username = data['username']
	password = data['password']
	
	# existing_user = mongo.db.users.find_one({'username': username})
	if False:
		return jsonify({'message': 'Username already exists'}), 400
	
	new_user = {
		'username': username,
		'password': password,
		'filename':""
	}
	# os.makedirs('users/'+username)

	users_collection.insert_one(new_user)
	return jsonify({'message': 'Registration successful'})

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(username):
	user = users_collection.find_one({'username': str(username)})
	if user:
		print(user)
		return User(username,user.get('filename'))


@app.route('/login', methods=['POST'])
def login():
	data = request.json
	username = data['username']
	password = data['password']

	# print("YESS")

	user = list(users_collection.find({'username': str(username), 'password': str(password)}))
	if user:
		# token_payload = {
		#	 'username': username,
		#	 'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time
		# }
		# token = jwt.encode(token_payload, 'your-secret-key', algorithm='HS256')
		user = User(username,"")
		user.setPass(password)
		login_user(user)
		if not os.path.exists('users/'+ current_user.id+'/data/'):
			os.makedirs('users/'+ current_user.id+'/data/')
		if not os.path.exists('users/'+ current_user.id+'/model/'):
			os.makedirs('users/'+ current_user.id+'/model/')
		return jsonify({'message': 'Login successful', 'token': "1234"})
	else:
		print("NOT FOUND")
		return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/upload', methods = ['POST'])
def uploadData():
	if request.method == 'POST':
		# print(current_user.id)
		
		if not os.path.exists('users/'+ current_user.id+'/data/'):
			os.makedirs('users/'+ current_user.id+'/data/')
		
		f = request.files['file']
		print(f.filename)
		try:
			users_collection.update_one({'username': str(current_user.id)},{"$set":{"filename": str(f.filename)}})
		except Exception as e:
			print(e)
			return {"message":"Invalid return type!"}
		dataPath = 'users/'+ str(current_user.id)+'/data/'+str(f.filename)
		f.save(dataPath)
		df = pd.read_csv(dataPath,nrows=20,encoding='utf-8')
		json_data = df.to_json(orient='records')
		return jsonify(json_data)
	return {"message":"Invalid return type!"}

@app.route('/get_items', methods = ['POST'])
def getItems():
	data = request.json  # Retrieve JSON data from the request
	itemDetails={'id':current_user.id,'filename':current_user.filename}
	# print("FILEEE: "+ current_user.filename)
	data = [itemDetails]+ data
	json_data = requests.post(url="http://0.0.0.0:5001/dummy_preprocess",json=data)	
	return json_data.json()

@app.route('/get_summary', methods = ['GET'])
def getSummary():
	itemDetails={'id':current_user.id,'filename':current_user.filename}
	# print("FILEEE: "+ current_user.filename)
	data = [itemDetails]
	file_response = requests.post(url="http://0.0.0.0:5001/get_summary",json=data)	
	html_content = file_response.text

    # Create a response to serve the HTML content for download
	response = make_response(html_content)
	response.headers['Content-Disposition'] = 'attachment; filename=report.html'
	response.headers['Content-Type'] = 'text/html'

	return response

@app.route('/preprocess_data', methods = ['POST'])
def preProcess():
	data = request.json  # Retrieve JSON data from the request
	itemDetails={'id':current_user.id,'filename':current_user.filename}
	# print("FILEEE: "+ current_user.filename)
	data = [itemDetails]+ data
	file_response = requests.post(url="http://0.0.0.0:5001/preprocess",json=data)
	response = Response(file_response.content, content_type='text/csv')
	response.headers['Content-Disposition'] = file_response.headers['Content-Disposition']
	return response

@app.route('/train_data', methods = ['POST'])
def train():
	data = request.json  # Retrieve JSON data from the request
	data['user_details']={'id':current_user.id,'filename':current_user.filename}
	# print("FILEEE: "+ current_user.filename)
	print(data)
	data = json.dumps(data).encode('utf-8')
	producer.send('train-topic',data)

	# file_response = requests.post(url="http://0.0.0.0:5001/preprocess",json=data)
	# response = Response(file_response.content, content_type='text/csv')
	# response.headers['Content-Disposition'] = file_response.headers['Content-Disposition']
	return {"message":"Success"}


@app.route('/download_model', methods = ['GET'])
def downloadModel():
	# print("FILEEE: "+ current_user.filename)
    # Create a response to serve the HTML content for download
	try:
		model_path = 'users/'+str(current_user.id)+'/model/model.pkl'
		response = make_response(send_file(model_path, as_attachment=True))
		response.headers['Content-Type'] = 'application/octet-stream'
		response.headers['Content-Disposition'] = 'attachment; filename=model.pkl'
		return response
	except Exception as e:
		print(e)
		return {"message":"Model Not Found!"}

if __name__ == '__main__':
	heatbeat_thread = threading.Thread(target=send_heartbeat)
	heatbeat_thread.start()
	app.run(port=5000,debug=True)
