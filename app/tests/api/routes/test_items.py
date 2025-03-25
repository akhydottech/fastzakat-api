import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.drop_off_point import create_random_drop_off_point


def test_create_drop_off_point(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/drop-off-points/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_drop_off_point(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    response = client.get(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == drop_off_point.title
    assert content["description"] == drop_off_point.description
    assert content["id"] == str(drop_off_point.id)
    assert content["owner_id"] == str(drop_off_point.owner_id)


def test_read_drop_off_point_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/drop-off-points/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Drop off point not found"


def test_read_drop_off_point_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    response = client.get(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_drop_off_points(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_drop_off_point(db)
    create_random_drop_off_point(db)
    response = client.get(
        f"{settings.API_V1_STR}/drop-off-points/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_drop_off_point(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(drop_off_point.id)
    assert content["owner_id"] == str(drop_off_point.owner_id)


def test_update_drop_off_point_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/drop-off-points/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Drop off point not found"


def test_update_drop_off_point_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_drop_off_point(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    response = client.delete(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Drop off point deleted successfully"


def test_delete_drop_off_point_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/drop-off-points/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Drop off point not found"


def test_delete_drop_off_point_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    drop_off_point = create_random_drop_off_point(db)
    response = client.delete(
        f"{settings.API_V1_STR}/drop-off-points/{drop_off_point.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
