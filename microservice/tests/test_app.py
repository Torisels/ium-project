import pytest
from fastapi.testclient import TestClient
from recommendation_service.app_builder import build_app
from recommendation_service.response_models.experiment_result_model import ExperimentResultResponse
from recommendation_service.response_models.product_response import ProductResponse
from recommendation_service.services.users_service import UsersService
from recommendation_service.services.models_service import ModelsService
from recommendation_service.services.product_service import ProductsService
from recommendation_service.services.experiments_service import ExperimentsService
import os


@pytest.fixture(scope="module")
def client():
    os.environ["RUNNING_REMOTE"] = "true"
    users_service = UsersService()
    models_service = ModelsService()
    product_service = ProductsService()
    experiments_service = ExperimentsService(models_service)
    app = build_app(users_service, models_service, product_service, experiments_service)
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_models(client: TestClient):
    response = client.get("/api/recommendation_models")
    assert response.status_code == 200
    assert response.json()["models"] == ["basic", "advanced"]


def test_experiments(client: TestClient):
    response = client.get("/api/experiments")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_experiment_results():
    class ExperimentsServiceMock(ExperimentsService):

        def get_accuracy(self, experiment_id) -> ExperimentResultResponse:
            return ExperimentResultResponse(experiment_id=experiment_id, experiment_name="ab", type="offline",
                                            results={})

    users_service = UsersService()
    models_service = ModelsService()
    product_service = ProductsService()
    experiments_service = ExperimentsServiceMock(models_service)
    app = build_app(users_service, models_service, product_service, experiments_service)
    client = TestClient(app)
    response = client.get("/api/experiments/2/results")
    assert response.json()["experiment_id"] == 2
    assert response.json()["type"] == "offline"
    assert response.json()["experiment_name"] == "ab"


def test_recommendations():
    class ProductsServiceMock(ProductsService):
        def product_from_id(self, product_id: int) -> ProductResponse:
            return ProductResponse(id=123, name="great", category_path="1;3",
                                   rating=5.00,
                                   rating_count=399)

    class ModelsServiceMock(ModelsService):
        def recommend(self, model_id: str, user_id: int):
            return [0, 1, 2, 3, 4]

    users_service = UsersService()
    models_service = ModelsServiceMock()
    product_service = ProductsServiceMock()
    experiments_service = ExperimentsService(models_service)
    app = build_app(users_service, models_service, product_service, experiments_service)
    client = TestClient(app)
    response = client.get("/api/recommendation_models/basic/recommend/102")
    r_obj = response.json()[0]
    assert r_obj["id"] == 123
    assert r_obj["name"] == "great"
    assert r_obj["rating_count"] == 399
