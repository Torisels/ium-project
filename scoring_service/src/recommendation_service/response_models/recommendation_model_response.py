from pydantic import BaseModel
from typing import List


class RecommendationModel(BaseModel):
    models: List[str]
