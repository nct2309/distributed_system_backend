import pandas as pd
from confluent_kafka import Producer
import threading

# Load CSV Data
csv_url = 'https://drive.google.com/uc?export=download&id=1Mux3k8va5dVI7C7kvK0Dix6L-QYTxFn0'
data = pd.read_csv(csv_url)

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',  # Update with your Kafka broker
    'client.id': 'water-quality-producer'
}

producer = Producer(conf)

# Define topic names for each feature
topics = {
    "pH": "ph_topic",
    "DO": "do_topic",
    "Độ dẫn": "conductivity_topic",
    "N-NO2": "n_no2_topic",
    "N-NH4": "n_nh4_topic",
    "P-PO4": "p_po4_topic",
    "TSS": "tss_topic",
    "COD": "cod_topic",
    "Aeromonas tổng số": "aeromonas_total_topic"
}

def delivery_report(err, msg):
    """ Callback for producer delivery reports """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Function to send a row of data to Kafka topics
def send_to_kafka(row):
    observation_date = row["Ngày quan trắc"]
    
    for feature, topic in topics.items():
        if feature in row:
            message = {
                "Ngày quan trắc": observation_date,
                "value": row[feature]
            }
            # Produce message to the Kafka topic
            producer.produce(
                topic=topic,
                key=str(observation_date),
                value=str(message),
                callback=delivery_report
            )
    producer.flush()  # Ensure all messages are sent before moving to the next row

# Create a thread for each row to send data concurrently
threads = []
for index, row in data.iterrows():
    thread = threading.Thread(target=send_to_kafka, args=(row,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All data has been produced.")