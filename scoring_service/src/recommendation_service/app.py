import uvicorn
from recommendation_service.app_builder import build_app
from recommendation_service.services.users_service import UsersService
from recommendation_service.services.models_service import ModelsService
from recommendation_service.services.product_service import ProductsService
from recommendation_service.services.experiments_service import ExperimentsService

users_service = UsersService()
models_service = ModelsService()
product_service = ProductsService()
experiments_service = ExperimentsService()
app = build_app(users_service, models_service, product_service, experiments_service)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000)
