from distutils.log import debug
from fileinput import filename
from flask import *
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import requests
import threading, time
from kafka import KafkaProducer


app = Flask(__name__)

heartbeat_producer = KafkaProducer(bootstrap_servers='localhost:9092')


def send_heartbeat():
	while True:
		data={"from":"data-validation-service"}
		data = json.dumps(data).encode('utf-8')
		heartbeat_producer.send('health-topic',data)
		print("Sending Heartbeat.......")
		time.sleep(3)  # Add a delay to avoid busy-waiting

def isItemValid(item,df):
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
	except:
		return False

	return df


@app.route('/get_validated', methods = ['POST'])
def getItems():
    data =request.json
    path = 'users/'+str(data[0]['id'])+'/data/'+str(data[0]['filename'])
    df = pd.read_csv(path).head()
    # with open(json_file_path, 'r') as json_file:
    #     config_data = json.load(json_file)
    for row in data[1:]:
        df = isItemValid(row,df)
        if isinstance(df, pd.DataFrame):
            continue
        elif df is False:
            return jsonify({'validation': 'failed'}) 
    return jsonify({'validation': 'successful'})

if __name__ == '__main__':
	heartbeat_producer = KafkaProducer(bootstrap_servers='localhost:9092')
	heatbeat_thread = threading.Thread(target=send_heartbeat)
	heatbeat_thread.start()
	app.run(port=5002,debug=True)