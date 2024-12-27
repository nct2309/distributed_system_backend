from fastcrud import FastCRUD

from ..models.room import Room, RoomFeature, RoomBadge
from ..schemas.room import RoomCreate, RoomDelete, RoomUpdate, RoomUpdateInternal, RoomFeatureDetail, RoomBadgeDetail, RoomFeatureBase, RoomBadgeBase

CRUDRoom = FastCRUD[Room, RoomCreate, RoomUpdate, RoomUpdateInternal, RoomDelete]
crud_rooms = CRUDRoom(Room)

CRUDRoomFeature = FastCRUD[RoomFeature, RoomFeatureBase, RoomFeatureBase, RoomFeatureBase, RoomFeatureDetail]
crud_room_features = CRUDRoomFeature(RoomFeature)

CRUDRoomBadge = FastCRUD[RoomBadge, RoomBadgeBase, RoomBadgeBase, RoomBadgeBase, RoomBadgeDetail]
crud_room_badges = CRUDRoomBadge(RoomBadge)