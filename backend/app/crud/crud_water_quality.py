from fastcrud import FastCRUD

from ..models.water_quality import WaterQuality
from ..schemas.water_quality import WaterQualityRead

# CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdateInternal, UserDelete]
# crud_users = CRUDUser(User)

# Read only from warehouse
CRUDWaterQuality = FastCRUD[WaterQuality, None, None, None, None]
crud_water_quality = CRUDWaterQuality(WaterQuality)