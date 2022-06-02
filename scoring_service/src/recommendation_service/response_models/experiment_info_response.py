from typing import List, Dict
from pydantic import BaseModel


class ExperimentInfoResponse(BaseModel):
    experiment_id: int
    experiment_name: str
    model_ids: List[str]
    user_ids: Dict[str, List[int]]
    type: str
