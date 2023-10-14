from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

# Define the Kafka broker(s) and topic name
bootstrap_servers = 'localhost:9092'
topic_list = ['train-topic','notification-topic','health-topic','processing-topic']

# Create a KafkaAdminClient
admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
topics = admin_client.list_topics()

# Extract the topic names
topic_names = [topic for topic in topics]

# Check if the topic already exists
for topic_name in topic_list:
    if topic_name not in topic_names:
        try:
            # Create a NewTopic instance with the topic name, number of partitions, and replication factor
            new_topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)

            # Create the topic
            admin_client.create_topics([new_topic])

            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")
    else:
        print(f"Topic '{topic_name}' already exists.")

# Close the admin client when done
admin_client.close()
