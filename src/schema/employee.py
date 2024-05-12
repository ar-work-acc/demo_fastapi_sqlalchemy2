from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int
    email: str
    first_name: str
    last_name: str
    is_manager: bool
