import logging
import httpx
from app.config import settings
from app.schemas.cocktail import Cocktail

logger = logging.getLogger(__name__)


class CocktailDBClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._client = httpx.AsyncClient(timeout=10.0)

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = self._base_url + endpoint
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def search_by_name(self, name: str) -> list[Cocktail]:
        data = await self._get("search.php", {"s": name})
        drinks = data.get("drinks") or []
        return [Cocktail.from_api(d) for d in drinks]

    async def search_by_letter(self, letter: str) -> list[Cocktail]:
        data = await self._get("search.php", {"f": letter})
        drinks = data.get("drinks") or []
        return [Cocktail.from_api(d) for d in drinks]

    async def lookup_by_id(self, drink_id: str) -> Cocktail | None:
        data = await self._get("lookup.php", {"i": drink_id})
        drinks = data.get("drinks") or []
        return Cocktail.from_api(drinks[0]) if drinks else None

    async def get_random(self) -> Cocktail:
        data = await self._get("random.php")
        drinks = data.get("drinks") or []
        return Cocktail.from_api(drinks[0])

    async def filter_by_category(self, category: str) -> list[dict]:
        data = await self._get("filter.php", {"c": category})
        return data.get("drinks") or []

    async def filter_by_ingredient(self, ingredient: str) -> list[dict]:
        data = await self._get("filter.php", {"i": ingredient})
        return data.get("drinks") or []

    async def filter_by_alcoholic(self, value: str) -> list[dict]:
        data = await self._get("filter.php", {"a": value})
        return data.get("drinks") or []

    async def filter_by_glass(self, glass: str) -> list[dict]:
        data = await self._get("filter.php", {"g": glass})
        return data.get("drinks") or []

    async def list_categories(self) -> list[str]:
        data = await self._get("list.php", {"c": "list"})
        drinks = data.get("drinks") or []
        return [d["strCategory"] for d in drinks]

    async def list_ingredients(self) -> list[str]:
        data = await self._get("list.php", {"i": "list"})
        drinks = data.get("drinks") or []
        return [d["strIngredient1"] for d in drinks]

    async def list_alcoholic_types(self) -> list[str]:
        data = await self._get("list.php", {"a": "list"})
        drinks = data.get("drinks") or []
        return [d["strAlcoholic"] for d in drinks]

    async def list_glasses(self) -> list[str]:
        data = await self._get("list.php", {"g": "list"})
        drinks = data.get("drinks") or []
        return [d["strGlass"] for d in drinks]

    async def close(self) -> None:
        await self._client.aclose()


cocktaildb_client = CocktailDBClient(settings.cocktaildb_base_url)
