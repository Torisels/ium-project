from recommendation_service.recommendation_ml_models.base_model import BaseModel

from typing import List


class AdvancedRecommendationModel(BaseModel):
    def __init__(self):
        self.name = "advanced"

    def recommend(self, user_id: int) -> List[int]:
        return [1025, 1026]

    def calculate_offline_accuracy(self, user_ids: List[int]) -> float:
        return 99.9
