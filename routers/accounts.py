import common.config as config

from tortoise import fields, models
from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Response,
    Request,
    Depends,
)
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from jose import jwt, JWTError
import httpx

import time
from urllib.parse import urlencode
import secrets
import random
import os
import re
from datetime import datetime, timedelta
from typing import Any, Annotated


router = APIRouter(tags=["accounts"])


class Account(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=254, unique=True, null=True)

    google_id = fields.TextField(null=True)

    created_at = fields.IntField() # unix timestamp
    updated_at = fields.IntField() # unix timestamp

    async def update(self):
        self.updated_at = int(time.time())
        return await self.save()


class AccountResponse(BaseModel):
    id: int
    email: str
    google_id: str
    created_at: int
    updated_at: int

    @classmethod
    async def create(cls, account: Account):
        return cls(
            id=account.id,
            email=account.email,
            google_id=account.google_id,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
    

def check_email(email: str):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email.")


def encode_token(
    data: dict[str, Any],
    expire_minutes: int = 60,
) -> str:

    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

    to_encode: dict = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=os.environ["JWT_SECRET"],
        algorithm="HS256"
    )

    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token=token,
            key=os.environ["JWT_SECRET"],
            algorithms="HS256"
        )
        return payload
    except JWTError as e:
        print(e)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return HTTPException(status.HTTP_400_BAD_REQUEST)


class Token(BaseModel):
    account_id: int
    scopes: list[str]


def create_token(account: Account) -> str:
    scopes = []

    return encode_token({
        "sub": str(account.id),
        "scopes": " ".join(scopes),
    })


def _login(
    response: Response,
    account: Account
):
    token = create_token(account)

    response.set_cookie(
        key="token",
        value=token,
        max_age=400 * 24 * 3600, # 400 days
        httponly=True,
        samesite="none",
        secure=True,
    )


async def _register(
    email: str = None,
    google_id: str = None,
):
    account = Account()

    if email is not None:
        check_email(email)

        if await Account.get_or_none(email=email.lower()) is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already used.")
        
        account.email = email

    if google_id is not None:
        account.google_id = google_id

    account.created_at = int(time.time())
    account.updated_at = int(time.time())
    await account.save()

    return account


@router.get("/google")
async def google_login():

    state = secrets.token_urlsafe(32)

    uri = urlencode({
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "state": state,
        "nonce": random.randint(0, 2**32),
    })

    response = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{uri}")

    response.set_cookie(
        key="state",
        value=state,
        max_age=60 * 10, # 10 minutes
        httponly=True,
        samesite="none",
        secure=True,
    )

    return response


@router.get("/google/callback")
async def google_callback(
    request: Request, 
    code: str, 
    state: str
):
    if state != request.cookies.get("state"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid state.")

    # exchange code for token
    uri = urlencode({
        "code": code,
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    })

    async with httpx.AsyncClient() as client:
        r = await client.post(f"https://oauth2.googleapis.com/token?{uri}")

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid code.")
    
    data = r.json()
    token = jwt.decode(
        data["id_token"], 
        key=None,
        algorithms="HS256",
        options={
            "verify_signature": False, 
            "verify_aud": False,
            "verify_at_hash": False,
        }
    )

    account = await Account.get_or_none(google_id=token["sub"])

    if account is None:
        account = await _register(
            email=token["email"], 
            google_id=token["sub"]
        )

    response = RedirectResponse(config.LOGIN_REDIRECT_URI)
    
    _login(response, account)

    return response


@router.get("/logout")
async def logout(response: Response):
    try:
        response = RedirectResponse(
            config.LOGOUT_REDIRECT_URI, 
            status_code=302
        )
        response.delete_cookie(
            key="token",
            samesite="none",
            secure=True,
        )
    except: 
        pass

    return response


def require_token(request: Request) -> Token:
    plain = request.cookies.get("token")

    if plain is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    payload = verify_token(plain)

    scopes = payload["scopes"].split(" ")

    return Token(
        account_id=payload["sub"],
        scopes=scopes,
    )


async def require_account(
    token: Annotated[Token, Depends(require_token)],
) -> Account:
    
    id = int(token.account_id)
    account = await Account.get_or_none(id=id)

    if account is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return account


@router.get("/me")
async def get_me(
    account: Annotated[Account, Depends(require_account)],
):
    return await AccountResponse.create(account)
