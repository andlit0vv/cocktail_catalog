const Auth = (() => {
  let currentUser = null;

  async function init() {
    const wasLoggedIn = currentUser !== null;
    try {
      const res = await CocktailAPI.getMe();
      if (res.ok) {
        currentUser = await res.json();
      } else {
        currentUser = null;
      }
    } catch {
      currentUser = null;
    }

    renderHeader();

    if (currentUser) {
      if (typeof Chat !== 'undefined') Chat.init();
    } else {
      if (typeof Chat !== 'undefined') Chat.destroy();
    }

    if (!wasLoggedIn && currentUser !== null) {
      await Favorites.migrateLocalToServer();
    }
  }

  function renderHeader() {
    const section = document.getElementById("auth-section");
    if (!section) return;

    if (currentUser) {
      const pic = currentUser.picture_url
        ? `<img class="auth__avatar" src="${currentUser.picture_url}" alt="${currentUser.name}" />`
        : "";
      section.innerHTML = `
        ${pic}
        <span class="auth__name">${currentUser.name}</span>
        <button id="logout-btn" class="auth__logout">Выйти</button>
      `;
      document.getElementById("logout-btn").addEventListener("click", logout);
    } else {
      section.innerHTML = `<a href="/auth/login" class="btn-google">Войти через Google</a>`;
    }
  }

  async function logout() {
    await CocktailAPI.logout();
    location.reload();
  }

  function isLoggedIn() {
    return currentUser !== null;
  }

  return { init, renderHeader, logout, isLoggedIn, get currentUser() { return currentUser; } };
})();
