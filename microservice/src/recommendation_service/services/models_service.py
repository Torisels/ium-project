from typing import List, Dict
from recommendation_service.recommendation_ml_models.basic_model import BasicRecommendationModel
from recommendation_service.recommendation_ml_models.base_model import BaseModel
from recommendation_service.recommendation_ml_models.advanced_model import AdvancedRecommendationModel


class ModelsService:
    def __init__(self):
        models = [BasicRecommendationModel(), AdvancedRecommendationModel()]

        self.models: Dict[str, BaseModel] = {k.name: k for k in models}

    def get_models(self) -> List[str]:
        return list(self.models.keys())

    def model_exists(self, model_id: str) -> bool:
        return model_id in self.models

    def recommend(self, model_id: str, user_id: int) -> List[int]:
        return self.models[model_id].recommend(user_id)

    def offline_results(self, model_id: str, users: List[int]):
        return self.models[model_id].calculate_offline_accuracy(users)
