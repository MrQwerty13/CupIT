# CupIT — план реализации

План основан на переданном `to_do.md` и технических решениях из
[`ARCHITECTURE.md`](./ARCHITECTURE.md). Задачи внутри этапа выполняются сверху
вниз. Новый этап начинается после выполнения критерия готовности предыдущего.

Обозначения: `P0` — блокирует MVP, `P1` — нужно для качественного релиза,
`P2` — развитие после MVP.

## 0. Проектирование и каркас

- [x] `P0` Изучить исходное видение из `to_do.md`.
- [x] `P0` Зафиксировать границы сервисов, потоки и владение данными.
- [x] `P0` Зафиксировать модель чека и снимки цены/себестоимости.
- [x] `P0` Утвердить стек первой версии: Python 3.12, Flask, PostgreSQL,
  SQLAlchemy/Alembic, pytest, Ollama, Docker Compose.
- [ ] `P0` Создать каталоги `services`, `packages`, `migrations`, `infra`, `tests`.
- [ ] `P0` Настроить единые lint/format/type-check команды.
- [x] `P0` Создать `.env.example`, `.gitignore` и корневой `README.md`.
- [ ] `P1` Добавить ADR для общей PostgreSQL с логическими схемами.
- [ ] `P1` Добавить CI: lint, type check, unit, integration, build images.

Готово, когда структура репозитория создана, базовые команды разработки
задокументированы, а автоматические проверки запускаются одной командой.

## 1. Контракты и доменная модель

- [ ] `P0` Описать DTO и API schemas для import, analytics, AI, report и errors.
- [ ] `P0` Реализовать `Cafe`, `Location`, `Category`, `Product`, `Receipt`,
  `SaleLine` с type hints и валидацией инвариантов.
- [x] `P0` Использовать `Decimal` для денег и timezone-aware datetime.
- [ ] `P0` Определить статусы и переходы `ImportBatch`, `Job`, `AnalyticsRun`,
  `AiInsight`, `Report`.
- [ ] `P0` Ввести `external_id`, checksum и idempotency key.
- [ ] `P0` Определить формулы KPI и правила округления в одном документе.
- [ ] `P1` Добавить OpenAPI/JSON Schema и contract tests.

Готово, когда схемы покрыты unit-тестами, а одинаковые контракты используются
производителем и потребителем без импорта бизнес-кода между сервисами.

## 2. PostgreSQL и миграции

- [ ] `P0` Поднять PostgreSQL в Docker Compose с persistent volume.
- [ ] `P0` Создать схемы `core`, `ingestion`, `analytics`, `ai`, `reporting`,
  `jobs`.
- [ ] `P0` Создать первую Alembic migration для минимальной доменной модели.
- [ ] `P0` Добавить PK/FK, unique constraints и индексы периода/кафе/товара.
- [ ] `P0` Настроить роли БД: владелец пишет, остальные читают только нужное.
- [ ] `P0` Реализовать repository interfaces и PostgreSQL adapters.
- [ ] `P1` Добавить migration tests на чистую БД и upgrade.
- [ ] `P1` Описать backup/restore локальных данных.

Готово, когда миграции применяются с нуля, ограничения ловят дубликаты и
нарушение ссылочной целостности, а тесты не зависят от порядка запуска.

## 3. Очередь заданий

- [ ] `P0` Реализовать таблицу jobs и атомарный захват через `SKIP LOCKED`.
- [ ] `P0` Реализовать worker loop, heartbeat и graceful shutdown.
- [ ] `P0` Реализовать состояния `queued/running/completed/failed/cancelled`.
- [ ] `P0` Возвращать зависшие jobs в очередь после заданного timeout.
- [ ] `P0` Добавить ограниченные retry только для временных ошибок.
- [ ] `P0` Версионировать payload для import, analytics, AI и report jobs.
- [ ] `P0` Ограничить worker захватом и обновлением jobs только своего типа.
- [ ] `P1` Добавить метрики глубины очереди и длительности выполнения.
- [ ] `P2` Рассмотреть внешний broker только после нагрузочных измерений.

Готово, когда перезапуск worker не теряет задание и не приводит к двойной
фиксации результата.

## 4. Data Ingestion Service

- [x] `P0` Определить интерфейс `DataSourceAdapter`.
- [x] `P0` Реализовать JSON adapter и формат sample dataset.
- [x] `P0` Подготовить реалистичные данные: минимум 10 товаров, несколько
  категорий/дней/чеков и не менее 100 строк продаж.
