from datetime import datetime

from pydantic import BaseModel


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


# INTENT: alias_generator + populate_by_name enables the API to accept/return
# camelCase JSON while Python code uses snake_case — single conversion point
# for the entire schema layer.
class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class TimestampedSchema(BaseSchema):
    created_at: datetime | None = None
