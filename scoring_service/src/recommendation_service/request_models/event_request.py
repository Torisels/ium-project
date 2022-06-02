from pydantic import BaseModel
from enum import Enum


class EventType(Enum):
    Buy = 1
    View = 2


class EventRequest(BaseModel):
    user_id: int
    product_id: int
    event_type: EventType
