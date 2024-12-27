import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv('https://drive.google.com/uc?export=download&id=1Mux3k8va5dVI7C7kvK0Dix6L-QYTxFn0')

# Example preprocessing
data.ffill()
data.dropna(subset=['pH', 'DO', 'Độ dẫn', 'N-NO2', 'N-NH4', 'P-PO4', 'TSS', 'COD', 'Aeromonas tổng số'], inplace=True)

# Define the feature columns and target variable
features = ['pH', 'DO', 'Độ dẫn', 'N-NO2', 'N-NH4', 'P-PO4', 'TSS', 'COD', 'Aeromonas tổng số']
# features = ['latitude', 'longitude', 'Place', 'Nhiệt độ', 'pH', 'DO', 'Độ dẫn', 'Độ kiềm', 'N-NO2', 'N-NH4', 'P-PO4', 'TSS', 'COD', 'Aeromonas tổng số']
# features = ['DO', 'TSS',  'Aeromonas tổng số', 'N-NH4']
target = 'WQI'
# features = ['Aeromonas tổng số']
# target = 'Aeromonas tổng số'

data['H2S'] = data['H2S'].replace({'KPH': 0})
data['pH'] = data['pH'].replace({'KPH': 0})
data['DO'] = data['DO'].replace({'KPH': 0})
data['Độ dẫn'] = data['Độ dẫn'].replace({'KPH': 0})
data['N-NO2'] = data['N-NO2'].replace({'KPH': 0})
data['N-NH4'] = data['N-NH4'].replace({'KPH': 0})
data['P-PO4'] = data['P-PO4'].replace({'KPH': 0})
data['TSS'] = data['TSS'].replace({'KPH': 0})
data['COD'] = data['COD'].replace({'KPH': 0})
data['Aeromonas tổng số'] = data['Aeromonas tổng số'].replace({'KPH': 0,'< 1':0, '<1':0})
data['Aeromonas tổng số'] = data['Aeromonas tổng số'].astype(float)
data['Coliform'] = data['Coliform'].replace({'KPH': 0})
numeric_columns = [
    'Nhiệt độ', 'pH', 'DO', 'Độ dẫn', 'Độ kiềm', 'N-NO2', 'N-NH4',
    'P-PO4', 'TSS', 'H2S', 'COD', 'Coliform'
]
data[numeric_columns] = data[numeric_columns].replace(',', '.', regex=True).apply(pd.to_numeric, errors='coerce')
data['Ngày quan trắc'] = pd.to_datetime(data['Ngày quan trắc'], format='%d/%m/%Y', errors='coerce')

data['date'] = pd.to_datetime(data['Ngày quan trắc'], dayfirst=True)
data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data['day'] = data['date'].dt.day
data = data.sort_values(by='date')

# Step 1: Clean the 'Tọa độ' column to replace "\n" with a space and remove extra spaces
data['Tọa độ'] = data['Tọa độ'].str.replace(' ', '').str.strip()
data['Tọa độ'] = data['Tọa độ'].str.replace('\n', ' ').str.strip()

# Step 2: Drop rows with invalid or malformed entries
data = data[data['Tọa độ'].str.contains(r'^\d{1,2},\d+\s\d{1,3},\d+$', na=False)]

# Step 3: Split the 'Tọa độ' column into 'latitude' and 'longitude'
data[['latitude', 'longitude']] = data['Tọa độ'].str.split(' ', expand=True)

# Step 4: Replace commas with dots and convert to float
data['latitude'] = data['latitude'].str.replace(',', '.').astype(float)
data['longitude'] = data['longitude'].str.replace(',', '.').astype(float)

# print(data.describe())
# distinct_latitudes = data['latitude'].unique()
# print("Distinct latitudes:", distinct_latitudes)
# print("Number of distinct latitudes:", len(distinct_latitudes))

# distinct_longitudes = data['longitude'].unique()
# print("Distinct longitudes:", distinct_longitudes)
# print("Number of distinct longitudes:", len(distinct_longitudes))

data = data.dropna(subset=['pH', 'DO','Độ dẫn', 'N-NO2','P-PO4', 'N-NH4','TSS',
                'COD','Aeromonas tổng số', 'WQI'])

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
from datetime import datetime
from app.models.water_quality import WaterQuality

# Setup the database engine and session
DATABASE_URL = 'postgresql+asyncpg://neondb_owner:jPRzLtEVNc30@ep-tight-snowflake-a1kwshu4.ap-southeast-1.aws.neon.tech/neondb'
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_recycle=3600)
Session = async_sessionmaker(async_engine, class_=AsyncSession)

# Define your Base
Base = declarative_base()

# Insert data function
async def insert_water_quality_data(session: AsyncSession, data: pd.DataFrame):
    # Loop through each row of the DataFrame and insert the data
    for _, row in data.iterrows():
        # Extract the required columns and map them to the WaterQuality class
        water_quality = WaterQuality(
            time=row['Ngày quan trắc'],  # Ensure that this is the correct column for 'time'
            place=str(row['Place']),  # Assuming 'Place' column exists in your DataFrame
            location=row['Điểm Quan Trắc'],  # 'Điểm Quan Trắc' corresponds to the location
            ph=row['pH'],
            do=row['DO'],
            conductivity=row['Độ dẫn'],
            n_no2=row['N-NO2'],
            n_nh4=row['N-NH4'],
            p_po4=row['P-PO4'],
            tss=row['TSS'],
            cod=row['COD'],
            aeromonas_total=row['Aeromonas tổng số'],
            actual_wqi=row['WQI'],
            predicted_wqi=row['WQI'],
        )
        
        # Add the object to the session
        session.add(water_quality)

    # Commit the session to the database
    await session.commit()

# Function to run the insert task
async def run_insert():
    async with Session() as session:
        await insert_water_quality_data(session, data)

# Running the insertion task (Make sure you have an asyncio event loop)
import asyncio
asyncio.run(run_insert())