# Cocktail Catalog

Локальный сайт-каталог коктейлей на FastAPI + ванильный JS.  
Данные берутся из TheCocktailDB API, кэшируются в памяти. Пользователи и избранное хранятся в SQLite.

## Быстрый старт

### 1. Установка зависимостей

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt
```

### 2. Настройка .env

Скопируйте `.env.example` в `.env` и заполните поля:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

В файле `.env` нужно заполнить четыре значения:

| Переменная | Что вставить |
|---|---|
| `GOOGLE_CLIENT_ID` | Client ID из Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Client Secret из Google Cloud Console |
| `JWT_SECRET` | Случайная строка — генерируется командой ниже |
| `SESSION_SECRET` | Ещё одна случайная строка — генерируется командой ниже |

**Как сгенерировать JWT_SECRET и SESSION_SECRET:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Запустите команду **два раза** — получите две разные строки. Первую вставьте в `JWT_SECRET`, вторую в `SESSION_SECRET`.

Это просто случайные пароли, которыми сервер подписывает сессии и токены. Без них приложение не сможет безопасно хранить состояние входа. Конкретные значения не важны — главное, чтобы они были случайными и секретными.

### 3. Настройка Google OAuth (один раз)

1. Откройте [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. **OAuth consent screen** → External → добавьте scopes: `openid`, `email`, `profile`
3. **Audience → Test users** → добавьте свой Gmail
4. **Clients → Create OAuth Client** → тип Web application
5. В поле **Authorized redirect URIs** добавьте ровно:
   ```
   http://localhost:8000/auth/callback
   ```
   (без слеша в конце, именно `localhost`, не `127.0.0.1`)
6. Скопируйте **Client ID** и **Client Secret** в `.env`

### 4. Применить миграцию БД (один раз)

```bash
alembic upgrade head
```

Создаст файл `cocktails.db` с таблицами `users` и `favorites`.

### 5. Запуск

```bash
uvicorn app.main:app --reload
```

Сайт: http://localhost:8000

---

## Как это работает

При первом запуске бэкенд загружает все ~400+ коктейлей из TheCocktailDB (15–30 секунд). Потом данные в памяти, ответы мгновенные.

**Гость** — сердечки сохраняются в localStorage браузера.  
**После входа** — избранное автоматически переносится из localStorage в БД и хранится там. При следующем входе оно на месте.

---

## Структура проекта

```
cocktail-app/
├── .env                        # Секреты (не коммитить!)
├── alembic/                    # Миграции БД
├── app/
│   ├── config.py               # Настройки (pydantic-settings)
│   ├── main.py                 # Точка входа FastAPI
│   ├── db.py                   # Async SQLAlchemy engine
│   ├── dependencies.py         # get_current_user / get_optional_user
│   ├── models/                 # SQLAlchemy ORM: User, Favorite
│   ├── repositories/           # Запросы к БД
│   ├── routers/
│   │   ├── cocktails.py        # JSON API /api/cocktails
│   │   ├── pages.py            # HTML страница
│   │   ├── auth.py             # /auth/login, /callback, /logout, /me
│   │   └── favorites.py        # /api/favorites
│   ├── schemas/                # Pydantic-схемы
│   └── services/
│       ├── cache.py            # In-memory кэш коктейлей
│       ├── cocktaildb.py       # HTTP-клиент TheCocktailDB
│       ├── jwt_service.py      # Создание/проверка JWT
│       └── oauth.py            # Authlib Google OAuth
├── static/
│   ├── css/style.css
│   └── js/
│       ├── api.js              # fetch-обёртки
│       ├── auth.js             # Состояние пользователя, шапка
│       ├── favorites.js        # Гибрид localStorage ↔ API
│       ├── filters.js          # Фильтры и поиск
│       └── cards.js            # Рендер карточек
└── templates/
    └── index.html
```

---

## Типичные проблемы

**`redirect_uri_mismatch`** — в Google Console URI должен быть точно `http://localhost:8000/auth/callback` (не `127.0.0.1`, не со слешем в конце).

**`Access blocked: This app's request is invalid`** — не добавили свой Gmail в Test Users в OAuth consent screen.

**Cookie не сохраняется** — убедитесь, что открываете сайт через `localhost`, а не `127.0.0.1`.

**Сервер падает при старте** — проверьте, что в `.env` заполнены все четыре поля: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET`, `SESSION_SECRET`.
