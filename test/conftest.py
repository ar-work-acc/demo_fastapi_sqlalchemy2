from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.initialize_data import init_db
from model import AsyncSessionMaker, Base, engine
from repository.product import create_product
from schema.product import ProductInput


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    """
    Pytest does not natively support running asynchronous test functions,
    so they have to be marked for the AnyIO pytest plugin to pick them up.
    See https://anyio.readthedocs.io/en/stable/testing.html
    """
    return "asyncio"


PRODUCT_DATA = [
    {
        "product_name": "phone",
        "unit_price": 300.0,
        "units_in_stock": 5,
        "type": 0,
    },
    {
        "product_name": "phone screen protector",
        "unit_price": 9.50,
        "units_in_stock": 10,
        "type": 1,
    },
    {
        "product_name": "headphone",
        "unit_price": 25.99,
        "units_in_stock": 10,
        "type": 2,
    },
    {
        "product_name": "digital camera",
        "unit_price": 45.99,
        "units_in_stock": 5,
    },
    {
        "product_name": "memory card 256GB",
        "unit_price": 21.99,
        "units_in_stock": 1,
        "type": 1,
    },
]


# https://docs.python.org/3/library/typing.html#typing.AsyncGenerator
@pytest.fixture(scope="session", autouse=True)
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    This session-scoped fixture resets the database and creates some initial
    users and products at the start of the test suite.
    """
    # drop and re-create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # initialize the database and yield the session
    async with AsyncSessionMaker() as session:
        # create the initial users
        await init_db(session)

        # create some products
        for data in PRODUCT_DATA:
            await create_product(session, ProductInput.model_validate(data))

        yield session
        # clean up code
        # (not required since we're dropping and recreating the tables)
