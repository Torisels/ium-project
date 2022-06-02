from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    description: Union[str, None] = None
    category_path: Union[str, None] = None
    rating: float
    rating_count: int
