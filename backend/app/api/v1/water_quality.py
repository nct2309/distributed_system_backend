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
@router.get("/{id}", response_model=WaterQualityRead)
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