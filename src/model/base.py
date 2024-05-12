from __future__ import annotations  # PEP-563

import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import Numeric, String
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

from core.config import PROJECT_SETTINGS

DATABASE_URL = str(PROJECT_SETTINGS.SQLALCHEMY_DATABASE_URL)

# use create_async_engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# async_sessionmaker: a factory for new AsyncSession objects.
# expire_on_commit - don't expire objects after transaction commit
AsyncSessionMaker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    """
    Declarative base with Python dataclass integration.

    AsyncAttrs: to "await" for lazy loaded attributes
    """

    pass


# Define re-usable types:
int_pk = Annotated[
    int,
    mapped_column(
        primary_key=True,
    ),
]
date_auto = Annotated[
    datetime.date,
    mapped_column(
        default=datetime.date.today,
    ),
]
timestamp_auto = Annotated[
    datetime.datetime,
    mapped_column(
        default=datetime.datetime.now,
    ),
]
str_127 = Annotated[
    str,
    mapped_column(
        String(127),
    ),
]
str_255 = Annotated[
    str,
    mapped_column(
        String(255),
    ),
]
num_12_2 = Annotated[
    Decimal,
    mapped_column(
        Numeric(12, 2),
    ),
]
