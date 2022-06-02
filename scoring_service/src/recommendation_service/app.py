import os
import uvicorn
from recommendation_service.app_builder import build_app

app = build_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=os.environ.get("MODEL_APP_PORT", 5000))
