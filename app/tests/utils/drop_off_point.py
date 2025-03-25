from sqlmodel import Session

from app import crud
from app.models import DropOffPoint, DropOffPointCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_drop_off_point(db: Session) -> DropOffPoint:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    drop_off_point_in = DropOffPointCreate(title=title, description=description)
    return crud.create_drop_off_point(session=db, drop_off_point_in=drop_off_point_in, owner_id=owner_id)
