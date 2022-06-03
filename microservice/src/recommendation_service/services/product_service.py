from recommendation_service.utils import get_folder_path
from recommendation_service.config import settings
from recommendation_service.response_models.product_response import ProductResponse
from typing import List
import pandas as pd


class ProductsService:
    def __init__(self):
        data_folder = get_folder_path(settings.data_folder_path)
        data_file = settings.products_data_file
        self.products: pd.DataFrame = pd.read_json(data_folder / data_file, lines=True)

    def product_from_id(self, product_id: int) -> ProductResponse:
        p = self.products.loc[self.products["product_id"] == product_id].to_dict(orient="records")[0]
        return ProductResponse(id=p["product_id"], name=p["product_name"], category_path=p["category_path"],
                               rating=p["user_rating"],
                               rating_count=p["user_rating_count"])

    def products_from_ids(self, product_ids: List[int]) -> List[ProductResponse]:
        return [self.product_from_id(pid) for pid in product_ids]
