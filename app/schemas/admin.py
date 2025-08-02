from typing import Any, Literal

from models.user import User
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

protected_fields = {"password","id"}


class ModifyUser(BaseModel):
    userid: str
    attr: str
    attr_type: Literal["bool", "int", "str"]
    value: Any

    @field_validator("attr")
    @classmethod
    def check_attr(cls, v):
        if v in protected_fields:
            raise ValueError(f"Attribute '{v}' is protected and cannot be modified.")

        column_names = [col.name for col in User.__table__.columns]
        if v not in column_names:
            raise ValueError(f"Invalid attribute '{v}'. Must be one of {column_names}.")

        return v

    @field_validator("value")
    @classmethod
    def check_value(cls, v, info: ValidationInfo):
        expected_type = info.data.get("attr_type")  # "int", "str", "bool"

        try:
            match expected_type:
                case "int":
                    return int(v)
                case "bool":
                    if isinstance(v, str):
                        return v.lower() in ("true", "1")
                    return bool(v)
                case "str":
                    return str(v)
        except Exception:
            raise ValueError(f"Value '{v}' is not valid for type '{expected_type}'.")

        raise ValueError(f"Unsupported type '{expected_type}' specified.")  # fallback
