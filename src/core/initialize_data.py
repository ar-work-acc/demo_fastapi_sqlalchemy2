import asyncio
import logging
from datetime import date, timedelta
from typing import Callable

from sqlalchemy import Engine, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_password_hash
from core.config import PROJECT_SETTINGS
from model import AsyncSessionMaker, Employee

# to directly print out the logs (not to a file),
# use a separate logging config here:
logging.basicConfig(
    encoding="utf-8",
    level=PROJECT_SETTINGS.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s][%(name)s]: %(message)s",
)
logger = logging.getLogger(__name__)


async def check_and_create_user(
    session: AsyncSession,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    is_manager: bool,
    hire_date: date,
) -> None:
    exists_criteria = (
        select(Employee.employee_id).filter_by(email=email).exists()
    )
    stmt = select(exists_criteria)
    result = await session.scalar(stmt)

    if result:
        logger.debug(f"User ({email}) already exists! Skipping.")
        return
    else:
        logger.debug(f"Create a new user for: {email}!")
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=get_password_hash(password),
            is_manager=is_manager,
            hire_date=hire_date,
        )
        session.add(employee)
        await session.commit()


async def init_db(session: AsyncSession) -> None:
    """Initialize the database with two users:
    one manager (admin) and one normal user.
    """
    engine = session.get_bind()
    if isinstance(engine, Engine):
        db_url = engine.url
        logging.debug(f"*** Initializing database: {db_url} ***")

    #  create admin user
    await check_and_create_user(
        session,
        first_name="Louis",
        last_name="Huang",
        email=PROJECT_SETTINGS.ADMIN_USERNAME,
        password=PROJECT_SETTINGS.ADMIN_PASSWORD,
        is_manager=True,
        hire_date=date.today() - timedelta(days=30),
    )

    # create another normal user
    await check_and_create_user(
        session,
        first_name="Alice",
        last_name="Maxwell",
        email=PROJECT_SETTINGS.USER_USERNAME,
        password=PROJECT_SETTINGS.USER_PASSWORD,
        is_manager=False,
        hire_date=date.today(),
    )


async def start_async_session_to_run_async_function(func: Callable) -> None:
    async with AsyncSessionMaker() as session:
        await func(session)


if __name__ == "__main__":
    asyncio.run(start_async_session_to_run_async_function(init_db))
