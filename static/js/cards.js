const Cards = (() => {
  const grid    = () => document.getElementById("cards-grid");
  const loading = () => document.getElementById("loading");
  const error   = () => document.getElementById("error");
  const empty   = () => document.getElementById("empty");
  const count   = () => document.getElementById("results-count");

  function _alcBadgeClass(alcoholic) {
    if (!alcoholic) return "badge--cat";
    const v = alcoholic.toLowerCase();
    if (v === "alcoholic") return "badge--alc";
    if (v.includes("non")) return "badge--non";
    return "badge--opt";
  }

  function renderCard(cocktail) {
    const isFav = Favorites.isFavorite(cocktail.id);
    const article = document.createElement("article");
    article.className = "card";
    article.dataset.id = cocktail.id;

    article.innerHTML = `
      <button class="card__fav ${isFav ? "card__fav--active" : ""}"
              aria-label="${isFav ? "Убрать из избранного" : "В избранное"}"
              data-id="${cocktail.id}">
        ${isFav ? "♥" : "♡"}
      </button>
      <div class="card__img-wrap">
        <img class="card__img"
             src="${cocktail.image_url || "/static/img/placeholder.png"}"
             alt="${cocktail.name}"
             loading="lazy"
             onerror="this.src='/static/img/placeholder.png'" />
      </div>
      <div class="card__body">
        <h2 class="card__name">${cocktail.name}</h2>
        <div class="card__badges">
          ${cocktail.category ? `<span class="badge badge--cat">${cocktail.category}</span>` : ""}
          ${cocktail.alcoholic ? `<span class="badge ${_alcBadgeClass(cocktail.alcoholic)}">${cocktail.alcoholic}</span>` : ""}
        </div>
      </div>
    `;

    article.querySelector(".card__fav").addEventListener("click", async (e) => {
      e.stopPropagation();
      const btn = e.currentTarget;
      const newState = await Favorites.toggle(cocktail.id);
      btn.classList.toggle("card__fav--active", newState);
      btn.textContent = newState ? "♥" : "♡";
      btn.setAttribute("aria-label", newState ? "Убрать из избранного" : "В избранное");
    });

    article.addEventListener("click", () => openModal(cocktail));
    return article;
  }

  function renderCards(cocktails) {
    const g = grid();
    g.innerHTML = "";

    const countEl = count();
    if (cocktails.length === 0) {
      g.setAttribute("hidden", "");
      empty().removeAttribute("hidden");
      countEl.textContent = "";
      return;
    }

    empty().setAttribute("hidden", "");
    g.removeAttribute("hidden");
    countEl.textContent = `Показано: ${cocktails.length} коктейлей`;

    const frag = document.createDocumentFragment();
    cocktails.forEach((c) => frag.appendChild(renderCard(c)));
    g.appendChild(frag);
  }

  function showLoading()  { loading().removeAttribute("hidden"); }
  function hideLoading()  { loading().setAttribute("hidden", ""); }
  function showError(msg) {
    error().removeAttribute("hidden");
    document.getElementById("error-message").textContent = msg;
  }

  function openModal(cocktail) {
    const overlay = document.getElementById("modal-overlay");
    const content = document.getElementById("modal-content");

    const ingredientsHTML = cocktail.ingredients.map((ing) =>
      `<li><span>${ing.name}</span><span class="modal__measure">${ing.measure || ""}</span></li>`
    ).join("");

    content.innerHTML = `
      <img class="modal__img"
           src="${cocktail.image_url || "/static/img/placeholder.png"}"
           alt="${cocktail.name}"
           onerror="this.src='/static/img/placeholder.png'" />
      <h2 class="modal__title">${cocktail.name}</h2>
      <div class="modal__badges">
        ${cocktail.category ? `<span class="badge badge--cat">${cocktail.category}</span>` : ""}
        ${cocktail.alcoholic ? `<span class="badge ${_alcBadgeClass(cocktail.alcoholic)}">${cocktail.alcoholic}</span>` : ""}
        ${cocktail.glass ? `<span class="badge badge--cat">${cocktail.glass}</span>` : ""}
      </div>
      ${cocktail.ingredients.length ? `
        <div class="modal__section">
          <h3>Ингредиенты</h3>
          <ul class="modal__ingredients">${ingredientsHTML}</ul>
        </div>` : ""}
      ${cocktail.instructions ? `
        <div class="modal__section">
          <h3>Приготовление</h3>
          <p class="modal__instructions">${cocktail.instructions}</p>
        </div>` : ""}
    `;

    overlay.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    document.getElementById("modal-overlay").setAttribute("hidden", "");
    document.body.style.overflow = "";
  }

  async function init() {
    showLoading();
    try {
      const [cocktails] = await Promise.all([
        CocktailAPI.getAll(),
        Auth.init().then(() => Favorites.load()),
        Filters.populateDropdowns(),
      ]);
      window.allCocktails = cocktails;
      hideLoading();
      renderCards(cocktails);
      Filters.attach();
    } catch (e) {
      hideLoading();
      showError(`Ошибка загрузки: ${e.message}`);
      console.error(e);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("modal-close").addEventListener("click", closeModal);
    document.getElementById("modal-overlay").addEventListener("click", (e) => {
      if (e.target === e.currentTarget) closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });
  });

  document.addEventListener("DOMContentLoaded", init);

  return { renderCards, showLoading, hideLoading, showError };
})();
