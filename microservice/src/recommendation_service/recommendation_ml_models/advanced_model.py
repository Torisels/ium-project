from recommendation_service.recommendation_ml_models.base_model import BaseModel
from recommendation_service.utils import get_folder_path
from recommendation_service.config import settings
import pandas as pd

from typing import List


class AdvancedRecommendationModel(BaseModel):
    def __init__(self):
        self.name = "advanced"
        self.train_set = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / f"train_data.pickle")

        self.test_set = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / f"test_data.pickle")

        self.content_df = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / f"content_df.pickle")
        self.k = settings.advanced_model_recommendations

        self.user_actions = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / f"user_actions.pickle")

    def recommend(self, user_id: int) -> List[int]:
        return self._get_recommendation(user_id, self.user_actions)

    def _get_recommendation(self, user_id, dataset):
        content_df = self.content_df.loc[self.content_df['user_id'] == user_id]
        content_df = content_df.set_index("product_id")
        user_content_df = content_df.sort_values(by="score", ascending=False)
        indices_to_drop = list(
            dataset[(dataset["view_ocurred"] == True) & (dataset["user_id"] == user_id)]["product_id"])
        user_content_df = user_content_df.drop(indices_to_drop)
        return list(user_content_df.head(self.k).index)

    def calculate_offline_accuracy(self, user_ids: List[int]) -> float:
        correct = 0
        for user in user_ids:
            recommendations = self._get_recommendation(user, self.train_set)
            for recommendation in recommendations:
                view_occurred = \
                    self.test_set[(self.test_set['product_id'] == recommendation) & (self.test_set['user_id'] == user)][
                        'view_ocurred']
                if view_occurred.any() and view_occurred.item() == True:
                    correct += 1
        result = correct / (self.k * len(user_ids))
        return result
