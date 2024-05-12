
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from model import Employee


async def get_employee_by_email(
        session: AsyncSession,
        email: str,
) -> Employee | None:
    stmt = (
        select(Employee)
        .where(Employee.email == email)
        .options(load_only(
            Employee.employee_id,
            Employee.email,
            Employee.first_name,
            Employee.last_name,
            Employee.is_manager,
            Employee.password_hash,
        ))
    )
    result = await session.scalar(stmt)

    return result
