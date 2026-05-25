import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.base_client import OAuthError
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserPublic
from app.services.oauth import oauth
from app.services import jwt_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/login")
async def login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        logger.error("OAuthError: %s", e)
        return RedirectResponse(url="/?auth_error=1", status_code=302)

    userinfo = token.get("userinfo")
    if not userinfo:
        try:
            userinfo = await oauth.google.parse_id_token(request, token)
        except Exception as e:
            logger.error("parse_id_token error: %s", e)
            return RedirectResponse(url="/?auth_error=1", status_code=302)

    google_sub = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("name", email)
    picture_url = userinfo.get("picture")

    user = await UserRepository(db).upsert_from_google(google_sub, email, name, picture_url)
    access_token = jwt_service.create_token(user.id)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.jwt_expire_days * 86400,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me", response_model=UserPublic)
async def me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)
