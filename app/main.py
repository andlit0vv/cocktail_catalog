import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routers import cocktails, pages
from app.routers import auth, favorites, assistant
from app.services import cache
from app.services.cocktaildb import cocktaildb_client
from app.config import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.initialize()
    yield
    await cocktaildb_client.close()


app = FastAPI(title="Cocktail Catalog", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router)
app.include_router(cocktails.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["assistant"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=settings.app_debug)
