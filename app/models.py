from typing import List, Optional
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    is_organization: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    is_organization: bool | None = Field(default=None)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    dropOffPoints: list["DropOffPoint"] = Relationship(back_populates="owner", cascade_delete=True)
    organization_memberships: list["MemberOf"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MemberOf.organization_id]", "cascade": "all, delete-orphan"},
        back_populates="organization",
    )
    member_of_organizations: list["MemberOf"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MemberOf.member_id]", "cascade": "all, delete-orphan"},
        back_populates="member"
    )

class MemberOfBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="user.id")
    member_id: uuid.UUID = Field(foreign_key="user.id")
    is_pending: bool = Field(default=True)


class MemberOf(MemberOfBase, table=True):
    organization: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MemberOf.organization_id]"},
        back_populates="organization_memberships"
    )
    member: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MemberOf.member_id]"},
        back_populates="member_of_organizations"
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class MemberInfo(UserPublic):
    is_pending: bool


class MembersResponse(SQLModel):
    data: list[MemberInfo]
    count: int

class InvitationsResponse(SQLModel):
    data: list[MemberOf]
    count: int

class OrganizationMembershipResponse(SQLModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    member_id: uuid.UUID
    is_pending: bool
    organization_name: str | None = None

class OrganizationMembershipsResponse(SQLModel):
    data: list[OrganizationMembershipResponse]
    count: int


# Shared properties
class DropOffPointBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)
    address: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)


# Properties to receive on drop off point creation
class DropOffPointCreate(DropOffPointBase):
    pass


# Properties to receive on drop off point update
class DropOffPointUpdate(DropOffPointBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class DropOffPoint(DropOffPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="dropOffPoints")
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)


# Properties to return via API, id is always required
class DropOffPointPublic(DropOffPointBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_full_name: str | None = None


class DropOffPointsPublic(SQLModel):
    data: list[DropOffPointPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# Address model

class AddressProperties(SQLModel):
    label: Optional[str] = None
    score: Optional[float] = None
    id: Optional[str] = None
    name: Optional[str] = None
    postcode: Optional[str] = None
    citycode: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    city: Optional[str] = None
    context: Optional[str] = None
    type: Optional[str] = None
    importance: Optional[float] = None
    banId: Optional[str] = None
    oldcitycode: Optional[str] = None
    oldcity: Optional[str] = None

class AddressGeometry(SQLModel):
    type: Optional[str] = None
    coordinates: List[float]

class AddressFeature(SQLModel):
    type: Optional[str] = None
    geometry: Optional[AddressGeometry] = None
    properties: Optional[AddressProperties] = None

class AddressResponse(SQLModel):
    type: Optional[str] = None
    version: Optional[str] = None
    features: Optional[List[AddressFeature]] = None
    attribution: Optional[str] = None
    licence: Optional[str] = None
    query: Optional[str] = None
    limit: Optional[int] = None