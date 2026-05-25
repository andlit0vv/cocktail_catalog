const Favorites = (() => {
  const KEY = "favorites";
  let _set = new Set();

  async function load() {
    let ids;
    if (Auth.isLoggedIn()) {
      ids = await CocktailAPI.getFavoritesIds();
    } else {
      try {
        ids = JSON.parse(localStorage.getItem(KEY) || "[]");
      } catch {
        ids = [];
      }
    }
    _set = new Set(ids);
  }

  async function toggle(id) {
    if (_set.has(id)) {
      await remove(id);
      return false;
    } else {
      await add(id);
      return true;
    }
  }

  async function add(id) {
    if (Auth.isLoggedIn()) {
      await CocktailAPI.addFavorite(id);
    } else {
      _saveToLocal(_set);
    }
    _set.add(id);
    if (!Auth.isLoggedIn()) _saveToLocal(_set);
  }

  async function remove(id) {
    if (Auth.isLoggedIn()) {
      await CocktailAPI.removeFavorite(id);
    }
    _set.delete(id);
    if (!Auth.isLoggedIn()) _saveToLocal(_set);
  }

  function _saveToLocal(set) {
    try {
      localStorage.setItem(KEY, JSON.stringify([...set]));
    } catch (e) {
      console.error("Favorites save error", e);
    }
  }

  function isFavorite(id) {
    return _set.has(id);
  }

  async function migrateLocalToServer() {
    let localIds;
    try {
      localIds = JSON.parse(localStorage.getItem(KEY) || "[]");
    } catch {
      localIds = [];
    }
    if (localIds.length === 0) return;

    for (const id of localIds) {
      try {
        await CocktailAPI.addFavorite(id);
      } catch {}
    }
    localStorage.removeItem(KEY);
    await load();
  }

  return { load, toggle, add, remove, isFavorite, migrateLocalToServer };
})();
