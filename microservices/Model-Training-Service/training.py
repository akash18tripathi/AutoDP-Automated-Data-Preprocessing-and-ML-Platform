from distutils.log import debug
from fileinput import filename
from flask import *
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import requests
import json
from kafka import KafkaConsumer, KafkaProducer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import pickle
import time, threading


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


def trainData(algorithm,x_train,y_train,model_path):
	if algorithm=="LogisticRegression":
		model = LogisticRegression()
		model.fit(x_train,y_train)
		print("===============Model Trained Successfully===========")
		with open(model_path+'/model.pkl', 'wb') as model_file:
			pickle.dump(model, model_file)
			print("===============Model Saved Successfully===========")
		return True
	elif algorithm=="DecisionTree":
		model = DecisionTreeClassifier()
		model.fit(x_train,y_train)
		print("===============Model Trained Successfully===========")
		with open(model_path+'/model.pkl', 'wb') as model_file:
			pickle.dump(model, model_file)
			print("===============Model Saved Successfully===========")
		return True
	elif algorithm=="SVM":
		model = SVC()
		model.fit(x_train,y_train)
		print("===============Model Trained Successfully===========")
		with open(model_path+'/model.pkl', 'wb') as model_file:
			pickle.dump(model, model_file)
			print("===============Model Saved Successfully===========")
		return True
	elif algorithm=="RandomForest":
		model = RandomForestClassifier()
		model.fit(x_train,y_train)
		print("===============Model Trained Successfully===========")
		with open(model_path+'/model.pkl', 'wb') as model_file:
			pickle.dump(model, model_file)
			print("===============Model Saved Successfully===========")
		return True

	return False


def send_heartbeat():
	while True:
		data={"from":"training-service"}
		data = json.dumps(data).encode('utf-8')
		heartbeat_producer.send('health-topic',data)
		print("Sending Heartbeat.......")
		time.sleep(3)  # Add a delay to avoid busy-waiting

# Create a Kafka consumer
consumer = KafkaConsumer('train-topic', bootstrap_servers='localhost:9092')
consumer.subscribe(['train-topic'])
producer = KafkaProducer(bootstrap_servers='localhost:9092')
TOPIC_NAME = 'notification-topic'
heartbeat_producer = KafkaProducer(bootstrap_servers='localhost:9092')
heatbeat_thread = threading.Thread(target=send_heartbeat)
heatbeat_thread.start()


for message in consumer:
    try:
        # Decode the message value as a JSON-encoded string
        json_data = json.loads(message.value.decode('utf-8'))
        path = 'users/'+str(json_data['user_details']['id'])+'/data/'+str(json_data['user_details']['filename'])
        model_dir = 'users/'+str(json_data['user_details']['id'])+'/model'
        data = [json_data['user_details']]+json_data['preprocessCommands']
        val_response = requests.post(url="http://0.0.0.0:5002/get_validated",json=data)	
        df = pd.read_csv(path).head(20)
        if val_response.json()['validation']=='successful':
            print("Validation pass")
            print(data[1:])
            for row in data[1:]:
                df = parseItem(row,df)
            #Preprocess Succesfully
            print("=========== Preprocess SuccessFully!!=============")
            XCols = json_data['selectedXTrains']
            YCols = json_data['selectedYTrain']
            x_train = df[XCols]
            y_train = df[YCols]
            # print(x_train)
            flag = trainData(json_data['selectedAlgorithm'],x_train,y_train,model_dir)
            if flag:
                print("============ Sending Notification.... =============")
                response={"to":"akash18tripathi@gmail.com","subject":"Model Trained and ready to download","message":"Hey, you can collect your trained Model by visiting our platform! Happy Machine Learning...... :)"}
                response = json.dumps(response).encode('utf-8')
                producer.send(TOPIC_NAME,response)
                print("============ Notification Sent! =============")

            else:
                print("============ Model Failed!!! =============")
            
        else:
            print("Validation fail")

        # Process the JSON data

    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)

consumer.close()
