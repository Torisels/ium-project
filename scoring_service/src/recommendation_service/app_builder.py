from typing import List
from fastapi import FastAPI, HTTPException
from recommendation_service.models.product_response import Product


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def status():
        return {"project_description": "IUM Recommendation Model"}

    @app.get("/api/health")
    def status():
        return {"status": "healthy"}

    @app.get("/api/version")
    def version():
        return {"version": "1"}

    @app.get("/api/models/{model_id}/recommend/{user_id}", response_model=List[Product])
    async def recommend(model_id: str, user_id: int = 0):
        m = models.get(model_id, None)
        if m is None:
            raise HTTPException(status_code=404, detail="Model not found")

        if not user_exists(user_id, users):
            raise HTTPException(status_code=404, detail="User does not exist in database")

        return [Product(name="Name",
                        description="Opis",
                        category_path="Cat path",
                        rating=5.77,
                        rating_count=123)]

    @app.get("/api/experiments/ab/{model_a}/{model_b}/", response_model=List[Product])
    async def experiment(model_id: str, user_id: int = 0):
        m = models.get(model_id, None)
        if m is None:
            raise HTTPException(status_code=404, detail="Model not found")

        if not user_exists(user_id, users):
            raise HTTPException(status_code=404, detail="User does not exist in database")

        return [Product(name="Name",
                        description="Opis",
                        category_path="Cat path",
                        rating=5.77,
                        rating_count=123)]

    return app
