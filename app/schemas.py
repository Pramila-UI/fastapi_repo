from pydantic import BaseModel , validator
from typing import Optional

class SignUpModel(BaseModel):
    # id : Optional[int]
    username : str
    email : str
    password :str
    is_staff : Optional[bool]
    is_active : Optional[bool]
    

class LoginModel(BaseModel) :
    username : str | None
    password : str
    email : str | None 


class OrderModel(BaseModel):
    # id : Optional[int]
    quantity : int
    order_status : Optional[str] = "PENDING"
    pizza_size : Optional[str] = "SMALL"
    user_id : int

    @validator("quantity")
    def quantity_must_be_greater_than_zero(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

class OrderUpdateModel(BaseModel):
    quantity : int
    pizza_size : Optional[str] = "SMALL"

    @validator("quantity")
    def quantity_must_be_greater_than_zero(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v
