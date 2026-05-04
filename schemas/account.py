from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, model_validator


class ProductType(str, Enum):
    current_account = "current_account"
    deposit = "deposit"
    mortgage = "mortgage"
    credit_card = "credit_card"


class ConditionType(str, Enum):
    salary_credit = "salary_credit"
    age_below = "age_below"
    age_above = "age_above"
    min_balance = "min_balance"
    min_monthly_transactions = "min_monthly_transactions"
    student_status = "student_status"
    under_30 = "under_30"
    under_35 = "under_35"


class FeaturePrice(BaseModel):
    condition_type: ConditionType
    condition_value: Decimal | None = None
    price_override: Decimal
    condition_label: str


class AccountFeatureYAML(BaseModel):
    code: str
    value_money: Decimal | None = None
    value_bool: bool | None = None
    value_text: str | None = None
    free_quota: int | None = None
    unit_cost: Decimal | None = None
    percentage: Decimal | None = None
    notes: str | None = None
    conditions: list[FeaturePrice] = []

    @model_validator(mode="after")
    def check_value_type_consistency(self) -> "AccountFeatureYAML":
        populated = [
            f for f in ["value_money", "value_bool", "value_text", "percentage"]
            if getattr(self, f) is not None
        ]
        has_quota = self.free_quota is not None or self.unit_cost is not None
        if len(populated) > 1:
            raise ValueError(
                f"feature {self.code!r}: only one value field may be set, got {populated}"
            )
        if has_quota and self.value_bool is not None:
            raise ValueError(f"feature {self.code!r}: quota fields incompatible with value_bool")
        return self


class Account(BaseModel):
    id: str
    bank: str  # bank slug, resolved to bank_id during build
    name: str
    slug: str
    product_type: ProductType
    source_url: str
    last_updated: str  # ISO date string
    features: list[AccountFeatureYAML] = []
