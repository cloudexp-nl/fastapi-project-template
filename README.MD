# FastAPI App

``` bash
fastapi_app/
├── alembic/                       # Database migrations
├── src/                           # Application source code
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization and route inclusion
│   ├── core/                      # Shared utilities and setup
│   │   ├── __init__.py
│   │   ├── config.py              # Global app configuration (settings management)
│   │   ├── database.py            # Database connection logic
│   │   ├── middleware.py          # Global middleware (e.g., CORS, logging)
│   │   └── security.py            # Security utilities (e.g., password hashing, JWT tools)
│   ├── auth/                      # Authentication module
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   ├── posts/                     # Posts module
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_main.py
├── .env                           # Environment variables
├── .gitignore                     # Git ignore file
├── Dockerfile                     # Dockerfile for containerization
├── docker-compose.yml             # Docker Compose for local development
├── pyproject.toml                 # Python project dependencies and settings
├── requirements/                  # Dependency management
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│   └── test.txt                # Test API script
├── logging.ini                    # Logging configuration
└── README.md 
```

## Building & staring the project in Docker-compose

``` bash
docker-compose up --build
```

## Alternative way to start the project

``` bash

docker run --rm --name fastapi_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=fastapi_db -p 5432:5432 -d postgres:17
```

Set the database url for alembic (db migration tool)

``` bash
export DATABASE_URL="postgresql://user:password@localhost:5432/fastapi_db"
```

Run the DB migrations

``` bash
alembic upgrade head
```

Run the FastAPI app

``` bash
uvicorn src.main:app --reload
```

## Testing approach

Local testing with testcontainers  [testcontainers](https://testcontainers.com/)

### Unit testing:

- Pytest with testcontainers ( Postgres 17 created in tests/conftest.py)

### Semi-automated testing:

1. Postman collection
2. Bash script
3. Python script

### Install dependencies for testing

``` bash
pip install -r requirements/test.txt

pytest tests
```

### Postman collection

File FastApi Template.postman_collection.json

### Bash script for API testing

``` bash
chmod +x test_api.sh
test_api.sh
```

### Python script for API testing

```python
pytest test_api.py
```

## Upgrading dependencies in requirements/base.txt, requirements/dev.txt, requirements/prod.txt

``` bash
pip install pur

pur -r requirements/base.txt
pur -r requirements/dev.txt
pur -r requirements/prod.txt
```

## Activation Python 3.11 virtual environment with Conda

``` bash
conda create -n venv311 python=3.11
conda activate venv311
```

## Deactivation Python 3.11 virtual environment with Conda

``` bash
conda deactivate
```
