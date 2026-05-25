from authlib.integrations.starlette_client import OAuth
from app.config import settings

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    # Прямые URL вместо server_metadata_url — убирает сетевой запрос на /.well-known/
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={"scope": "openid email profile"},
)
