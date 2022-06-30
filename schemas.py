from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models import Status


class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int


class ProductUpdate(BaseModel):
    name: Optional[str]
    price: Optional[float]
    quantity: Optional[int]


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


class ListOrders(BaseModel):
    data: List[OrderBase]


class ListOrdersOut(BaseModel):
    data: List[OrderOut]
