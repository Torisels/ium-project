from typing import List, Union

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    category_path: Union[str, None] = None
    rating: float
    rating_count: int


