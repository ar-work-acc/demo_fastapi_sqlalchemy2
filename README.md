# FastAPI + SQLAlchemy 2.0 Demo Project

This is a demo project for FastAPI + SQLAlchemy 2.0, which can serve as a
template for your project. ASGI is used, so you should use asynchronous settings
in Alembic (initialization and database URLs), and also in the database URLs in
Python code (asyncpg).

## Dependencies

Install required packages (`fastapi[all]` includes uvicorn):

```bash
pip install "fastapi[all]"
pip install pydantic

pip install SQLAlchemy
pip install alembic

pip install "python-jose[cryptography]"
pip install bcrypt

pip install asyncpg

pip install pytest
pip install pytest-cov
```

Installing additional utilities:

```bash
pip install httpie
pip install ipython
```

Install mypy and
[SQLAlchemy mypy extension](https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html#installation):

```bash
pip install mypy
pip install sqlalchemy[mypy]
```

Mypy settings ("mypy.ini"):

```ini
[mypy]
python_version = 3.11
plugins = sqlalchemy.ext.mypy.plugin
mypy_path = src/
```

## Run

To start your app, run:

```bash
cd src
uvicorn main:app --reload
```

You can access the FastAPI Swagger UI page at
[http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints

First, run "initialize_data.py" to create initial users; an admin and a normal
user are created to test different levels of authorization:

```bash
python -m core.initialize_data
```

Login and get the JWT token with HTTPie (form):

```bash
http -v --form POST http://localhost:8000/api/v1/auth/login username='admin@meowfish.org' password='pw2023'
http -v --form POST http://localhost:8000/api/v1/auth/login username='alice@meowfish.org' password='666'
```

To access a protected endpoint, include the JWT token in the Authorization
header as:

```bash
http http://localhost:8000/api/v1/auth/employee-info 'Authorization:Bearer YOUR_JWT_TOKEN'
http http://localhost:8000/api/v1/auth/user-info 'Authorization:Bearer YOUR_JWT_TOKEN'
```

Create a product (only managers/admins can do that):

```bash
http POST http://127.0.0.1:8000/products/ \
Content-Type:application/json \
product_name="phone" \
unit_price:=300.0 \
units_in_stock:=5 \
type:=0 \
'Authorization:Bearer YOUR_TOKEN'
```

To access product details, you need to log in and acquire a token first.

```bash
http 'http://127.0.0.1:8000/products/1' \
'Authorization:Bearer YOUR_TOKEN'
```

## CORS

For FastAPI (Starlette), both headers are needed for
[CORS preflight requests](https://www.starlette.io/middleware/#cors-preflight-requests):
These are any OPTIONS request with Origin and
[Access-Control-Request-Method](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Request-Method)
headers. In this case, the middleware will intercept the incoming request and
respond with appropriate CORS headers, and either a 200 or 400 response for
informational purposes.

## Gunicorn

To start multiple workers with Gunicorn (note that in production, you should
just handle this with K8s):

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker

Run these commands to build the container image and run it:

```bash
docker build -t fastapi-shop .
docker run -d --name shop --network host fastapi-shop
docker logs -f shop
```

Note that the container uses the "prod" database, which needs to be initialized
first (you can initialize "dev" and rename it to "prod").

## Testing

Logs are written to "pytest.log"; you can adjust the settings in "pytest.ini".

## Coverage problems

SQLAlchemy uses Greenlet, and FastAPI uses threads when using synchronous
routes. You have to specify the concurrency option
[`.coveragerc`](https://coverage.readthedocs.io/en/7.5.1/config.html#run-concurrency):

```txt
[run]
concurrency =
  greenlet
  thread
```

You will also want to exclude these lines from the coverage report:

```txt
[report]
exclude_also =
    if TYPE_CHECKING:
    if __name__ == "__main__":
```

## TODO

1. Full documentation for Swagger UI.
2. CORS
