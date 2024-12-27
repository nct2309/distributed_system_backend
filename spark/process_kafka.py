from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit, udf
from pyspark.sql.types import StructType, StructField, StringType, FloatType

# Define the WQI calculation functions
def calculate_PH_value(ph):
    if ph < 5.5:
        return 1
    elif 5.5 <= ph < 6.5:
        return 99 * ph - 543.5
    elif 6.5 <= ph < 8.5:
        return 100
    elif 8.5 <= ph < 9.5:
        return -99 * ph + 941.5
    else:
        return 1

def calculate_EC_value(value):
    if value <= 1500:
        return 100
    elif 1500 < value < 4500:
        return -0.033 * value + 149.5
    else:
        return 1

def calculate_qDO(DO):
    if DO <= 3:
        return 1
    elif 3 < DO < 5:
        return 49.5 * DO - 147.5
    elif 5 <= DO < 7:
        return 100
    elif 7 <= DO < 11:
        return -24.75 * DO + 273.25
    else:
        return 1

def calculate_qTSS(TSS):
    if TSS <= 50:
        return 100
    elif 50 < TSS < 150:
        return -0.99 * TSS + 149.5
    else:
        return 1

def calculate_qCOD(COD):
    if COD <= 10:
        return 100
    elif 10 < COD < 20:
        return -9.9 * COD + 199
    else:
        return 1

def calculate_qNNH4(vl):
    if vl <= 0.3:
        return 100
    elif 0.3 < vl < 1.7:
        return -70.71 * vl + 121.21
    else:
        return 1

def calculate_qNNO2(vl):
    if vl <= 0.1:
        return 100
    elif 0.1 < vl < 1:
        return -111.1 * vl + 111
    else:
        return 1

def calculate_qPPO4(vl):
    if vl <= 0.1:
        return 100
    elif 0.1 < vl < 0.5:
        return -247.5 * vl + 124.75
    else:
        return 1

def calculate_qAeromonas(vl):
    if vl <= 1000:
        return 100
    elif 1000 < vl < 3000:
        return -0.0495 * vl + 149.5
    else:
        return 1

def safe_power(x, power, decimals=8):
    if x < 0:
        return None
    else:
        return round(x ** power, decimals)

def calculate_WQI(ph, DO, EC, N_NO2, N_NH4, P_PO4, TSS, COD, Aeromonas):
    try:
        q_ph = safe_power(calculate_PH_value(ph), 0.11)
        q_EC = safe_power(calculate_EC_value(EC), 0.06)
        q_DO = safe_power(calculate_qDO(DO), 0.1)
        q_TSS = safe_power(calculate_qTSS(TSS), 0.13)
        q_COD = safe_power(calculate_qCOD(COD), 0.1)
        q_N_NH4 = safe_power(calculate_qNNH4(N_NH4), 0.13)
        q_N_NO2 = safe_power(calculate_qNNO2(N_NO2), 0.1)
        q_P_PO4 = safe_power(calculate_qPPO4(P_PO4), 0.12)
        q_Aeromonas = safe_power(calculate_qAeromonas(Aeromonas), 0.15)

        WQI = round(q_ph * q_EC * q_DO * q_TSS * q_COD * q_N_NH4 * q_N_NO2 * q_P_PO4 * q_Aeromonas, 4)
        return WQI
    except:
        return None
    
# Define the schema for each topic's data
topic_schema = StructType([
    StructField("Ngày quan trắc", StringType(), True),
    StructField("value", FloatType(), True)
])

# Initialize Spark session
spark = SparkSession.builder \
    .appName("WQI-Calculation") \
    .config("spark.jars", "postgresql-42.2.18.jar") \
    .getOrCreate()

# Kafka broker and topics configuration
KAFKA_BROKER = "localhost:9092"
TOPICS = [
    "ph_topic", "do_topic", "conductivity_topic", "n_no2_topic",
    "n_nh4_topic", "p_po4_topic", "tss_topic", "cod_topic", "aeromonas_total_topic"
]

# Create Kafka DataFrame for each topic
streams = {
    topic: spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", topic)
    .option("startingOffsets", "earliest")
    .load()
    .select(from_json(col("value").cast("string"), topic_schema).alias("data"))
    .select(col("data.*")) for topic in TOPICS
}

# Join all the topics on "Ngày quan trắc"
joined_stream = streams["ph_topic"].alias("ph")
for topic, stream in streams.items():
    if topic != "ph_topic":
        joined_stream = joined_stream.join(
            stream.alias(topic),
            on="Ngày quan trắc",
            how="inner"
        )

# Rename columns to meaningful names
renamed_stream = joined_stream.select(
    col("Ngày quan trắc").alias("observation_date"),
    col("ph.value").alias("ph"),
    col("do_topic.value").alias("do"),
    col("conductivity_topic.value").alias("conductivity"),
    col("n_no2_topic.value").alias("n_no2"),
    col("n_nh4_topic.value").alias("n_nh4"),
    col("p_po4_topic.value").alias("p_po4"),
    col("tss_topic.value").alias("tss"),
    col("cod_topic.value").alias("cod"),
    col("aeromonas_total_topic.value").alias("aeromonas_total")
)

# Define UDFs for WQI calculation
def calculate_WQI_udf(ph, do, conductivity, n_no2, n_nh4, p_po4, tss, cod, aeromonas_total):
    # Reuse your calculate_WQI function here
    return calculate_WQI(ph, do, conductivity, n_no2, n_nh4, p_po4, tss, cod, aeromonas_total)

wqi_udf = udf(calculate_WQI_udf, FloatType())

# Apply WQI calculation
processed_stream = renamed_stream.withColumn(
    "wqi",
    wqi_udf(
        col("ph"), col("do"), col("conductivity"),
        col("n_no2"), col("n_nh4"), col("p_po4"),
        col("tss"), col("cod"), col("aeromonas_total")
    )
)

# Define a function to write to PostgreSQL
def write_to_postgres(batch_df, batch_id):
    db_properties = {
        "user": "your_user",
        "password": "your_password",
        "driver": "org.postgresql.Driver"
    }
    db_url = "jdbc:postgresql+asyncpg://neondb_owner:jPRzLtEVNc30@ep-tight-snowflake-a1kwshu4.ap-southeast-1.aws.neon.tech/neondb"

    batch_df.write \
        .format("jdbc") \
        .option("url", db_url) \
        .option("dbtable", "water_quality") \
        .mode("append") \
        .save()

# Write the processed stream to PostgreSQL
query = processed_stream.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

query.awaitTermination()