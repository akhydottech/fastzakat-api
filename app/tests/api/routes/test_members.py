from fastapi.testclient import TestClient
from sqlmodel import Session
import uuid

from app.core.config import settings
from app.tests.utils.user import create_random_organization, create_random_user, authentication_token_from_email
from app.tests.utils.utils import random_email


def test_get_organizations(
    client: TestClient, db: Session
) -> None:
    # Create organization
    org = create_random_organization(db)
    
    # Create user and add them to organization
    user = create_random_user(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Invite user to organization
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user.email}
    )
    assert r.status_code == 200
    
    # Get user's organizations
    user_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    r = client.get(
        f"{settings.API_V1_STR}/members/organizations",
        headers=user_headers
    )
    assert r.status_code == 200
    response = r.json()
    assert response["count"] == 1
    assert len(response["data"]) == 1
    assert response["data"][0]["organization_id"] == str(org.id)
    assert response["data"][0]["is_pending"] is True


def test_accept_invitation(
    client: TestClient, db: Session
) -> None:
    # Create organization
    org = create_random_organization(db)
    
    # Create user and add them to organization
    user = create_random_user(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Invite user to organization
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user.email}
    )
    assert r.status_code == 200
    
    # Get invitation ID
    user_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    r = client.get(
        f"{settings.API_V1_STR}/members/organizations",
        headers=user_headers
    )
    invitation_id = r.json()["data"][0]["id"]
    
    # Accept invitation
    r = client.post(
        f"{settings.API_V1_STR}/members/invitations/{invitation_id}/accept",
        headers=user_headers
    )
    assert r.status_code == 200
    assert r.json() is True
    
    # Verify invitation is accepted
    r = client.get(
        f"{settings.API_V1_STR}/members/organizations",
        headers=user_headers
    )
    assert r.status_code == 200
    response = r.json()
    assert response["data"][0]["is_pending"] is False


def test_accept_nonexistent_invitation(
    client: TestClient, db: Session
) -> None:
    # Create user
    user = create_random_user(db)
    user_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    
    # Try to accept non-existent invitation
    nonexistent_uuid = uuid.uuid4()
    r = client.post(
        f"{settings.API_V1_STR}/members/invitations/{nonexistent_uuid}/accept",
        headers=user_headers
    )
    assert r.status_code == 404


def test_delete_organization_membership(
    client: TestClient, db: Session
) -> None:
    # Create organization
    org = create_random_organization(db)
    
    # Create user and add them to organization
    user = create_random_user(db)
    org_headers = authentication_token_from_email(
        client=client, email=org.email, db=db
    )
    
    # Invite user to organization
    r = client.post(
        f"{settings.API_V1_STR}/organizations/invite",
        headers=org_headers,
        params={"email": user.email}
    )
    assert r.status_code == 200
    
    # Get membership ID
    user_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    r = client.get(
        f"{settings.API_V1_STR}/members/organizations",
        headers=user_headers
    )
    membership_id = r.json()["data"][0]["id"]
    
    # Delete membership
    r = client.delete(
        f"{settings.API_V1_STR}/members/{membership_id}",
        headers=user_headers
    )
    assert r.status_code == 200
    assert r.json() is True
    
    # Verify membership is deleted
    r = client.get(
        f"{settings.API_V1_STR}/members/organizations",
        headers=user_headers
    )
    assert r.status_code == 200
    response = r.json()
    assert response["count"] == 0
    assert len(response["data"]) == 0


def test_delete_nonexistent_membership(
    client: TestClient, db: Session
) -> None:
    # Create user
    user = create_random_user(db)
    user_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    
    # Try to delete non-existent membership
    nonexistent_uuid = uuid.uuid4()
    r = client.delete(
        f"{settings.API_V1_STR}/members/{nonexistent_uuid}",
        headers=user_headers
    )
    assert r.status_code == 404
