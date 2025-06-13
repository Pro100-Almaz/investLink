<h1 align=center><strong>FastAPI Backend Application for InvestLink</strong></h1>

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
   # For testing without Docker
   pytest
   
   # For testing within Docker
   docker exec backend_app pytest
   ```

4. `Pre-Commit` setup:
    ```shell
    # Make sure you are in the ROOT project directory
    pre-commit install
    pre-commit autoupdate
    ```

5. Backend app credentials setup:
    If you are not used to VIM or Linux CLI, then ignore the `echo` command and do it manually. All the secret variables for this template are located in `.env.example`.

    If you want to have another name for the secret variables, don't forget to change them also in:

    * `backend/src/config/base.py`
    * `docker-compose.yaml`

    ```shell
    # Make sure you are in the ROOT project directory
    touch .env

    echo "SECRET_VARIABLE=SECRET_VARIABLE_VALUE" >> .env
    ```

6. `CODEOWNERS` setup:
    Go to `.github/` and open `CODEOWNERS` file. This file is to assign the code to a specific team member so you can distribute the weights of the project clearly.

7. Docker setup:
   ```shell
    # Make sure you are in the ROOT project directory
    chmod +x backend/entrypoint.sh

    docker-compose build
    docker-compose up

    # Every time you write a new code, update your container with:
    docker-compose up -d --build
   ```

8. (IMPORTANT) Database setup:
   ```shell
    # (Docker) Generate revision for the database auto-migrations
    docker exec backend_app alembic revision --autogenerate -m "YOUR MIGRATION TITLE"
    docker exec backend_app alembic upgrade head    # to register the database classes
    
    # (Local) Generate revision for the database auto-migrations
    alembic revision --autogenerate -m "YOUR MIGRATION TITLE"
    alembic upgrade head    # to register the database classes
   ```

9. Go to https://about.codecov.io/, and sign up with your github to get the `CODECOV_TOKEN`

10. Go to your GitHub and register all the secret variables (look in .env.example) in your repository (`settings` $\rightarrow$ (scroll down a bit) `Secrets` $\rightarrow$ `Actions` $\rightarrow$ `New repository secret`)

**IMPORTANT**: Without the secrets registered in Codecov and GitHub, your `CI` will fail and life will be horrible 🤮🤬
**IMPORTANT**: Remember to always run the container update every once in a while. Without the arguments `-d --build`, your `Docker` dashboard will be full of junk containers!

## Project Structure

```shell
.github/
├── workflows/
    ├── ci-backend.yaml                 # A CI file for the backend app that consists of `build`, `code-style`, and `test`
├── CODEOWNERS                          # A configuration file to distribute code responsibility
├── semantic.yaml                       # A configuration file for ensuring an automated semantic commit message

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
        ├── schemas/
            ├── account.py              # Account classes for data validation objects
            ├── base.py                 # Base class for data validation objects
    ├── repository/
        ├── crud/
            ├── account.py              # C. R. U. D. operations for Account entity
            ├── base.py                 # Base class for C. R. U. D. operations
        ├── migrations/
            ├── versions/
            ├── env.py                  # Generated via alembic for automigration
            ├── script.py.mako          # Generated via alembic
        ├── base.py                     # Entry point for alembic automigration
        ├── database.py                 # Database class with engine and session
        ├── events.py                   # Registration of database events
        ├── table.py                    # Custom SQLAlchemy Base class
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
        ├── test_src.py                 # Testing the src directory's version
    ├── conftest.py                     # The fixture codes and other base test codes
├── Dockerfile                          # Docker configuration file for backend application
├── README.md                           # Documentation for backend app
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

## Final Step

You can delete these 3 files (or change its content based on your need):
- `LICENSE.md`
- `README.md`
- `backend/README.md`

Enjoy your development and may your technology be forever useful to everyone 😉🚀🧬

---
