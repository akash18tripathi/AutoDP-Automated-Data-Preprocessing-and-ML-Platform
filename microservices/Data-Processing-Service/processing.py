from distutils.log import debug
from fileinput import filename
from flask import *
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import requests
from pandas_profiling import ProfileReport
from kafka import KafkaProducer, KafkaConsumer
import time
import threading
import logging




app = Flask(__name__)
logging.basicConfig(filename='./app.log', level=logging.INFO)

producer = KafkaProducer(bootstrap_servers='localhost:9092')
TOPIC_NAME = 'processing-topic'


# @app.route('/')
# def main():
# 	return render_template('index.html')

def parseItem(item,df):
	try:
		# item has colVal, option1, option2,option3
		if item['option1']=='Normalization':
			if(item['option2']=='Min-Max Scaling'):
				mms = MinMaxScaler()
				df[item['colVal']] = mms.fit_transform(df[item['colVal']].values.reshape(-1,1))
				return df
			elif(item['option2']=='Z-Score'):
				mean = df[item['colVal']].mean()
				std =df[item['colVal']].std()
				df[item['colVal']] = (df[item['colVal']] - mean) / std
				return df
			elif(item['option2']=='Robust Scaling'):
				median = df[item['colVal']].median()
				q1 = df[item['colVal']].quantile(0.25)
				q3 = df[item['colVal']].quantile(0.75)
				iqr = q3 - q1
				# Apply robust scaling
				df[item['colVal']] = (df[item['colVal']] - median) / iqr
				return df
		elif item['option1']=='Missing':
			if(item['option2']=='Delete'):
				df = df.dropna(subset=[item['colVal']])
				return df
			elif(item['option2']=='Mean'):
				mean_value = df[item['colVal']].mean()
				df[item['colVal']].fillna(mean_value, inplace=True)
				return df
			elif(item['option2']=='Median'):
				median_value = df[item['colVal']].mean()
				df[item['colVal']].fillna(median_value, inplace=True)
				return df
		elif item['option1']=='Encoding':
			if(item['option2']=='Label Encoding'):
				label_encoder = LabelEncoder()
				df[item['colVal']]=label_encoder.fit_transform(df[item['colVal']])
				return df
			elif(item['option2']=='One Hot Encoding'):
				one_hot_encoder = OneHotEncoder(sparse=False)
				one_hot_encoded = one_hot_encoder.fit_transform(df[item['colVal']].values.reshape(-1,1))
				one_hot_encoded = pd.DataFrame(one_hot_encoded, columns=[f"{item['colVal']}_{cls}" for cls in one_hot_encoder.categories_[0]])
				df=pd.concat([df, one_hot_encoded], axis=1)
				return df
		elif item['option1']=='Remove Column':
			df = df.drop([item['colVal']],axis=1)
			return df
	except:
		return df

	return df


# @app.route('/hello')
# def hello():
# 	return {"message":"hello world"}

def send_heartbeat():
	while True:
		data={"from":"processing-service"}
		data = json.dumps(data).encode('utf-8')
		heartbeat_producer.send('health-topic',data)
		print("Sending Heartbeat.......")
		time.sleep(3)  # Add a delay to avoid busy-waiting


@app.route('/dummy_preprocess', methods = ['POST'])
def getItems():
	data =request.json
	logging.info(time.time()+": /dummy_preprocess POST hit by "+ str(data[0]['id']))

	path = 'users/'+str(data[0]['id'])+'/data/'+str(data[0]['filename'])
	json_data = requests.post(url="http://0.0.0.0:5002/get_validated",json=data)
	df = pd.read_csv(path).head(20)
	if json_data.json()['validation']=='successful':
		print("Validation pass")
		for row in data[1:]:
			df = parseItem(row,df)
		json_data = df.to_json(orient='records')
		return jsonify(json_data)
	else:
		print("Validation fail")
		json_data = df.to_json(orient='records')
		return jsonify(json_data)

@app.route('/get_summary', methods = ['POST'])
def getSummary():
	data =request.json
	logging.info(time.time()+": /get_summary POST hit by "+ str(data[0]['id']))
	path = 'users/'+str(data[0]['id'])+'/data/'+str(data[0]['filename'])
	json_data = requests.post(url="http://0.0.0.0:5002/get_validated",json=data)
	df = pd.read_csv(path)
	if json_data.json()['validation']=='successful':
		print("Validation pass")
		profile = ProfileReport(df)
		# Save the report as an HTML file
		report_path = '/home/aakash/workdir/Project/report.html'
		profile.to_file(report_path)
		with open(report_path, 'r') as file:
			html_content = file.read()
		resp = make_response(html_content)
		# resp.headers["Content-Disposition"] = "attachment; filename=report.html"
		resp.headers["Content-Type"] = "text/html"
		del df
		return resp
		# return jsonify(json_data)
	else:
		print("Validation fail")
		# json_data = df.to_json(orient='records')
		return jsonify({'Validation':'Failed'})

@app.route('/preprocess', methods = ['POST'])
def preProcess():
	data =request.json
	# print(data[0])
	logging.info(time.time()+": /preprocess POST hit by "+ str(data[0]['id']))
	path = 'users/'+str(data[0]['id'])+'/data/'+str(data[0]['filename'])
	# json_data = requests.post(url="http://0.0.0.0:5002/get_validated",json=data)	
	# print(json_data)
	data = {'id':data[0]['id'],'filename':path}
	data = json.dumps(data).encode('utf-8')
	producer.send('processing-topic',data)


	return {"message","Request Sent, You can Chill"}

@app.route('/download_data', methods = ['POST'])
def preProcess():
	data =request.json
	# print(data[0])
	logging.info(time.time()+": /download_data POST hit by "+ str(data[0]['id']))
	path = 'users/'+str(data[0]['id'])+'/data/'+str(data[0]['filename'])
	# json_data = requests.post(url="http://0.0.0.0:5002/get_validated",json=data)	
	# print(json_data)
	df = pd.read_csv(path)
	resp = make_response(df.to_csv())
	resp.headers["Content-Disposition"] = "attachment; filename=data.csv"
	resp.headers["Content-Type"] = "text/csv"
	del df

	return resp

if __name__ == '__main__':
	heartbeat_producer = KafkaProducer(bootstrap_servers='localhost:9092')
	heatbeat_thread = threading.Thread(target=send_heartbeat)
	heatbeat_thread.start()
	app.run(port=5001,debug=True)