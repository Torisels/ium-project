from recommendation_service.recommendation_ml_models.base_model import BaseModel
from typing import List

class BasicRecommendationModel(BaseModel):
    def __init__(self):
        self.name = "basic"

    def recommend(self, user_id: int) -> List[int]:
        return [1022,1023]
