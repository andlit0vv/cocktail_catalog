from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.config import settings


def create_token(user_id: int) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=settings.jwt_expire_days),
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (ExpiredSignatureError, JWTError, ValueError):
        return None
