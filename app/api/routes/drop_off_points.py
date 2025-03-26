import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import DropOffPoint, DropOffPointCreate, DropOffPointPublic, DropOffPointsPublic, DropOffPointUpdate, Message
from app.utils import address_search
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drop-off-points", tags=["drop-off-points"])


@router.get("/", response_model=DropOffPointsPublic)
def read_drop_off_points(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100, use_pagination: bool = True
) -> Any:
    """
    Retrieve drop off points.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(DropOffPoint)
        count = session.exec(count_statement).one()
        statement = select(DropOffPoint).offset(skip).limit(limit)
        drop_off_points = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(DropOffPoint)
            .where(DropOffPoint.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(DropOffPoint)
            .where(DropOffPoint.owner_id == current_user.id)
        )
        if use_pagination:
            statement = statement.offset(skip).limit(limit)
        drop_off_points = session.exec(statement).all()

    # Convert to DropOffPointPublic with owner_full_name
    public_drop_off_points = []
    for drop_off_point in drop_off_points:
        public_point = DropOffPointPublic(
            id=drop_off_point.id,
            title=drop_off_point.title,
            description=drop_off_point.description,
            address=drop_off_point.address,
            owner_id=drop_off_point.owner_id,
            owner_full_name=drop_off_point.owner.full_name if drop_off_point.owner else None,
            latitude=drop_off_point.latitude,
            longitude=drop_off_point.longitude
        )
        public_drop_off_points.append(public_point)

    return DropOffPointsPublic(data=public_drop_off_points, count=count)


@router.get("/{id}", response_model=DropOffPointPublic)
def read_drop_off_point(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get drop off point by ID.
    """
    drop_off_point = session.get(DropOffPoint, id)
    if not drop_off_point:
        raise HTTPException(status_code=404, detail="Drop off point not found")
    if not current_user.is_superuser and (drop_off_point.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return DropOffPointPublic(
        id=drop_off_point.id,
        title=drop_off_point.title,
        description=drop_off_point.description,
        address=drop_off_point.address,
        owner_id=drop_off_point.owner_id,
        owner_full_name=drop_off_point.owner.full_name if drop_off_point.owner else None,
        latitude=drop_off_point.latitude,
        longitude=drop_off_point.longitude
    )


@router.post("/", response_model=DropOffPointPublic)
def create_drop_off_point(
    *, session: SessionDep, current_user: CurrentUser, drop_off_point_in: DropOffPointCreate
) -> Any:
    """
    Create new drop off point.
    """
    longitude, latitude = None, None
    try:
        if drop_off_point_in.address:
            coordinates = address_search(drop_off_point_in.address).features[0].geometry.coordinates
            longitude, latitude = coordinates
            drop_off_point_in.longitude = longitude
            drop_off_point_in.latitude = latitude
        else:
            drop_off_point_in.longitude = None
            drop_off_point_in.latitude = None
            
    except Exception as e:
        logger.error(f"Error creating drop off point: {e}")

    drop_off_point = DropOffPoint.model_validate(drop_off_point_in, update={"owner_id": current_user.id})
    session.add(drop_off_point)
    session.commit()
    session.refresh(drop_off_point)
    return DropOffPointPublic(
        id=drop_off_point.id,
        title=drop_off_point.title,
        description=drop_off_point.description,
        address=drop_off_point.address,
        owner_id=drop_off_point.owner_id,
        owner_full_name=current_user.full_name,
        latitude=drop_off_point.latitude,
        longitude=drop_off_point.longitude
    )


@router.put("/{id}", response_model=DropOffPointPublic)
def update_drop_off_point(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    drop_off_point_in: DropOffPointUpdate,
) -> Any:
    """
    Update a drop off point.
    """
    drop_off_point = session.get(DropOffPoint, id)
    if not drop_off_point:
        raise HTTPException(status_code=404, detail="Drop off point not found")
    if not current_user.is_superuser and (drop_off_point.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = drop_off_point_in.model_dump(exclude_unset=True)
    longitude, latitude = None, None
    try:
        if drop_off_point.address:
            address_search_result = address_search(drop_off_point_in.address).features[0]
            coordinates = address_search_result.geometry.coordinates
            longitude, latitude = coordinates
            update_dict["latitude"] = latitude
            update_dict["longitude"] = longitude
        else:
            update_dict["latitude"] = None
            update_dict["longitude"] = None
    except Exception as e:
        logger.error(f"Error updating drop off point: {e}")

    drop_off_point.sqlmodel_update(update_dict)
    session.add(drop_off_point)
    session.commit()
    session.refresh(drop_off_point)
    return DropOffPointPublic(
        id=drop_off_point.id,
        title=drop_off_point.title,
        description=drop_off_point.description,
        address=drop_off_point.address,
        owner_id=drop_off_point.owner_id,
        owner_full_name=drop_off_point.owner.full_name if drop_off_point.owner else None,
        latitude=drop_off_point.latitude,
        longitude=drop_off_point.longitude
    )


@router.delete("/{id}")
def delete_drop_off_point(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a drop off point.
    """
    drop_off_point = session.get(DropOffPoint, id)
    if not drop_off_point:
        raise HTTPException(status_code=404, detail="Drop off point not found")
    if not current_user.is_superuser and (drop_off_point.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(drop_off_point)
    session.commit()
    return Message(message="Drop off point deleted successfully")
