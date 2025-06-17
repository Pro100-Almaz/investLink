<h1 align=center><strong>FastAPI Backend Application for InvestLink</strong></h1>


A FastAPI-based proxy for fetching and caching historical market data from Polygon.io.  
Этот сервис минимизирует запросы к Polygon.io, ускоряет ответы клиентов и обеспечивает надёжное хранение временных рядов.

---

## Table of Contents

1. [Storage Selection](#storage-selection)  
2. [Getting Started](#getting-started)  
3. [Set Up](#setup-guide)  
4. [Project Structure](#project-structure)  

---

## Storage Selection

### 1. Goals & Requirements

- **Работа с временными рядами**  
  - Высокая скорость вставок и запросов по диапазонам времени.  
- **Масштабируемость**  
  - Обработка тысяч вставок/запросов без деградации производительности.  
- **Привычный SQL**  
  - Полная поддержка ANSI-SQL и знакомых инструментов (ORM, PgAdmin).  
- **Управление объёмом данных**  
  - Сжатие и «архивация» старых данных без потери доступности.

### 2. Альтернативы

- **InfluxDB** — специализирован для TSDB, требует Flux/InﬂuxQL  
- **Apache Cassandra** — линейная масштабируемость, но нет гибких агрегатов  
- **MongoDB Time Series** — гибкая схема, но менее эффективная для аггрегаций  
- **RedisTimeSeries** — быстрый, но хранит всё в памяти/журнале  
- **Elasticsearch** — мощный поиск и аггрегации, но дорого шардится при высокой нагрузке

### 3. Сравнение

| Параметр                       | TimescaleDB       | InfluxDB            | Cassandra          | MongoDB TS          | RedisTS           |
|--------------------------------|-------------------|---------------------|--------------------|---------------------|-------------------|
| Язык запросов                  | PostgreSQL (SQL)  | Flux / InfluxQL     | CQL                | Mongo-query         | собственный API   |
| Горизонтальное масштабирование | ✔ (multi-node)    | ✔ (Enterprise)      | ✔                  | ✔                   | ограничено        |
| Compression & retention        | гипертейблы + компрессия | TSM-сжатие   | ❌                  | WiredTiger-сжатие   | ❌                |
| Continuous aggregates          | ✔                 | ✔                   | ❌                  | ✔                   | ✔                 |
| OLTP + OLAP нагрузки           | ✔ гибридная       | меньше OLAP         | OLTP-ориентир.     | гибридно            | OLTP-ориентир.    |

### 4. Почему TimescaleDB

1. **PostgreSQL-совместимость**  
   – привычный SQL, оконные функции, JOIN’ы, CTE.  
2. **Hypertables**  
   – автоматический шардинг по времени и по ключу.  
3. **Continuous Aggregates**  
   – предрасчёт и кэширование агрегатов для мгновенного отклика.  
4. **Встроенная компрессия**  
   – экономия места на диске без потери скорости запросов.  
5. **Гибрид OLTP/OLAP**  
   – одновременная обработка вставок и сложных аналитических запросов.  
6. **Экосистема**  
   – интеграция с Grafana/Promscale, зрелая документация.

### 5. Вывод

**TimescaleDB** сочетает в себе преимущества реляционной СУБД (транзакции, SQL) и специализированных TSDB-функций (гипертейблы, аггрегации, компрессия). Это делает её оптимальным выбором для нашего прокси-сервиса исторических котировок.


## Getting Started



<br>

This is a template repository aimed to provide for InvestLink mt coding skills and general knowledge in Backend. 

* 🐳 [Dockerized](https://www.docker.com/)
* 🐘 [Asynchronous PostgreSQL](https://www.postgresql.org/docs/current/libpq-async.html)
* ⏰ [TimesacleDB](https://www.timescale.com/)
* 🐍 [FastAPI](https://fastapi.tiangolo.com/)

When the `Docker` is started, these are the URL addresses:

* Backend Application (API docs) $\rightarrow$ `http://localhost:8001/docs`
* Database editor (Adminer) $\rightarrow$ `http//localhost:8081`

The backend API without `Docker` can be found in `http://localhost:8000/docs`.

## Setup Guide

This backend application is setup with `Docker`. Nevertheless, you can see the full local setup without `Docker` in [backend/README.md](https://github.com/Aeternalis-Ingenium/FastAPI-Backend-Template/blob/trunk/backend/README.md).

1. Before setting up the backend app, please create a new directory called `coverage` for the testing report purpose:
   ```shell
   cd backend && mkdir coverage
   ```

2. Backend app setup:
    ```shell
    # Creating VENV
    pyenv virtualenv 3.11.0 any_venv_name
    pyenv local any_venv_name

    # Install dependencies
    pip3 install -r requirements.txt

    # Test run your backend server
    uvicorn src.main:backend_app --reload
    ```

3. Testing with `PyTest`:
   Make sure that you are in the `backend/` directory.
   ```shell
   docker run -d \             
        --name test-postgres \
        -e POSTGRES_USER=testuser \
        -e POSTGRES_PASSWORD=testpass \
        -e POSTGRES_DB=testdb \
        -p 5433:5432 \
        postgres:15

    docker run -d \
        --name redis \
        -p 6379:6379 \
        -v redis_data:/data \
        redis:latest
        
   # For testing without Docker
   pytest
   ```

4. Docker setup:
   ```shell
    # Make sure you are in the ROOT project directory
    chmod +x backend/entrypoint.sh

    docker-compose build
    docker-compose up

    # Every time you write a new code, update your container with:
    docker-compose up -d --build
   ```

5. Go to https://about.codecov.io/, and sign up with your github to get the `CODECOV_TOKEN`

## Project Structure

```shell
backend/
├── coverage/
├── src/
    ├── api/
        ├── dependencies/               # Dependency injections
            ├── session.py
            ├──repository.py
        ├── routes/                     # Endpoints
            ├── account.py              # Account routes
            ├── authentication.py       # Signup and Signin routes
            ├── market.py               # Market ticker endpoints
        ├── endpoints.py                # Endpoint registration
    ├── config/
        ├── settings/
            ├── base.py                 # Base settings / settings parent class
                ├── development.py      # Development settings
                ├── environments.py     # Enum with PROD, DEV, STAGE environment
                ├── production.py       # Production settings
                ├── staging.py          # Test settings
        ├── events.py                   # Registration of global events
        ├── manager.py                  # Manage get settings
    ├── models/
        ├── db/
            ├── account.py              # Account class for database entity
            ├── market.py               # Ticker class for database entity
        ├── schemas/
            ├── account.py              # Account classes for data validation objects
            ├── base.py                 # Base class for data validation objects
    ├── repository/
        ├── crud/
            ├── account.py              # C. R. U. D. operations for Account entity
            ├── base.py                 # Base class for C. R. U. D. operations
            ├── market.py               # C. R. U. D. operations for Ticker entity
        ├── base.py                     # Entry point for alembic automigration
        ├── database.py                 # Database class with engine and session
        ├── events.py                   # Registration of database events
        ├── poligion_client.py          # Poligon.io interaction client
        ├── redis.py                    # NoSQL database for caching the frequent requests
        ├── table.py                    # Custom SQLAlchemy Base class
    ├── scheduler/
        ├── tasks.py                    # Cron functions to process regularly
    ├── security/
        ├── hashing/
            ├── hash.py                 # Hash functions with passlib
            ├── password.py             # Password generator with hash functions
        ├── authorizations/
            ├── jwt.py                  # Generate JWT tokens with python-jose
        ├── verifications/
            ├── credentials.py          # Check for attributes' availability
    ├── utilities/
        ├── exceptions/
            ├── http/
                ├── http_exc_400.py     # Custom 400 error handling functions
                ├── http_exc_401.py     # Custom 401 error handling functions
                ├── http_exc_403.py     # Custom 403 error handling functions
                ├── http_exc_404.py     # Custom 404 error handling functions
            ├── database.py             # Custom `Exception` class
            ├── password.py             # Custom `Exception` class
        ├── formatters/
            ├── datetime_formatter.py   # Reformat datetime into the ISO form
            ├── field_formatter.py      # Reformat snake_case to camelCase
        ├── messages/
            ├── http/
                ├── http_exc_details.py	# Custom message for HTTP exceptions
    ├── main.py                         # Our main backend server app
├── tests/
    ├── end_to_end_tests/               # End-to-end tests
    ├── integration_tests/              # Integration tests
    ├── security_tests/                 # Security-related tests
    ├── unit_tests/                     # Unit tests
    ├── conftest.py                     # The fixture codes and other base test codes
├── Dockerfile                          # Docker configuration file for backend application                           # Documentation for backend app
├── entrypoint.sh                       # A script to restart backend app container if postgres is not started
├── alembic.ini                         # Automatic database migration configuration
├── pyproject.toml                      # Linter and test main configuration file
├── requirements.txt                    # Packages installed for backend app
.dockerignore                           # A file that list files to be excluded in Docker container
.gitignore                              # A file that list files to be excluded in GitHub repository
.pre-commit-config.yaml                 # A file with Python linter hooks to ensure conventional commit when committing
LICENSE.md                              # A license to use this template repository (delete this file after using this repository)
README.md                               # The main documentation file for this template repository
codecov.yaml                            # The configuration file for automated testing CI with codecov.io
docker-compose.yaml                     # The main configuration file for setting up a multi-container Docker
```

---
