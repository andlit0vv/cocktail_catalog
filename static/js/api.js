const CocktailAPI = (() => {
  async function request(path, options = {}) {
    const res = await fetch(path, { credentials: "include", ...options });
    if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
    if (res.status === 204) return null;
    return res.json();
  }

  async function requestRaw(path, options = {}) {
    return fetch(path, { credentials: "include", ...options });
  }

  return {
    getAll:            () => request("/api/cocktails"),
    getById:           (id) => request(`/api/cocktails/${id}`),
    getRandom:         () => request("/api/cocktails/random"),
    getCategories:     () => request("/api/filters/categories"),
    getIngredients:    () => request("/api/filters/ingredients"),
    getGlasses:        () => request("/api/filters/glasses"),
    getAlcoholicTypes: () => request("/api/filters/alcoholic"),

    getMe:             () => requestRaw("/auth/me"),
    logout:            () => request("/auth/logout", { method: "POST" }),

    getFavoritesIds:   () => request("/api/favorites/ids"),
    getFavorites:      () => request("/api/favorites"),
    addFavorite:       (cocktailId) => request("/api/favorites", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cocktail_id: cocktailId }),
    }),
    removeFavorite:    (cocktailId) => requestRaw(`/api/favorites/${cocktailId}`, {
      method: "DELETE",
    }),
  };
})();
