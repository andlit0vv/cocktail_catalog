import asyncio
import logging
from app.schemas.cocktail import Cocktail
from app.services.cocktaildb import cocktaildb_client

logger = logging.getLogger(__name__)

_cocktails: dict[str, Cocktail] = {}
_initialized: bool = False
_init_lock: asyncio.Lock | None = None


def _get_lock() -> asyncio.Lock:
    global _init_lock
    if _init_lock is None:
        _init_lock = asyncio.Lock()
    return _init_lock


async def initialize() -> None:
    global _initialized
    async with _get_lock():
        if _initialized:
            return
        await _load_all()
        _initialized = True


async def _load_all() -> None:
    global _cocktails
    semaphore = asyncio.Semaphore(5)
    letters = "abcdefghijklmnopqrstuvwxyz"

    async def fetch_letter(letter: str) -> list[Cocktail]:
        async with semaphore:
            try:
                results = await cocktaildb_client.search_by_letter(letter)
                logger.info(f"Letter '{letter}': {len(results)} cocktails")
                return results
            except Exception as exc:
                logger.warning(f"Letter '{letter}' failed: {exc}")
                return []

    tasks = [fetch_letter(letter) for letter in letters]
    all_results = await asyncio.gather(*tasks)

    for batch in all_results:
        for cocktail in batch:
            _cocktails[cocktail.id] = cocktail

    logger.info(f"Cache loaded: {len(_cocktails)} cocktails total")


async def get_all() -> list[Cocktail]:
    if not _initialized:
        await initialize()
    return list(_cocktails.values())


async def get_by_id(drink_id: str) -> Cocktail | None:
    if not _initialized:
        await initialize()
    return _cocktails.get(drink_id)


async def refresh() -> None:
    global _initialized, _cocktails
    _initialized = False
    _cocktails = {}
    await initialize()
