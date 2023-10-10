from flask import *
import pandas as pd
import json
from kafka import KafkaConsumer, KafkaProducer
import time


# Create a Kafka consumer
consumer = KafkaConsumer('health-topic', bootstrap_servers='localhost:9092')
consumer.subscribe(['health-topic'])

producer = KafkaProducer(bootstrap_servers='localhost:9092')

received_services = set()
all_services = {"api-gateway","processing-service","training-service","data-validation-service"}

while True:
    count=0
    print("YESSS")
    for message in consumer:
        try:
            # Decode the message value as a JSON-encoded string
            json_data = json.loads(message.value.decode('utf-8'))
            msgFrom = str(json_data['from'])
            received_services.add(msgFrom)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
        count+=1
        if(count==10):
            break
    for service in all_services:
        if service not in received_services:
            response={"to":"akash18tripathi@gmail.com","subject": "Alert!! " +  str(service) + "is down, ACT fast","message":"Go and up that service!"}
            response = json.dumps(response).encode('utf-8')
            producer.send('notification-topic',response)
            print("Notification sent for "+str(service))
        else:
            print("Heartbeat recieved from"+ str(service))
    received_services.clear()
    time.sleep(3)


consumer.close()
