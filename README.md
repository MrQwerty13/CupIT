# CupIT

Локальный MVP аналитики для кафе: JSON-данные нормализуются в доменные модели,
чистое аналитическое ядро рассчитывает KPI, Flask API отдаёт результаты, а
web-app показывает dashboard и безопасно передаёт агрегаты локальной Ollama.

Техническое устройство описано в [ARCHITECTURE.md](./ARCHITECTURE.md), план
дальнейшей разработки — в [todo.md](./todo.md).

## Что уже работает

- нормализованные `Cafe`, `Product`, `Receipt`, `SaleLine`;
- заменяемый `DataProvider` и JSON adapter;
- детерминированный набор из 10 товаров и более 500 чеков;
- выручка, прибыль, маржа, средний чек, проданные позиции;
- дневная динамика и рейтинг товаров;
- Flask API с валидацией и JSON errors;
- AI endpoint, который получает только агрегаты и корректно переживает
  недоступность Ollama;
- адаптивный web dashboard с выбором периода и AI drawer;
- Docker Compose для API, web и Ollama;
- unit/API tests.

PostgreSQL queue, реальные импорты 1C/iiko и PDF worker остаются следующими
этапами. Текущий JSON slice намеренно сохраняет границы, нужные для их добавления.

## Локальный запуск

Требования: Python 3.12+, Node.js 22+.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/generate_sample_data.py
.venv/bin/python services/app/run.py
```

API будет доступен на `http://localhost:5050/api/v1`.

Во втором терминале:

```bash
cd web
npm ci --ignore-scripts
npm run dev
```

Web-app будет доступен на `http://localhost:3000` и автоматически подключится к
локальному API. Если API выключен, интерфейс остаётся доступен в demo mode.

## Подготовка и перенос данных

Создать единый JSON-шаблон с текущим каталогом товаров и примером чека:

```bash
.venv/bin/python scripts/dataset_manager.py template ./cupit-data.json
```

Заполните `cafe`, `products` и `sales`, затем проверьте и перенесите файл:

```bash
.venv/bin/python scripts/dataset_manager.py import ./cupit-data.json
```

Скрипт принимает три варианта:

- единый bundle JSON с ключами `cafe`, `products`, `sales`;
- каталог с `cafe.json`, `products.json`, `sales.json`;
- отдельный JSON-массив чеков с `--catalog` для карточек кафе и товаров.

```bash
.venv/bin/python scripts/dataset_manager.py import ./sales.json \
  --catalog ./data/samples
```

Перед активацией данные проходят ту же валидацию, что и API. Каждая партия
сохраняется в отдельном каталоге с SHA-256 и `manifest.json`; предыдущие партии
не удаляются. После успешного импорта перезапустите API. Для загрузки без
переключения активного набора добавьте `--no-activate`.

## Docker

Вся система запускается из корня проекта одной командой:

```bash
docker compose up --build
```

- web: `http://localhost:3000`;
- API: `http://localhost:5050/api/v1`;
- Ollama: `http://localhost:11434`.

При первом запуске `ollama-init` автоматически скачает модель
`qwen2.5:3b`. Другую модель можно выбрать в `.env` через `OLLAMA_MODEL`.
Повторные запуски используют сохранённый Docker volume и не скачивают модель
заново.

Остановка:

```bash
docker compose down
```

## API

```text
GET  /api/v1/health
GET  /api/v1/dashboard?from=2026-08-01&to=2026-08-14
GET  /api/v1/analytics
GET  /api/v1/products
GET  /api/v1/products/performance
GET  /api/v1/sales/daily
POST /api/v1/ai/insights
```

Пример AI-запроса:

```bash
curl -X POST http://localhost:5050/api/v1/ai/insights \
  -H 'Content-Type: application/json' \
  -d '{"question":"Какие три действия повысят прибыль?"}'
```

При недоступной Ollama endpoint возвращает `503 AI_UNAVAILABLE`; health,
dashboard и обычная аналитика продолжают работать.

## Тесты

```bash
.venv/bin/pytest -q
cd web && npm run build
```

## Поток данных

```text
JSON -> JsonDataProvider -> domain models -> analytics -> service -> Flask API
                                                               -> web-app
                                                               -> AI -> Ollama
```

Аналитика не читает JSON и не импортирует Flask/Ollama. Новый источник должен
реализовать `DataProvider`, не меняя формулы и API.
