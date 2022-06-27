from datetime import datetime

from pydantic import BaseModel

from models import Status


class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    product_id: int
    quantity: int


class OrderOut(OrderBase):
    id: int
    price: float
    fee: float
    total: float
    quantity: int
    status: Status
    created_at: datetime

    class Config:
        orm_mode = True
