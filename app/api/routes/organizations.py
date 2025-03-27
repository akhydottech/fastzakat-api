from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_organization,
)
from app.models import MemberOf, MembersResponse, MemberInfo

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/invite", dependencies=[Depends(get_current_active_organization)],  response_model=bool)
def invite_user_to_organization(
    email: str,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Send an invitation to a user to join the organization.
    """
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    is_existing_member = session.exec(
        select(MemberOf).where(
            MemberOf.organization_id == current_user.id,
            MemberOf.member_id == user.id
        )
    ).first()
    
    if is_existing_member:
        raise HTTPException(status_code=400, detail="User already a member of the organization")

    member_of = MemberOf(organization_id=current_user.id, member_id=user.id, is_pending=True)
    session.add(member_of)
    session.commit()
    session.refresh(member_of)

    return True

@router.get("/members", dependencies=[Depends(get_current_active_organization)], response_model=MembersResponse)
def get_members(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Get all members of the current organization.
    """
    memberships = session.exec(
        select(MemberOf)
        .options(joinedload(MemberOf.member))
        .where(MemberOf.organization_id == current_user.id)
    ).all()
    

    member_infos = []
    for membership in memberships:
        membership = membership[0]
        member_infos.append(
            MemberInfo(
                id=membership.member.id,
                email=membership.member.email,
                is_active=membership.member.is_active,
                is_superuser=membership.member.is_superuser,
                is_organization=membership.member.is_organization,
                full_name=membership.member.full_name,
                is_pending=membership.is_pending
            )
        )
    return MembersResponse(data=member_infos, count=len(member_infos))

@router.delete("/members/{member_id}", dependencies=[Depends(get_current_active_organization)], response_model=bool)
def delete_member(
    member_id: str,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete a member from the current organization.
    """
    member = session.exec(
        select(MemberOf).where(
            MemberOf.organization_id == current_user.id,
            MemberOf.member_id == member_id
        )
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    session.delete(member[0])
    session.commit()
    return True
