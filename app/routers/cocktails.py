from fastapi import APIRouter, HTTPException
from app.schemas.cocktail import Cocktail
from app.services import cache
from app.services.cocktaildb import cocktaildb_client

router = APIRouter(prefix="/api")


@router.get("/cocktails/random", response_model=Cocktail)
async def get_random():
    return await cocktaildb_client.get_random()


@router.get("/cocktails/{cocktail_id}", response_model=Cocktail)
async def get_by_id(cocktail_id: str):
    cocktail = await cache.get_by_id(cocktail_id)
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    return cocktail


@router.get("/cocktails", response_model=list[Cocktail])
async def get_all():
    return await cache.get_all()


@router.get("/filters/categories", response_model=list[str])
async def get_categories():
    return await cocktaildb_client.list_categories()


@router.get("/filters/ingredients", response_model=list[str])
async def get_ingredients():
    return await cocktaildb_client.list_ingredients()


@router.get("/filters/glasses", response_model=list[str])
async def get_glasses():
    return await cocktaildb_client.list_glasses()


@router.get("/filters/alcoholic", response_model=list[str])
async def get_alcoholic_types():
    return await cocktaildb_client.list_alcoholic_types()