- [ ] `P0` Реализовать pipeline raw -> parse -> validate -> normalize -> upsert.
- [ ] `P0` Сохранять исходный файл, checksum, source и метаданные партии.
- [ ] `P0` Реализовать атомарную запись валидной партии.
- [ ] `P0` Реализовать отчёт ошибок по строкам без падения всего процесса.
- [ ] `P0` Гарантировать идемпотентность повторной загрузки.
- [ ] `P0` Добавить статусы `pending/running/completed/partial/failed`.
- [x] `P0` Покрыть тестами missing/malformed/invalid/duplicate JSON.
- [x] `P0` Добавить CLI для шаблона, проверки и версионированного переноса данных.
- [ ] `P1` Добавить лимиты размера, безопасные имена и очистку временных файлов.
- [ ] `P2` Реализовать CSV adapter.
- [ ] `P2` Спроектировать 1C adapter на реальном примере экспорта/API.
- [ ] `P2` Спроектировать iiko adapter на реальном контракте API.

Готово, когда повторный импорт sample JSON не создаёт дубликаты, ошибки видны
по API, а данные в `core` не содержат частично записанных чеков.

## 5. Analytics Service

- [x] `P0` Реализовать чистые функции для revenue, sold units, receipt count,
  average receipt, gross profit и margin.
- [ ] `P0` Реализовать группировки по дню, товару, категории и точке.
- [ ] `P0` Реализовать best/least-selling и most-profitable rankings.
- [ ] `P0` Корректно учитывать возвраты, скидки, нулевую цену и inactive products.
- [x] `P0` Выполнять дневную агрегацию в timezone кафе.
- [ ] `P0` Создавать неизменяемый `AnalyticsRun` с периодом и версией алгоритма.
- [ ] `P0` Сохранять агрегаты и публиковать стабильные read views для app.
- [x] `P0` Добавить детерминированные unit tests для всех формул.
- [ ] `P0` Добавить golden dataset с заранее рассчитанными результатами.
- [ ] `P1` Замерить расчёт на целевом объёме и добавить необходимые индексы.
- [ ] `P2` Добавить месячные тренды, аномалии и сравнение периодов.

Готово, когда результаты golden dataset совпадают до заданного правила
округления и analytics не импортирует ingestion/file parsing код.

## 6. CupIT App и внешний API

- [x] `P0` Создать application factory и конфигурацию через environment.
- [x] `P0` Реализовать единый JSON error envelope.
- [ ] `P0` Добавить request ID во входящие запросы, логи и error envelope.
- [x] `P0` Реализовать `GET /api/v1/health`.
- [ ] `P0` Реализовать создание и просмотр import jobs.
- [ ] `P0` Реализовать создание и просмотр analytics runs.
- [x] `P0` Реализовать dashboard и product performance endpoints.
- [ ] `P0` Возвращать `202`, `job_id`, status URL и `Retry-After` для тяжёлых задач.
- [ ] `P0` Связать внешние запросы с созданием jobs и чтением результатов.
- [x] `P0` Валидировать даты, идентификаторы и формат JSON-запроса.
- [ ] `P0` Добавить валидацию формата и размера файла после появления upload endpoint.
- [ ] `P1` Сформировать OpenAPI и примеры curl для каждого endpoint.
- [x] `P1` Реализовать минимальный dashboard UI после стабилизации API.

Готово, когда пользователь может импортировать sample JSON, запустить расчёт и
получить dashboard только через внешний API, не обращаясь к сервисам напрямую.

## 7. AI Service и Ollama

- [x] `P0` Поднять Ollama отдельным Compose service с persistent model volume.
- [x] `P0` Вынести host, model, timeout и параметры генерации в environment.
- [x] `P0` Создать allowlist метрик, разрешённых для AI-контекста.
- [ ] `P0` Реализовать context builder только из сохранённого `AnalyticsRun`.
- [x] `P0` Создать версионированный prompt template.
- [x] `P0` Реализовать клиент Ollama с timeout.
- [ ] `P0` Добавить контролируемые retry временных ошибок после появления async jobs.
- [ ] `P0` Реализовать create/status endpoints для AI insight.
- [ ] `P0` Сохранять model, prompt_version и ссылку на analytics run.
- [x] `P0` Возвращать понятную ошибку, если Ollama недоступна.
- [x] `P0` Проверить, что app/analytics работают без Ollama.
- [ ] `P1` Добавить Ollama stub и тесты prompt/context без реальной модели.
- [ ] `P1` Добавить лимит контекста и удаление персональных полей.

Готово, когда AI отвечает на основании выбранного снимка аналитики, не имеет
доступа к raw/core данным, а отключение Ollama не нарушает остальные сценарии.

## 8. PDF Reporting Service

