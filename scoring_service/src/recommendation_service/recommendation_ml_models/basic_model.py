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

    def recommend(self, user_id: int) -> List[int]:
        return self._get_recommendations(user_id)

    def _load_products(self):
        return pd.read_pickle(get_folder_path(settings.model_data_path) / self.name / f"products_{self.name}.pickle")

    def _load_model(self):
        with open(get_folder_path(settings.model_data_path) / self.name / f"model_{self.name}.pickle", "rb") as f:
            return pickle.load(f)

    def _get_users_views(self):
        sessions = self.sessions.copy()
        sessions['view'] = sessions['event_type'].map(lambda x: 1 if x == "VIEW_PRODUCT" else 0)
        users_views = sessions.groupby(['user_id', 'product_id'], as_index=False)['view'].sum()
        return users_views

    def _get_product_params(self, product_id):
        ret_product = self.products.loc[self.products["product_id"] == product_id]
        return ret_product.drop(columns="product_id")

    def _get_recommendations(self, user_id):
        most_viewed = self.users_views.loc[self.users_views["user_id"] == user_id].sort_values(by=["view"],
                                                                                               ascending=False)
        viewed_products = list(most_viewed["product_id"])
        final_recommendation = []
        for product in viewed_products:
            distances, recommended = self.model.kneighbors(self._get_product_params(product), n_neighbors=self.k)
            for recommended_product in recommended[0]:
                recommended_product_id = self.products.iloc[[recommended_product]]['product_id']
                if int(recommended_product_id) not in viewed_products:
                    final_recommendation.append(int(recommended_product_id))
                if len(final_recommendation) == self.k:
                    return final_recommendation
