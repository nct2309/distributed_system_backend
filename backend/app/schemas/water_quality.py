from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
    

class WaterQualityBase(BaseModel):
    time: Annotated[datetime, Field(examples=["2022-01-01T00:00:00"])]
    place: Annotated[str, Field(examples=["Kandy"])]
    location: Annotated[str, Field(examples=["Kandy Lake"])]
    ph: Annotated[float, Field(examples=[6.5])]
    do: Annotated[float, Field(examples=[7.5])]
    conductivity: Annotated[float, Field(examples=[0.5])]
    n_no2: Annotated[float, Field(examples=[0.5])]
    n_nh4: Annotated[float, Field(examples=[0.5])]
    p_po4: Annotated[float, Field(examples=[0.5])]
    tss: Annotated[float, Field(examples=[0.5])]
    cod: Annotated[float, Field(examples=[0.5])]
    aeromonas_total: Annotated[float, Field(examples=[0.5])]
    actual_wqi: Annotated[float, Field(examples=[0.5])]
    predicted_wqi: Annotated[float, Field(examples=[0.5])]
    
class WaterQuality(WaterQualityBase):
    pass

class WaterQualityRead(WaterQualityBase):
    id: int