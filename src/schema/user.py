from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    """
    User model for the JWT token.

    sub: subject,
    exp: expiration time,
    """

    sub: str  # same as email here
    exp: datetime

    first_name: str
    last_name: str | None = None
    is_manager: bool = False
