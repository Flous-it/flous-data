from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class ValueType(str, Enum):
    boolean = "boolean"
    money_fixed = "money_fixed"
    money_with_quota = "money_with_quota"
    percentage = "percentage"
    text = "text"


class Category(str, Enum):
    management = "management"
    cards = "cards"
    operations = "operations"
    branch_ops = "branch_ops"
    withdrawals = "withdrawals"
    digital = "digital"
    fx = "fx"
    extras = "extras"


class Feature(BaseModel):
    code: str
    label_it: str
    category: Category
    product_type: str
    value_type: ValueType
    unit: str | None = None
    display_order: int
