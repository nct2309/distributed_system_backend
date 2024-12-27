from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_rooms import crud_rooms, crud_room_features, crud_room_badges
from ...schemas.room import RoomCreate, RoomDelete, RoomRead, RoomReadExternal, RoomUpdate, RoomUpdateInternal, RoomFeatureBase, RoomBadgeBase, RoomFeatureDetail, RoomBadgeDetail

router = APIRouter(tags=["rooms"])

@router.post("/room", response_model=RoomRead, status_code=201)
async def write_room(
    request: Request, room: RoomCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RoomRead:
    name_row = await crud_rooms.exists(db=db, name=room.name)
    if name_row:
        raise DuplicateValueException("Room name is already registered")

    created_room: RoomRead = await crud_rooms.create(db=db, object=room)
    return created_room

@router.get("/rooms", response_model=PaginatedListResponse[RoomReadExternal])
async def read_rooms(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    rooms_data = await crud_rooms.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=RoomRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=rooms_data, page=page, items_per_page=items_per_page)
    for room in response["data"]:
        room_features = await crud_room_features.get_multi(
            db=db, schema_to_select=RoomFeatureDetail, id__in=room["feature_ids"]
        )
        room_badges = await crud_room_badges.get_multi(
            db=db, schema_to_select=RoomBadgeDetail, id__in=room["badge_ids"]
        )
        room["features"] = room_features["data"]
        room["badges"] = room_badges["data"]
    
    return response

@router.get("/room/{id}", response_model=RoomReadExternal)
async def read_room(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_room: RoomRead | None = await crud_rooms.get(
        db=db, schema_to_select=RoomRead, id=id, is_deleted=False
    )
    if db_room is None:
        raise NotFoundException("Room not found")

    # get room features and badges in the room.feature_ids and room.badge_ids
    room = dict(db_room)
    room_features = await crud_room_features.get_multi(
        db=db, schema_to_select=RoomFeatureDetail, id__in=db_room["feature_ids"]
    )
    room_badges = await crud_room_badges.get_multi(
        db=db, schema_to_select=RoomBadgeDetail, id__in=db_room["badge_ids"]
    )
    room["features"] = room_features["data"]
    room["badges"] = room_badges["data"]
    
    return room

@router.patch("/room/{id}")
async def patch_room(
    request: Request,
    values: RoomUpdate,
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_room = await crud_rooms.get(db=db, schema_to_select=RoomRead, id=id)
    if db_room is None:
        raise NotFoundException("Room not found")

    await crud_rooms.update(db=db, object=values, id=id)
    return {"message": "Room updated"}

@router.delete("/room/{id}")
async def erase_room(
    request: Request,
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_room = await crud_rooms.get(db=db, schema_to_select=RoomRead, id=id)
    if not db_room:
        raise NotFoundException("Room not found")

    await crud_rooms.delete(db=db, id=id)
    return {"message": "Room deleted"}

# add a new room feature:
@router.post("/room_feature", response_model=RoomFeatureDetail, status_code=201, tags=["room_features_and_badges"])
async def write_room_feature(
    request: Request,
    feature: RoomFeatureBase,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: dict = Depends(get_current_superuser),
) -> RoomFeatureDetail:
    db_feature = await crud_room_features.exists(db=db, name=feature.name)
    if db_feature:
        raise DuplicateValueException("Feature is already registered")

    created_feature: RoomFeatureDetail = await crud_room_features.create(db=db, object=feature)
    return created_feature

# edit a room feature
@router.patch("/room_feature/{id}", response_model=dict, tags=["room_features_and_badges"])
async def patch_room_feature(
    request: Request,
    values: RoomFeatureBase,
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: dict = Depends(get_current_superuser),
) -> dict[str, str]:
    db_feature = await crud_room_features.get(db=db, schema_to_select=RoomFeatureDetail, id=id)
    if db_feature is None:
        raise NotFoundException("Feature not found")

    await crud_room_features.update(db=db, object=values, id=id)
    return {"message": "Feature updated"}

# list of room features
@router.get("/room_features", response_model=dict, tags=["room_features_and_badges"])
async def read_room_features(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> list[RoomFeatureBase]:
    features: dict[str, Any] = await crud_room_features.get_multi(db=db, schema_to_select=RoomFeatureDetail, limit=None)
    return features

# add a new room badge
@router.post("/room_badge", response_model=RoomBadgeDetail, status_code=201, tags=["room_features_and_badges"])
async def write_room_badge(
    request: Request,
    badge: RoomBadgeBase,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: dict = Depends(get_current_superuser),
) -> RoomBadgeDetail:
    db_badge = await crud_room_badges.exists(db=db, name=badge.name)
    if db_badge:
        raise DuplicateValueException("Badge is already registered")

    created_badge: RoomBadgeDetail = await crud_room_badges.create(db=db, object=badge)
    return created_badge

# edit a room badge
@router.patch("/room_badge/{id}", response_model=dict, tags=["room_features_and_badges"])
async def patch_room_badge(
    request: Request,
    values: RoomBadgeBase,
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: dict = Depends(get_current_superuser),
) -> dict[str, str]:
    db_badge = await crud_room_badges.get(db=db, schema_to_select=RoomBadgeDetail, id=id)
    if db_badge is None:
        raise NotFoundException("Badge not found")

    await crud_room_badges.update(db=db, object=values, id=id)
    return {"message": "Badge updated"}

# list of room badges
@router.get("/room_badges", response_model=dict, tags=["room_features_and_badges"])
async def read_room_badges(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> list[RoomBadgeBase]:
    badges: dict[str, Any] = await crud_room_badges.get_multi(db=db, schema_to_select=RoomBadgeDetail, limit=None)
    return badges

# An API use to filter room in range of price and features and badges
@router.get("/rooms/filter", response_model=PaginatedListResponse[RoomReadExternal])
async def filter_rooms(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    min_price: int = 0,
    max_price: int = 200,
    # feature_ids: list[int] = [],
    # badge_ids: list[int] = [],
    feature_ids: list[int] = Query([]),
    badge_ids: list[int] = Query([]),
) -> dict:
    rooms_data = await crud_rooms.get_multi(
        db=db,
        limit=None,
        schema_to_select=RoomRead,
        is_deleted=False,
        price__gte=min_price,
        price__lte=max_price,
    )

    if feature_ids != []:
        rooms_data["data"] = [room for room in rooms_data["data"] if set(feature_ids).issubset(room["feature_ids"])]
    if badge_ids != []:
        rooms_data["data"] = [room for room in rooms_data["data"] if set(badge_ids).issubset(room["badge_ids"])]
    rooms_data["total_count"] = len(rooms_data["data"])
    if rooms_data["total_count"] > items_per_page:
        rooms_data["data"] = rooms_data["data"][compute_offset(page, items_per_page):compute_offset(page, items_per_page) + items_per_page]
    response: dict[str, Any] = paginated_response(crud_data=rooms_data, page=page, items_per_page=items_per_page)
    
    for room in response["data"]:
        room_features = await crud_room_features.get_multi(
            db=db, schema_to_select=RoomFeatureDetail, id__in=room["feature_ids"]
        )
        room_badges = await crud_room_badges.get_multi(
            db=db, schema_to_select=RoomBadgeDetail, id__in=room["badge_ids"]
        )
        room["features"] = room_features["data"]
        room["badges"] = room_badges["data"]
        
    return response