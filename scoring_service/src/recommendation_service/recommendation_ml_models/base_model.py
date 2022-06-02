from abc import ABC, abstractmethod
from typing import List


class BaseModel:
    @abstractmethod
    def recommend(self, user_id: int) -> List[int]:
        pass