- [ ] `P0` Определить контракт report request/result.
- [ ] `P0` Создать один версионированный шаблон отчёта.
- [ ] `P0` Добавить KPI, динамику, товары, категории и AI-рекомендации.
- [ ] `P0` Строить графики только из выбранного `AnalyticsRun`.
- [ ] `P0` Сохранять PDF в отдельный volume, а в БД — метаданные и checksum.
- [ ] `P0` Реализовать create/status/download endpoints.
- [ ] `P0` Обработать отсутствие AI insight: отчёт должен формироваться без него.
- [ ] `P1` Проверять PDF рендерингом страниц и visual/golden tests.
- [ ] `P1` Добавить очистку устаревших файлов по retention policy.

Готово, когда PDF воспроизводим из зафиксированных входов, совпадает по цифрам
с dashboard и открывается стандартным PDF reader.

## 9. Docker и локальная установка

- [ ] `P0` Создать отдельный Dockerfile для каждого сервиса.
- [ ] `P0` Собрать Compose: app, ingestion, analytics, ai, report, postgres, ollama.
- [ ] `P0` Открыть на хосте только app; workers и БД оставить в Docker network.
- [ ] `P0` Настроить healthchecks, restart policy и dependency readiness.
- [ ] `P0` Запускать контейнеры не от root.
- [ ] `P0` Настроить volumes для PostgreSQL, raw, reports и Ollama models.
- [ ] `P0` Проверить холодный запуск `docker compose up --build`.
- [ ] `P1` Добавить dev profile с bind mounts и быстрым reload.
- [ ] `P1` Зафиксировать patch/digest версии base images (Python/Node); версии dependencies уже зафиксированы.
- [ ] `P1` Проверить backup/restore на отдельной тестовой установке.

Готово, когда чистая машина с Docker запускает CupIT по README одной командой,
данные переживают restart, а недоступность Ollama отражается только на AI.

## 10. Наблюдаемость, безопасность и устойчивость

- [ ] `P0` Включить структурированные JSON-логи без секретов и raw payloads.
- [ ] `P0` Прокидывать `request_id`, `job_id`, `cafe_id` через job payload/logs.
- [ ] `P0` Добавить liveness и readiness каждому сервису.
- [ ] `P0` Настроить DB pool, таймауты внешних вызовов и graceful shutdown.
- [ ] `P0` Запретить stack traces во внешних ответах.
- [ ] `P1` Добавить метрики запросов, ошибок, очередей и длительности jobs.
- [ ] `P1` Добавить dependency/container vulnerability scan в CI.
- [ ] `P1` Документировать threat model локальной установки.
- [ ] `P2` Добавить authentication, роли и audit log перед multi-user режимом.

Готово, когда сбой любого необязательного сервиса диагностируется по health и
логам, не раскрывает чувствительные данные и не вызывает каскадного падения.

## 11. Сквозная проверка и релиз MVP

- [x] `P0` Unit tests проходят для domain, ingestion и analytics.
- [ ] `P0` Contract tests проходят для внешнего API и всех job payloads.
- [ ] `P0` Integration tests проходят с реальным PostgreSQL и Ollama stub.
- [ ] `P0` E2E: sample JSON -> import -> analytics -> dashboard.
- [ ] `P0` E2E: analytics -> AI stub -> PDF -> download.
- [ ] `P0` E2E: malformed import даёт отчёт и не портит существующие данные.
- [x] `P0` API-тест: Ollama down не ломает health и analytics.
- [ ] `P0` E2E: Ollama down не ломает health, import, analytics и PDF без AI.
- [ ] `P0` Сверить каждый KPI вручную на golden dataset.
- [x] `P0` Написать README: установка, конфигурация, API и тесты.
- [ ] `P0` Добавить backup/restore раздел после внедрения PostgreSQL.
- [ ] `P0` Подготовить release checklist и версию `0.1.0`.
- [ ] `P1` Провести короткий пилот на обезличенном наборе данных кафе.

MVP принят, когда чистая локальная установка проходит оба основных E2E-потока,
все P0-задачи закрыты, расчёты воспроизводимы, а исходные данные не передаются
во внешние сервисы.

## 12. После MVP

- [ ] `P2` CSV, 1C и iiko adapters на подтверждённых пользовательских форматах.
- [ ] `P2` Плановые импорты и инкрементальная синхронизация.
- [ ] `P2` Сравнение нескольких точек и консолидация по кафе.
- [ ] `P2` Прогнозы только после накопления и оценки качества данных.
- [ ] `P2` Hybrid/cloud deployment с явным согласием владельца данных.
- [ ] `P2` Объектное хранилище для raw/PDF.
- [ ] `P2` Внешний broker и отдельные БД при подтверждённой нагрузке.
- [ ] `P2` Kubernetes только после появления требований к масштабированию/SLA.
