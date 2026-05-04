from __future__ import annotations

import re
from pydantic import BaseModel, field_validator


class Bank(BaseModel):
    id: str
    name: str
    slug: str
    bic: str
    abi: str
    mec_code: str
    country: str = "IT"

    @field_validator("abi", "mec_code")
    @classmethod
    def validate_numeric_code(cls, v: str) -> str:
        if not re.match(r"^\d{5}$", v):
            raise ValueError("must be exactly 5 digits")
        return v

    @field_validator("bic")
    @classmethod
    def validate_bic(cls, v: str) -> str:
        # 8-char (AAAABBCC) or 11-char (AAAABBCCDDD) BIC
        if not re.match(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$", v):
            raise ValueError(f"invalid BIC format: {v!r}")
        return v
