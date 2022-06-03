from recommendation_service.recommendation_ml_models.base_model import BaseModel
from recommendation_service.utils import get_folder_path
from recommendation_service.config import settings
from typing import List
import pandas as pd
import pickle


class BasicRecommendationModel(BaseModel):
    def __init__(self):
        self.name = "basic"

        data_folder = get_folder_path(settings.data_folder_path)
        self.products: pd.DataFrame = self._load_products()
        self.sessions: pd.DataFrame = pd.read_json(data_folder / settings.sessions_data_file, lines=True)
        self.users_views = self._get_users_views()
        self.model = self._load_model()
        self.k = settings.basic_model_recommendations
        self.train_data = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / "train_data.pickle")

        self.test_data = pd.read_pickle(
            get_folder_path(settings.model_data_path) / self.name / "test_data.pickle")

    def recommend(self, user_id: int) -> List[int]:
        return self._get_recommendations(user_id, self.users_views)

    def calculate_offline_accuracy(self, user_ids: List[int]) -> float:
        correct = 0
        for user in user_ids:
            recommendations = self._get_recommendations(user, self.train_data)
            for recommendation in recommendations:
                view = self.test_data.loc[
                    (self.test_data['product_id'] == recommendation) & (self.test_data['user_id'] == user)]['view']
                if view.any():
                    correct += 1

        result = correct / (self.k * len(user_ids))
        return result

    def _load_products(self):
        return pd.read_pickle(get_folder_path(settings.model_data_path) / self.name / "products.pickle")

    def _load_model(self):
        with open(get_folder_path(settings.model_data_path) / self.name / "model.pickle", "rb") as f:
            return pickle.load(f)

    def _get_users_views(self):
        sessions = self.sessions.copy()
        sessions['view'] = sessions['event_type'].map(lambda x: 1 if x == "VIEW_PRODUCT" else 0)
        users_views = sessions.groupby(['user_id', 'product_id'], as_index=False)['view'].sum()
        return users_views

    def _get_product_params(self, product_id):
        ret_product = self.products.loc[self.products["product_id"] == product_id]
        return ret_product.drop(columns="product_id")

    def _get_recommendations(self, user_id, users_views):
        most_viewed = users_views.loc[users_views["user_id"] == user_id].sort_values(by=["view"], ascending=False)
        most_viewed_products = list(most_viewed["product_id"])
        viewed_products = set(most_viewed[most_viewed["view"] > 0.0]["product_id"])

        final_reccomendation = []
        for product in most_viewed_products:
            recommended = self.model.kneighbors(self._get_product_params(product), return_distance=False)

            for recommended_product in recommended[0]:
                recommended_product_id = self.products.iloc[[recommended_product]]['product_id']

                pid = int(recommended_product_id)
                if pid not in viewed_products and pid not in final_reccomendation:
                    final_reccomendation.append(int(recommended_product_id))
                if len(final_reccomendation) == self.k:
                    return final_reccomendation
