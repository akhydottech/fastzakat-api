from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.user import create_random_organization, create_random_user, authentication_token_from_email
from app.tests.utils.utils import random_email


def test_invite_user_to_organization(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Create user to invite
    user_to_invite = create_random_user(db)
    
    # Test successful invitation
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user_to_invite.email}
    )
    assert r.status_code == 200
    assert r.json() is True


def test_invite_nonexistent_user(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Test invitation with non-existent email
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": "nonexistent@example.com"}
    )
    assert r.status_code == 404


def test_invite_existing_member(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Create and invite user
    user_to_invite = create_random_user(db)
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user_to_invite.email}
    )
    assert r.status_code == 200
    
    # Try to invite the same user again
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user_to_invite.email}
    )
    assert r.status_code == 400


def test_get_members(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Create and invite a user
    user_to_invite = create_random_user(db)
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user_to_invite.email}
    )
    assert r.status_code == 200
    
    # Get members
    r = client.get(
        f"{settings.API_V1_STR}/organizations/members",
        headers=org_headers
    )
    assert r.status_code == 200
    response = r.json()
    assert response["count"] == 1
    assert len(response["data"]) == 1
    assert response["data"][0]["email"] == user_to_invite.email
    assert response["data"][0]["is_pending"] is True


def test_delete_member(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Create and invite a user
    user_to_invite = create_random_user(db)
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user_to_invite.email}
    )
    assert r.status_code == 200
    
    # Delete member
    r = client.delete(
        f"{settings.API_V1_STR}/organizations/members/{user_to_invite.id}",
        headers=org_headers
    )
    assert r.status_code == 200
    assert r.json() is True
    
    # Verify member is deleted
    r = client.get(
        f"{settings.API_V1_STR}/organizations/members",
        headers=org_headers
    )
    assert r.status_code == 200
    response = r.json()
    assert response["count"] == 0
    assert len(response["data"]) == 0


def test_delete_nonexistent_member(
    client: TestClient, db: Session
) -> None:
    # Create organization user
    org = create_random_organization(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Try to delete non-existent member with a valid UUID format
    nonexistent_uuid = "00000000-0000-0000-0000-000000000000"
    r = client.delete(
        f"{settings.API_V1_STR}/organizations/members/{nonexistent_uuid}",
        headers=org_headers
    )
    assert r.status_code == 404
