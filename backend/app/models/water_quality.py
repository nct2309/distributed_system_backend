import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Float, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base

class WaterQuality(Base):
    __tablename__ = 'water_quality'
    
    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True, init=False)
    time = mapped_column(DateTime)
    place = mapped_column(String)
    location = mapped_column(String)
    ph = mapped_column(Float)
    do = mapped_column(Float)
    conductivity = mapped_column(Float)
    n_no2 = mapped_column(Float)
    n_nh4 = mapped_column(Float)
    p_po4 = mapped_column(Float)
    tss = mapped_column(Float)
    cod = mapped_column(Float)
    aeromonas_total = mapped_column(Float)
    actual_wqi= mapped_column(Float)
    predicted_wqi= mapped_column(Float)
    
        # Define __init__ method to allow direct keyword arguments
    def __init__(self, time, place, location, ph=None, do=None, conductivity=None, n_no2=None,
                 n_nh4=None, p_po4=None, tss=None, cod=None, aeromonas_total=None, actual_wqi=None, predicted_wqi=None):
        self.time = time
        self.place = place
        self.location = location
        self.ph = ph
        self.do = do
        self.conductivity = conductivity
        self.n_no2 = n_no2
        self.n_nh4 = n_nh4
        self.p_po4 = p_po4
        self.tss = tss
        self.cod = cod
        self.aeromonas_total = aeromonas_total
        self.actual_wqi = actual_wqi
        self.predicted_wqi = predicted_wqi
        

