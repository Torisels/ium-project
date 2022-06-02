from typing import List
from fastapi import FastAPI, HTTPException
from recommendation_service.response_models.product_response import ProductResponse
from recommendation_service.response_models.experiment_info_response import ExperimentInfoResponse
from recommendation_service.response_models.recommendation_model_response import RecommendationModel
from recommendation_service.services.users_service import UsersService
from recommendation_service.services.models_service import ModelsService
from recommendation_service.services.product_service import ProductsService
from recommendation_service.services.experiments_service import ExperimentsService
from recommendation_service.utils import get_api_version
from recommendation_service.config import settings
from recommendation_service.request_models.event_request import EventRequest


def build_app(users_service: UsersService, models_service: ModelsService, product_service: ProductsService,
              experiments_service: ExperimentsService) -> FastAPI:
    app = FastAPI()
    api_version = get_api_version(settings.version_file_path)

    @app.get("/")
    def status():
        return {"project_description": "IUM Recommendation Model"}

    @app.get("/health")
    def status():
        return {"status": "healthy"}

    @app.get("/api/version")
    def version():
        return {"version": api_version}

    @app.get("/api/recommendation_models", response_model=RecommendationModel)
    async def models():
        m = models_service.get_models()
        response = RecommendationModel(models=m)
        return response

    @app.get("/api/recommendation_models/{model_id}/recommend/{user_id}", response_model=List[ProductResponse])
    async def recommend(model_id: str, user_id: int = 0):
        if not models_service.model_exists(model_id):
            raise HTTPException(status_code=404, detail="Model not found")

        if not users_service.user_exists(user_id):
            raise HTTPException(status_code=404, detail="User does not exist in database")

        recommendations = models_service.recommend(model_id, user_id)

        return product_service.products_from_ids(recommendations)

    @app.get("/api/experiments/{experiment_id}/results", response_model=List[ProductResponse])
    async def experiment_results(experiment_id: int):
        if not experiments_service.experiment_exists(experiment_id):
            raise HTTPException(status_code=404, detail="Experiment not found")

        return [ProductResponse(name="Name",
                                description="Opis",
                                category_path="Cat path",
                                rating=5.77,
                                rating_count=123)]

    @app.get("/api/experiments/{experiment_id}/recommend/{user_id}", response_model=List[ProductResponse])
    async def recommend_from_experiment(experiment_id: int, user_id: int):
        if not experiments_service.experiment_exists(experiment_id):
            raise HTTPException(status_code=404, detail="Experiment not found")
        if not users_service.user_exists(user_id):
            raise HTTPException(status_code=404, detail="User does not exist in database")

        recommendations = experiments_service.get_recommendations(user_id, experiment_id)
        return product_service.products_from_ids(recommendations)

    @app.get("/api/experiments", response_model=List[ExperimentInfoResponse])
    async def list_experiments():
        return experiments_service.get_experiments()

    @app.get("/api/experiments/online/current", response_model=ExperimentInfoResponse)
    async def list_current_experiment():
        return experiments_service.get_current_experiment()

    @app.post("/api/experiments/log/viewed")
    async def register_event(event: EventRequest):
        return event

    return app
