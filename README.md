# AutoDP: Automated Data PreProcessing and Machine Learning Platform



## Description

This Automated Data Preprocessing and Model Training Platform is a user-friendly, no-code solution that empowers users to effortlessly upload, manipulate, and analyze their datasets while seamlessly training machine learning models. With an intuitive interface, it eliminates the need for manual coding and simplifies data preprocessing, model selection, and hyperparameter tuning. This platform ensures data professionals and domain experts can efficiently navigate the machine learning pipeline, fostering data-driven insights and rapid model development for a wide range of applications.

## Architecture Diagram

![Architecture Diagram](diagram.jpg)

## Folder Structure


- `client`: client side code.
  - `src`: Source code.
- `microservices`: Microservices
  - `Data Processing Service`: Performs data preprocessing.
  - `Data Validation Service`: Validates the submitted data.
  - `Model Training Service`: Trains ML Model.
  - `Notification Service`: Notifies on trigger.
  - `Health Monitoring Service`: Keeps track of system health.
  - `Notification Service`: Notifies on trigger.
  - `server.py`: API gateway file
  - `kafka_initializer.py` : Iniitialises Kafka and Zookeeper
  - `bootstrapper.py` : Starts all the microservices

# Microservices

## API Gateway (`server.py`)

- The API gateway serves as the primary interface immediately after the load balancer. 
- It is closely integrated with the Authentication service and functions as a software intermediary between our backend architecture and clients, responsible for directing requests to the appropriate microservices.


## Data Preprocessing Service(Synchronous)

- This service is available for front-end manipulation of data by client. As soon as the user manipulates the dataset, immediately some(Ex:50) rows are processed and immediately sent to the client. 
- This makes sure the seamless data manipulation on front-end. This service is internally communicating with `API gateway` and `Data validation service` via Synchronous REST APIs. 
- For error handling, the data is first validated and then processed.

## Data Preprocessing Service(Asynchronous)

- This is an Asynchronous service for processing of large data. It Reads messages/requests from messaging queues(Kafka) from `Processing Topic` and process the request accordingly.
-  After the data is processed a notification is sent to the user (via `Notification` service) to come and download the processed dataset.
- This service communicates with the synchronous Data Validation service.

## Data Validation Service

- Data validation is required before preprocessing the data, because there can be faulty operations as input(i.e Fill missing values with mean of column in a text column). 
- This is a synchronous service as validating the data with the given operations is not a memory heavy operation. Data is loaded in chunks and then validated, thus making it more efficient. 
- This microservice communicates with `Data Preprocessing Service(Sync and Async both)`.

## Model Training Service

- Model training is the most time and resources(CPU, Memory) consuming microservice in the whole architecture. Thus, operates Asynchronously by communicating with other services via `Kafka`.
- A request contains preprocessing instructions followed by ML algorithm and hyperparameters to apply.
- Communicates with `Data Preprocessing Service(Async)` for preprocessing and Trains the ML model accordingly. Provides the model in '.pkl' format to download.
- A Notification is sent to the user after trainig is completed- via `Notification Service`.

## Health Monitoring Service

- This microservice recieves **heartbeats** from all the other microservices periodically.
- All microservices have a thread running which sends heartbeats meaning 'hey I am alive'.
- When a heartbeat is not recieved from a particular service, then a Notification is sent to the Admin saying 'Please up this service'.

## Notification Service

- Continously listens to the Kafka `Notification Topic` and sends Notification EMails accordingly to user/admin.

## Bootstrapper

- This will UP all the Microservices in backend. Admin will just run this to create instances of all microservices.


## Contributions

Contributions to this project are welcome! If you find any issues or have ideas for improvements, please feel free to open an issue or submit a pull request.

Let's make Kthis scalable!!
