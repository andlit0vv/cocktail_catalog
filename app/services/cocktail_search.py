import re
from app.schemas.cocktail import Cocktail
from app.services import cache

RU_TO_EN: dict[str, str] = {
    "водка": "vodka",
    "ром": "rum",
    "джин": "gin",
    "текила": "tequila",
    "виски": "whiskey",
    "бурбон": "bourbon",
    "коньяк": "cognac",
    "бренди": "brandy",
    "ликёр": "liqueur",
    "ликер": "liqueur",
    "шампанское": "champagne",
    "вино": "wine",
    "пиво": "beer",
    "лимон": "lemon",
    "лайм": "lime",
    "апельсин": "orange",
    "грейпфрут": "grapefruit",
    "клубника": "strawberry",
    "малина": "raspberry",
    "мята": "mint",
    "имбирь": "ginger",
    "сахар": "sugar",
    "мёд": "honey",
    "мед": "honey",
    "молоко": "milk",
    "сливки": "cream",
    "кофе": "coffee",
    "шоколад": "chocolate",
    "кокос": "coconut",
    "ананас": "pineapple",
    "арбуз": "watermelon",
    "персик": "peach",
    "манго": "mango",
    "абрикос": "apricot",
    "вишня": "cherry",
    "гранат": "grenadine",
    "гренадин": "grenadine",
    "томат": "tomato",
    "огурец": "cucumber",
    "сельдерей": "celery",
    "табаско": "tabasco",
    "вустер": "worcestershire",
    "лёд": "ice",
    "лед": "ice",
    "содовая": "soda",
    "тоник": "tonic",
    "кола": "cola",
}


def _translate_text(text: str) -> str:
    lower = text.lower()
    for ru, en in RU_TO_EN.items():
        lower = re.sub(r'\b' + re.escape(ru) + r'\b', en, lower)
    return lower


async def extract_ingredients_from_text(text: str) -> list[str]:
    all_cocktails = await cache.get_all()
    known: set[str] = set()
    for c in all_cocktails:
        for ing in c.ingredients:
            known.add(ing.name.lower())

    translated = _translate_text(text)
    found: list[str] = []
    for ingredient in sorted(known, key=len, reverse=True):
        pattern = r'\b' + re.escape(ingredient) + r'\b'
        if re.search(pattern, translated, re.IGNORECASE):
            found.append(ingredient)
    return found


async def find_by_ingredients(ingredients: list[str], limit: int = 10) -> list[Cocktail]:
    if not ingredients:
        return []
    all_cocktails = await cache.get_all()
    scored: list[tuple[int, Cocktail]] = []
    for cocktail in all_cocktails:
        cocktail_ings = {ing.name.lower() for ing in cocktail.ingredients}
        score = sum(1 for ing in ingredients if ing.lower() in cocktail_ings)
        if score > 0:
            scored.append((score, cocktail))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:limit]]


async def find_by_name(name: str, limit: int = 5) -> list[Cocktail]:
    all_cocktails = await cache.get_all()
    lower = name.lower()
    return [c for c in all_cocktails if lower in c.name.lower()][:limit]


def format_cocktails_for_prompt(cocktails: list[Cocktail]) -> str:
    lines: list[str] = []
    for c in cocktails:
        ings = ", ".join(
            f"{ing.name} {ing.measure}".strip() for ing in c.ingredients
        )
        instructions = (c.instructions or "")[:200]
        if len(c.instructions or "") > 200:
            instructions += "..."
        lines.append(
            f"- {c.name} ({c.alcoholic or '?'}, {c.glass or '?'})\n"
            f"  Ингредиенты: {ings}\n"
            f"  Инструкция: {instructions}"
        )
    return "\n".join(lines)
