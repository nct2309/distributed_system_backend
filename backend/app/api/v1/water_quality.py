from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...crud.crud_water_quality import crud_water_quality

from ...schemas.water_quality import WaterQuality, WaterQualityRead

router = APIRouter(tags=["water_quality"])

# Read only from warehouse

# by id
@router.get("/water_quality/{id}", response_model=WaterQualityRead)
async def read_water_quality_by_id(id: int, db: AsyncSession = Depends(async_get_db)):
    water_quality = await crud_water_quality.get(db=db, schema_to_select=WaterQualityRead, id=id)
    if not water_quality:
        raise NotFoundException("Water Quality not found")
    return water_quality

# by place: str (1.0, 2.0, ...)
@router.get("/place/{place}", response_model=PaginatedListResponse[WaterQualityRead])
async def read_water_quality_by_place(
    request: Request, 
    db: AsyncSession = Depends(async_get_db),
    place: int = 1,
    page: int = 1,
    items_per_page: int = 10,
):
    """_summary_

    Args:
        place (int): place from 1 to 37
    Returns:
        _type_: _description_
    """
    # float the place
    place = str(float(place))
    offset = compute_offset(page, items_per_page)
    water_qualities = await crud_water_quality.get_multi(db=db, schema_to_select=WaterQualityRead, place__in=[place], offset=offset, sort_columns='time', sort_orders='asc')
    return paginated_response(crud_data=water_qualities, page=page, items_per_page=items_per_page)

# get the list of mapping from place to location
@router.get("/location", response_model=Any)
# get distinct place and its associated location
async def read_water_quality_locations(db: AsyncSession = Depends(async_get_db)):
    res = await crud_water_quality.get_multi(db=db, schema_to_select=WaterQualityRead, columns=['place'], distinct=True)
    
    data = [{"place": d.get('place'), "location": d.get('location')} for d in res.get('data')]
    
    # take out the unique place (convert to float to remove the duplicate)
    unique_place = set([float(d.get('place')) for d in data])
    data = [{"place": int(p), "location": [d.get('location') for d in data if float(d.get('place')) == p][0]} for p in unique_place]
    # sort in float the place
    data = sorted(data, key=lambda x: float(x.get('place')))
    
    return data

from sb3_contrib import RecurrentPPO
from huggingface_hub import hf_hub_download
import numpy as np
from typing import List, Dict, Any

# Download and load the model from Hugging Face
model_path = hf_hub_download(repo_id="nctstuti/ds_btl", filename="rppo_wqi_model.zip")
model = RecurrentPPO.load(model_path)

def prepare_observation(water_quality_data: Dict[str, Any]) -> np.ndarray:
    """
    Prepare the observation data in the format expected by the model.
    Adjust the feature list according to your model's expected input.
    """
    # ph = mapped_column(Float)
    # do = mapped_column(Float)
    # conductivity = mapped_column(Float)
    # n_no2 = mapped_column(Float)
    # n_nh4 = mapped_column(Float)
    # p_po4 = mapped_column(Float)
    # tss = mapped_column(Float)
    # cod = mapped_column(Float)
    # aeromonas_total = mapped_column(Float)
    features = [
        'place', 'ph', 'do', 'conductivity', 'n_no2', 'n_nh4', 'p_po4', 'tss', 'cod', 'aeromonas_total'
    ]
    
    # Create observation array
    obs = np.array([float(water_quality_data.get(feature, 0)) for feature in features], 
                   dtype=np.float32)
    return obs

@router.get("/predict/{place}", response_model=Any)
async def predict_water_quality(
    place: int = 24, 
    db: AsyncSession = Depends(async_get_db)
):
    """_summary_

    Args:
        place (int, optional): _description_. Defaults to 24.
        db (AsyncSession, optional): _description_. Defaults to Depends(async_get_db).

    Returns:
        _type_: _description_
    """
    try:
        # Convert place to string format as per your existing code
        place = str(float(place))
        
        # Get water quality data
        water_qualities = await crud_water_quality.get_multi(
            db=db, 
            schema_to_select=WaterQualityRead, 
            place__in=[place], 
            sort_columns='time', 
            sort_orders='asc'
        )
        
        # Process the data
        data = water_qualities.get('data', [])
        if not data:
            return {"error": "No data available for the specified place"}
            
        # Get the last observation from the first 80% of data
        training_data = data[:int(len(data)*0.8)]
        if not training_data:
            return {"error": "Insufficient data for prediction"}
            
        last_observation = training_data[-1]
        
        # Prepare observation data
        obs = prepare_observation(last_observation)
        
        # # Make prediction
        # action, states = model.predict(
        #     observation=obs,
        #     deterministic=True  # Set to True for consistent predictions
        # )
        
        # # Process the prediction
        # predicted_wqi = float(action[0] * 100)  # Scale back to WQI range
        # Loop to predict for the length of 20% of data
        predicted_wqis = []
        for i in range(int(len(data)*0.8), len(data)):
            obs = prepare_observation(data[i])
            action, states = model.predict(
                observation=obs,
                deterministic=True  # Set to True for consistent predictions
            )
            predicted_wqis.append(float(action[0] * 100))
        
        return {
            'place': place,
            # 'predicted_wqis': predicted_wqis,
            'history': training_data,
            # date list for prediction (in the last 20% of data)
            # 'dates': [d.get('time') for d in data[int(len(data)*0.8):]],
            # join predicted wqis with the date
            "predicted": [{"date": d.get('time'), "predicted_wqi": wqi} for d, wqi in zip(data[int(len(data)*0.8):], predicted_wqis)]
        }
        
    except Exception as e:
        return {
            "error": f"Prediction failed: {str(e)}",
            "details": "Please ensure all required features are present in the input data"
        }