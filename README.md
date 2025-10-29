## Автотесты Effective Mobile — Playwright + Pytest + HTML‑отчёт

Проект покрывает тестами главную страницу `effective-mobile.ru`: клики по навигационным пунктам (якорям) приводят к скроллу в соответствующие секции и обновлению URL с фрагментом.

### Быстрый старт

**Клонирование:**
```bash
git clone https://github.com/DmitriyKuladmed/AutoTests_EffectiveMobile.git
cd AutoTests_EffectiveMobile
```

**Установка:**
```bash
pip install -r requirements.txt
python -m playwright install --with-deps
```

**Запуск тестов:**
```bash
pytest -m ui --html=report.html --self-contained-html
```

Отчёт автоматически откроется в браузере после завершения прогона.

### Технологии

- Python 3.10
- Playwright (pytest-playwright)
- Pytest + pytest-html
- Docker (опционально)

### Структура проекта

- `tests/pages/` — Page Object'ы (`BasePage`, `MainPage`)
- `tests/test_main_page_navigation.py` — UI тест на переход по всем якорным ссылкам
- `tests/conftest.py` — фикстуры, сбор логов, авто‑открытие HTML‑отчёта
- `pytest.ini` — настройки pytest
- `requirements.txt` — зависимости
- `Dockerfile`, `docker-compose.yml` — контейнеризация

### Запуск

**Локально:**

Если ещё не клонировали репозиторий:
```bash
git clone https://github.com/DmitriyKuladmed/AutoTests_EffectiveMobile.git
cd AutoTests_EffectiveMobile
```

Переопределить базовый URL (по умолчанию `https://effective-mobile.ru/`):
```bash
BASE_URL=https://effective-mobile.ru pytest -m ui --html=report.html --self-contained-html
```

Отключить автозапуск отчёта:
```bash
OPEN_REPORT=0 pytest -m ui --html=report.html --self-contained-html
```

**Docker:**

```bash
docker build -t em-tests .
docker run --rm -e BASE_URL=https://effective-mobile.ru/ -v %cd%:/app em-tests \
  pytest -m ui --html=report.html --self-contained-html
```

На Linux/macOS замените `%cd%` на `$(pwd)`.

**docker-compose:**

```bash
docker compose up --build
```

С кастомным URL:
```bash
BASE_URL=https://effective-mobile.ru docker compose up --build
```

После прогона откройте `report.html` в корне проекта.

### Отчёт

HTML‑отчёт (`report.html`) содержит:

- **Колонка URL** — текущий адрес страницы после проверки
- **Блок Log** — детальная информация:
  - Текущий URL
  - Сообщения консоли браузера (console/error)
  - Список сетевых ответов (status code + URL)
  - Итоговая статистика: `total`, `success`, `client_errors`, `server_errors`, `other`

Отчёт открывается автоматически после завершения прогона (отключается через `OPEN_REPORT=0`).

### Переменные окружения

- `BASE_URL` — базовый URL для тестов (по умолчанию `https://effective-mobile.ru/`)
- `OPEN_REPORT` — автоматически открывать HTML‑отчёт (по умолчанию `1`, установите `0` для отключения)

### Детали реализации

- **Page Object паттерн** — `MainPage` собирает уникальные якорные ссылки и обрабатывает переходы
- **Динамический сбор ссылок** — тест находит все `#fragment` ссылки, исключая попапы и невидимые элементы
- **Проверки:**
  - URL содержит соответствующий фрагмент
  - Целевая секция существует (поиск по `id`, `name`, `data-anchor`)
  - Секция прокручивается в видимую область
- **Автоматическая очистка** — каталог `allure-results` удаляется перед каждым запуском (если существует)
