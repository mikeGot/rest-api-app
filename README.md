# REST API Application

REST API приложение для управления справочником Организаций, Зданий и Деятельности.

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x (async)
- PostgreSQL
- Alembic
- Docker

## Структура БД

Схема базы данных представлена в файле `schema.png`.

## Быстрый старт

### С использованием Docker

```bash
docker-compose up -d
```

Приложение будет доступно по адресу: http://localhost:8000

API документация (Swagger UI): http://localhost:8000/docs
Альтернативная документация (ReDoc): http://localhost:8000/redoc

### Локальная разработка

1. Установите зависимости:
```bash
poetry install
```

2. Создайте файл `.env` на основе `.env.example`

3. Запустите PostgreSQL

4. Примените миграции:
```bash
poetry run alembic upgrade head
```

5. Запустите приложение:
```bash
poetry run uvicorn app.main:app --reload
```

## API Key

Для доступа к API необходимо передавать API ключ в заголовке:
```
X-API-Key: your-api-key
```

По умолчанию (из .env): `test-api-key-12345`

## Разработка

### Установка dev зависимостей

```bash
poetry install --with dev
```


Теперь при каждом коммите будут автоматически запускаться линтеры.

### Тестирование

Проект использует **pytest** для тестирования.


## Полезные команды

```bash
make help          # Показать все доступные команды
make install       # Установить зависимости
make test          # Запустить тесты
make lint          # Проверить код линтерами
make format        # Отформатировать код
make clean         # Очистить кеш и временные файлы
```

## Миграции базы данных

### Создание миграции

```bash
# Внутри Docker контейнера
docker-compose exec app alembic revision --autogenerate -m "Migration description"

# Локально
poetry run alembic revision --autogenerate -m "Migration description"
```

### Применение миграций

```bash
# Внутри Docker контейнера
docker-compose exec app alembic upgrade head

# Локально
poetry run alembic upgrade head
```

### Откат миграции

```bash
# На один шаг назад
alembic downgrade -1

# До конкретной версии
alembic downgrade <revision>
```

## Тестовые данные

Заполнить базу тестовыми данными:

```bash
# Внутри Docker
docker-compose exec app python seed_data.py

# Локально
poetry run python seed_data.py
```
