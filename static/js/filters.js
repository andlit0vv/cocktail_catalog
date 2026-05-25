const Filters = (() => {
  function getState() {
    return {
      search:   document.getElementById("search-input").value.trim().toLowerCase(),
      category: document.getElementById("filter-category").value,
      alcoholic:document.getElementById("filter-alcoholic").value,
      glass:    document.getElementById("filter-glass").value,
    };
  }

  function apply(cocktails, state) {
    return cocktails.filter((c) => {
      if (state.search && !c.name.toLowerCase().includes(state.search)) return false;
      if (state.category && c.category !== state.category) return false;
      if (state.alcoholic && c.alcoholic !== state.alcoholic) return false;
      if (state.glass && c.glass !== state.glass) return false;
      return true;
    });
  }

  function attach() {
    const inputs = ["search-input", "filter-category", "filter-alcoholic", "filter-glass"];
    inputs.forEach((id) => {
      document.getElementById(id).addEventListener("input", _onFilterChange);
      document.getElementById(id).addEventListener("change", _onFilterChange);
    });
    document.getElementById("btn-reset").addEventListener("click", reset);
  }

  function _onFilterChange() {
    const filtered = apply(window.allCocktails || [], getState());
    Cards.renderCards(filtered);
  }

  async function populateDropdowns() {
    try {
      const [cats, glasses, alcoholics] = await Promise.all([
        CocktailAPI.getCategories(),
        CocktailAPI.getGlasses(),
        CocktailAPI.getAlcoholicTypes(),
      ]);
      _fill("filter-category",  cats,      "Все категории");
      _fill("filter-glass",     glasses,   "Все стаканы");
      _fill("filter-alcoholic", alcoholics,"Алкогольность");
    } catch (e) {
      console.error("populateDropdowns error", e);
    }
  }

  function _fill(selectId, items, placeholder) {
    const sel = document.getElementById(selectId);
    sel.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item;
      opt.textContent = item;
      sel.appendChild(opt);
    });
  }

  function reset() {
    document.getElementById("search-input").value = "";
    document.getElementById("filter-category").value = "";
    document.getElementById("filter-alcoholic").value = "";
    document.getElementById("filter-glass").value = "";
    Cards.renderCards(window.allCocktails || []);
  }

  return { getState, apply, attach, populateDropdowns, reset };
})();
