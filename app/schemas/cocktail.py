from __future__ import annotations
from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    measure: str | None = None


class Cocktail(BaseModel):
    id: str
    name: str
    category: str | None = None
    alcoholic: str | None = None
    glass: str | None = None
    instructions: str | None = None
    image_url: str | None = None
    ingredients: list[Ingredient] = []
    tags: list[str] = []

    @classmethod
    def from_api(cls, raw: dict) -> "Cocktail":
        ingredients = []
        for i in range(1, 16):
            name = raw.get(f"strIngredient{i}")
            if not name or not name.strip():
                continue
            measure = raw.get(f"strMeasure{i}")
            ingredients.append(
                Ingredient(
                    name=name.strip(),
                    measure=measure.strip() if measure else None,
                )
            )

        raw_tags = raw.get("strTags") or ""
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

        return cls(
            id=raw.get("idDrink", ""),
            name=raw.get("strDrink", ""),
            category=raw.get("strCategory"),
            alcoholic=raw.get("strAlcoholic"),
            glass=raw.get("strGlass"),
            instructions=raw.get("strInstructions"),
            image_url=raw.get("strDrinkThumb"),
            ingredients=ingredients,
            tags=tags,
        )
