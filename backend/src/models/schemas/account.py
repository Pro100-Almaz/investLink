from datetime import datetime
from typing import Optional

import pydantic

from src.models.schemas.base import BaseSchemaModel


class AccountInCreate(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str


class AccountInUpdate(BaseSchemaModel):
    username: str | None
    email: str | None
    password: str | None


class AccountInLogin(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str


class AccountWithToken(BaseSchemaModel):
    token: str
    username: str
    email: str
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    is_logged_in: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AccountInResponse(BaseSchemaModel):
    id: int
    authorizedAccount: AccountWithToken
