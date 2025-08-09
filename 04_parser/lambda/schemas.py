from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1, description="商品ID")
    product_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., gt=0, le=100)
    unit_price: float = Field(..., gt=0)

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("単価は0より大きい値である必要があります")
        return round(v, 2)


class CustomerInfo(BaseModel):
    customer_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")


class Order(BaseModel):
    order_id: str = Field(..., min_length=1)
    customer: CustomerInfo
    items: list[OrderItem] = Field(..., min_length=1)
    status: OrderStatus = OrderStatus.PENDING
    order_date: datetime = Field(default_factory=datetime.now)
    notes: str | None = Field(None, max_length=500)
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: list[OrderItem]) -> list[OrderItem]:
        if not v:
            raise ValueError('注文には少なくとも1つの商品が必要です')
        return v
    
    def calculate_total(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)