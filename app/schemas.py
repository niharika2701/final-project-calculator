from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import EmailStr
from app.calculations import OperationType


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    model_config = {"from_attributes": True}


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: OperationType
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def no_division_by_zero(self) -> "CalculationCreate":
        if self.type == OperationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: OperationType
    result: float
    user_id: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}

class ReportRead(BaseModel):
    """
    Response schema for GET /reports/summary.
    Contains aggregate stats + the 5 most recent calculations.
    """
    total_calculations: int
    by_operation: Dict[str, int]
    average_a: float
    average_b: float
    average_result: float
    most_recent: List[CalculationRead]