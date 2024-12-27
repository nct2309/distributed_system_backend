from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, split, to_date, lit
from pyspark.sql.types import FloatType, StringType, DateType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Water Quality Data Processing") \
    .getOrCreate()

# Load dataset
data = spark.read.csv("https://drive.google.com/uc?export=download&id=1Mux3k8va5dVI7C7kvK0Dix6L-QYTxFn0", header=True, inferSchema=True)

# Data Preprocessing
data = data.fillna(method="ffill") \
    .dropna(subset=["pH", "DO", "Độ dẫn", "N-NO2", "N-NH4", "P-PO4", "TSS", "COD", "Aeromonas tổng số"])

# Replace specific values in columns
replace_values = {
    "H2S": {"KPH": "0"},
    "pH": {"KPH": "0"},
    "DO": {"KPH": "0"},
    "Độ dẫn": {"KPH": "0"},
    "N-NO2": {"KPH": "0"},
    "N-NH4": {"KPH": "0"},
    "P-PO4": {"KPH": "0"},
    "TSS": {"KPH": "0"},
    "COD": {"KPH": "0"},
    "Aeromonas tổng số": {"KPH": "0", "< 1": "0", "<1": "0"},
    "Coliform": {"KPH": "0"},
}
for column, replacements in replace_values.items():
    for old_value, new_value in replacements.items():
        data = data.withColumn(column, regexp_replace(col(column), old_value, new_value))

# Convert numeric columns
numeric_columns = [
    "Nhiệt độ", "pH", "DO", "Độ dẫn", "Độ kiềm", "N-NO2", "N-NH4",
    "P-PO4", "TSS", "H2S", "COD", "Coliform"
]
for column in numeric_columns:
    data = data.withColumn(column, regexp_replace(col(column), ",", ".").cast(FloatType()))

# Process 'Ngày quan trắc' column
data = data.withColumn("date", to_date(col("Ngày quan trắc"), "dd/MM/yyyy"))
data = data.withColumn("year", col("date").cast("int")) \
    .withColumn("month", col("date").cast("int")) \
    .withColumn("day", col("date").cast("int"))

# Process 'Tọa độ' column
data = data.withColumn("Tọa độ", regexp_replace(col("Tọa độ"), "\n", " ")) \
    .withColumn("Tọa độ", regexp_replace(col("Tọa độ"), " ", "")) \
    .filter(col("Tọa độ").rlike(r"^\d{1,2},\d+\s\d{1,3},\d+$"))

# Split 'Tọa độ' into latitude and longitude
data = data.withColumn("latitude", split(col("Tọa độ"), " ")[0]) \
    .withColumn("longitude", split(col("Tọa độ"), " ")[1]) \
    .withColumn("latitude", regexp_replace(col("latitude"), ",", ".").cast(FloatType())) \
    .withColumn("longitude", regexp_replace(col("longitude"), ",", ".").cast(FloatType()))

# Drop rows with null values in required columns
required_columns = ["pH", "DO", "Độ dẫn", "N-NO2", "P-PO4", "N-NH4", "TSS", "COD", "Aeromonas tổng số", "WQI"]
data = data.dropna(subset=required_columns)

# Define the database writing function
def write_to_db(partition):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.water_quality import WaterQuality
    import asyncio

    DATABASE_URL = "postgresql+asyncpg://neondb_owner:jPRzLtEVNc30@ep-tight-snowflake-a1kwshu4.ap-southeast-1.aws.neon.tech/neondb"
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine, class_=AsyncSession)

    async def insert_partition(partition_data):
        async with Session() as session:
            for row in partition_data:
                water_quality = WaterQuality(
                    time=row["Ngày quan trắc"],
                    place=row.get("Place", ""),
                    location=row.get("Điểm Quan Trắc", ""),
                    ph=row["pH"],
                    do=row["DO"],
                    conductivity=row["Độ dẫn"],
                    n_no2=row["N-NO2"],
                    n_nh4=row["N-NH4"],
                    p_po4=row["P-PO4"],
                    tss=row["TSS"],
                    cod=row["COD"],
                    aeromonas_total=row["Aeromonas tổng số"],
                    actual_wqi=row["WQI"],
                    predicted_wqi=row["WQI"],
                )
                session.add(water_quality)
            await session.commit()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(insert_partition(partition))

# Write data to database using foreachPartition
data.foreachPartition(write_to_db)

spark.stop()
