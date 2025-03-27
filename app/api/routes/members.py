from typing import Any
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import (
    CurrentUser,
    SessionDep,
)
from app.models import MemberOf, OrganizationMembershipsResponse, OrganizationMembershipResponse

router = APIRouter(prefix="/members", tags=["members"])

# As Member
@router.get("/organizations", response_model=OrganizationMembershipsResponse)
def get_organizations(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Get all organizations the current user is a member of.
    """
    organizations = session.exec(
        select(MemberOf).where(
            MemberOf.member_id == current_user.id,
        )
    ).all()
    
    response_data = []
    for membership in organizations:
        membership = membership[0]
        response_data.append(
            OrganizationMembershipResponse(
                id=membership.id,
                organization_id=membership.organization_id,
                email=membership.organization.email,
                member_id=membership.member_id,
                is_pending=membership.is_pending,
                organization_name=membership.organization.full_name
            )
        )
    
    return OrganizationMembershipsResponse(data=response_data, count=len(response_data))

@router.post("/invitations/{invitation_id}/accept", response_model=bool)
def accept_invitation(
    invitation_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Accept an invitation to join an organization.
    """
    invitation = session.exec(
        select(MemberOf).where(
            MemberOf.id == invitation_id,
            MemberOf.member_id == current_user.id,
            MemberOf.is_pending == True
        )
    ).first()
    print(invitation)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    invitation = invitation[0]
    invitation.is_pending = False
    session.commit()
    session.refresh(invitation)

    return True

@router.delete("/{member_id}", response_model=bool)
def delete_organization(
    member_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete a member from an organization.
    """
    member = session.exec(
        select(MemberOf).where(
            MemberOf.id == member_id,
            MemberOf.member_id == current_user.id
        )
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member = member[0]
    session.delete(member)
    session.commit()
    return True