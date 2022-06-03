from recommendation_service.utils import get_folder_path
from recommendation_service.config import settings
from typing import List
import pandas as pd
import json
from recommendation_service.response_models.experiment_info_response import ExperimentInfoResponse
from recommendation_service.response_models.experiment_result_model import ExperimentResultResponse
from recommendation_service.services.models_service import ModelsService
from recommendation_service.request_models.event_request import EventType
from pathlib import Path
import pickle


class ExperimentsLog:
    def __init__(self, exp_id: int, models):
        self.experiment_id = exp_id
        self.models = models
        self.data = {m: {} for m in self.models}

    def log_recommendations(self, model_id: str, user_id: int, product_ids: List[int]):
        if user_id in self.data[model_id]:
            self.data[model_id][user_id]["recommended"].update(product_ids)
        else:
            self.data[model_id][user_id] = self.create_empty_user_dict()
            self.data[model_id][user_id]["recommended"].update(product_ids)

    def log_buy(self, model_id, user_id, product_id):
        product_id = [product_id]
        if user_id in self.data[model_id]:
            self.data[model_id][user_id]["bought"].update(product_id)
        else:
            self.data[model_id][user_id] = self.create_empty_user_dict()
            self.data[model_id][user_id]["bought"].update(product_id)

    def log_view(self, model_id, user_id, product_id):
        product_id = [product_id]
        if user_id in self.data[model_id]:
            self.data[model_id][user_id]["viewed"].update(product_id)
        else:
            self.data[model_id][user_id] = self.create_empty_user_dict()
            self.data[model_id][user_id]["viewed"].update(product_id)

    def generate_report(self):
        result = {m: {} for m in self.data.keys()}

        for m, data in self.data.items():
            total_recommendations = sum([len(d["recommended"]) for d in data.values()])
            buy_hits = 0
            view_hits = 0
            for uid, info in data.items():
                buy_hits += len(info["recommended"].intersection(info["bought"]))
                view_hits += len(info["recommended"].intersection(info["viewed"]))

            result[m]["total_recommendations"] = total_recommendations
            result[m]["view_hits"] = view_hits
            result[m]["buy_hits"] = buy_hits
            result[m]["view_ratio"] = view_hits / total_recommendations if total_recommendations > 0 else "N/A"
            result[m]["buy_ratio"] = buy_hits / total_recommendations if total_recommendations > 0 else "N/A"

        return result

    @staticmethod
    def create_empty_user_dict():
        return {
            "recommended": set(),
            "bought": set(),
            "viewed": set(),
        }


class ExperimentsService:
    def __init__(self, models_service: ModelsService):
        self.models_service = models_service
        data_folder = get_folder_path(settings.experiments_data_path)
        with open(data_folder / "experiments.json") as f:
            self.experiments = json.load(f)

        self.users_map = {}
        for ex in self.experiments:
            d = {}
            for m in ex["models"]:
                for user_id in ex["user_sets"][m]:
                    d[user_id] = m
            self.users_map[ex["id"]] = d

        self.experiments_log_folder = data_folder / Path("logs")
        self.current_experiment_file = self.experiments_log_folder / Path(f"{settings.current_experiment_id}.pickle")
        self.current_experiment = self.get_experiment_by_id(settings.current_experiment_id)

        if not self.current_experiment_file.exists():
            l = ExperimentsLog(self.current_experiment["id"], self.current_experiment["models"])
            self._save_experiments_log(l)

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

    def log_event(self, user_id, product_id, event_type: EventType):
        model_id = self.users_map[settings.current_experiment_id][user_id]
        l = self._load_experiments_log()
        if event_type == EventType.Buy:
            l.log_buy(model_id, user_id, product_id)
        elif event_type == EventType.View:
            l.log_view(model_id, user_id, product_id)
        self._save_experiments_log(l)

    def get_current_experiment(self) -> ExperimentInfoResponse:
        ex = self.current_experiment
        return ExperimentInfoResponse(experiment_id=ex["id"], experiment_name=ex["name"],
                                      model_ids=ex["models"], user_ids=ex["user_sets"], type=ex["type"])

    def clear_current_log(self):
        l = ExperimentsLog(self.current_experiment["id"], self.current_experiment["models"])
        self._save_experiments_log(l)

    def get_recommendations(self, user_id: int, experiment_id: int) -> List[int]:
        if user_id not in self.users_map[experiment_id]:
            return []
        model_id = self.users_map[experiment_id][user_id]
        recommendations = self.models_service.recommend(model_id, user_id)
        self._handle_online_recommendation(experiment_id, model_id, user_id, recommendations)
        return recommendations

    def _handle_online_recommendation(self, experiment_id, model_id, user_id, recommendations):
        if not self.get_experiment_by_id(experiment_id)["type"] == "online":
            return
        log: ExperimentsLog = self._load_experiments_log()
        log.log_recommendations(model_id, user_id, recommendations)
        self._save_experiments_log(log)

    def _load_experiments_log(self, experiment_id=settings.current_experiment_id) -> ExperimentsLog:
        with open(self.experiments_log_folder / f"{experiment_id}.pickle", "rb") as f:
            return pickle.load(f)

    def _save_experiments_log(self, experiments_log):
        with open(self.experiments_log_folder / f"{experiments_log.experiment_id}.pickle", "wb") as f:
            pickle.dump(experiments_log, f)

    def get_accuracy(self, experiment_id) -> ExperimentResultResponse:
        exp = self.get_experiment_by_id(experiment_id)

        if exp["type"] == "offline":
            results = self._process_offline_experiment(exp)
        else:
            results = self._process_online_experiment(exp)
        return ExperimentResultResponse(experiment_id=exp["id"], experiment_name=exp["name"], type=exp["type"],
                                        results=results)

    def _process_offline_experiment(self, exp):
        res = {m: {} for m in exp["models"]}
        for m in exp["models"]:
            res[m]["accuracy"] = self.models_service.offline_results(m, exp["user_sets"][m])

        return res

    def _process_online_experiment(self, exp):
        l = self._load_experiments_log(exp["id"])
        report = l.generate_report()

        return report
