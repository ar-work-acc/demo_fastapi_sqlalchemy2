# FastAPI + SQLAlchemy 2.0 Demo Project

This is a demo project for FastAPI + SQLAlchemy 2.0, which can serve as a
template for your project. ASGI is used, so you should use asynchronous settings
in Alembic (initialization and database URLs), and also in the database URLs in
Python code (asyncpg).

Note: Celery is added for demonstrating its usage, but it does not work well
with asynchronous code and should be replaced with other services.

## Running the Application (Summary)

To start your app, run:

```bash
cd src
alembic upgrade head  # create tables
python -m core.initialize_data  # add initial users

uvicorn main:app --reload  # start FastAPI app
```

Starting/stopping Celery:

```bash
./celery.sh start  # start Celery workers
./celery.sh stop  # stop workers
```

Run tests:

```bash
./run_pytest.sh
```

Checking mypy issues:

```bash
mypy --disallow-untyped-defs src test
```

Access FastAPI's Swagger UI page at
[http://localhost:8000/docs](http://localhost:8000/docs).

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

To run all tests:

```bash
./run_pytest.sh
```

Or to run specific tests:

```bash
./run_pytest.sh -k <your_condition>
```

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

## Celery & Redis

Note: For better async support, you should check other available options (e.g.,
[FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)).
Celery by default is not designed to be used with async operations.

[Install the packages first](https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-redis-result-backend):

```bash
pip install celery[redis]
```

Update Redis CLI to the latest version (or you can't use the `-u` URI option):

```bash
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make redis-cli
sudo cp src/redis-cli /usr/local/bin/
```

Using the URI
[`redis://user:password@host:port/dbnum`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-redis-result-backend)
to connect to Redis:

```bash
$ redis-cli -u redis://admin:pw2024@localhost:6379/0
localhost:6379> ping
PONG
```

Using
[`AUTH username password`](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/):
to authenticate instead:

```bash
$ redis-cli
127.0.0.1:6379> ping
(error) NOAUTH Authentication required.
127.0.0.1:6379> AUTH admin pw2024
OK
127.0.0.1:6379> ping
PONG
```

Or simply specify the username and password in command line arguments:

```bash
redis-cli --user admin --pass pw2024
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.
127.0.0.1:6379> ping
PONG
```

Note: Mocking is used for Celery task tests, so you don't need to start any
worker for the tests.

### Starting and Stopping Celery

Use the script to start and stop Celery:

```bash
./celery.sh start
./celery.sh stop
```

### Starting a Worker

Run:

```bash
cd src
celery -A task_queue.tasks worker -Q default --loglevel=DEBUG
```

Note: For more complex routing, see
[Routing Tasks](https://docs.celeryq.dev/en/stable/userguide/routing.html)
