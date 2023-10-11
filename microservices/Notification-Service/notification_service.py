import json
from kafka import KafkaConsumer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




# Create a Kafka consumer
TOPIC_NAME = 'notification-topic'
MAIL_KEY='nizo cout yblx dqzq'

consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers='localhost:9092')
consumer.subscribe([TOPIC_NAME])


for message in consumer:
    try:
        # Decode the message value as a JSON-encoded string
        json_data = json.loads(message.value.decode('utf-8'))
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587  # TLS port
        receiver_email = json_data['to']
        sender_password =  MAIL_KEY
        sender_email = 'aakash.temporary@gmail.com'

        # Create a multipart message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = json_data['subject']

        # Add the message body (plain text or HTML)
        message.attach(MIMEText(json_data['message'], 'plain'))

        # Create an SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS (Transport Layer Security)
            server.login(sender_email, sender_password)  # Login to your email account
            # Send the email
            server.sendmail(sender_email, receiver_email, message.as_string())

        print('=========== Email sent successfully. =============')

    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)

consumer.close()
