from abc import ABC, abstractmethod
from typing import List


class BaseModel:
    @abstractmethod
    def recommend(self, user_id: int) -> List[int]:
        pass

    @abstractmethod
    def calculate_offline_accuracy(self, user_ids: List[int]) -> float:
        pass
