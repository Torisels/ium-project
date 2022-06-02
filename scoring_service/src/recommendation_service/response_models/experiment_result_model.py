from typing import List, Dict, Any
from pydantic import BaseModel


class ExperimentResultResponse(BaseModel):
    experiment_id: int
    experiment_name: str
    type: str

    results: Dict[str, Any]
