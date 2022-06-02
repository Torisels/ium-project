from recommendation_service.utils import get_folder_path
from recommendation_service.config import settings
from recommendation_service.response_models.product_response import ProductResponse
from typing import List
import pandas as pd
import json
from recommendation_service.response_models.experiment_info_response import ExperimentInfoResponse
from recommendation_service.services.models_service import ModelsService


class ExperimentsService:
    def __init__(self, models_service: ModelsService):
        self.models_service = models_service
        data_folder = get_folder_path(settings.experiments_data_path)
        with open(data_folder / "experiments_online.json") as f:
            self.experiments = json.load(f)

        self.users_map = {}
        for ex in self.experiments:
            d = {}
            for m in ex["models"]:
                for user_id in ex["user_sets"][m]:
                    d[user_id] = m
            self.users_map[ex["id"]] = d

        self.current_experiment = self.get_experiment_by_id(settings.current_experiment_id)

    def get_experiment_by_id(self, exp_id):
        return next((x for x in self.experiments if x["id"] == exp_id), None)

    def experiment_exists(self, experiment_id: int) -> bool:
        return self.get_experiment_by_id(experiment_id) is not None

    def get_experiments(self) -> List[ExperimentInfoResponse]:
        result = []
        for ex in self.experiments:
            experiment_info = ExperimentInfoResponse(experiment_id=ex["id"], experiment_name=ex["name"],
                                                     model_ids=ex["models"], user_ids=ex["user_sets"], type=ex["type"])
            result.append(experiment_info)
        return result

    def get_current_experiment(self) -> ExperimentInfoResponse:
        ex = self.current_experiment
        return ExperimentInfoResponse(experiment_id=ex["id"], experiment_name=ex["name"],
                                      model_ids=ex["models"], user_ids=ex["user_sets"], type=ex["type"])

    def get_recommendations(self, user_id: int, experiment_id: int) -> List[int]:
        model_id = self.users_map[experiment_id][user_id]
        return self.models_service.recommend(model_id, user_id)

    def get_accuracy(self, experiment_id):
        pass
