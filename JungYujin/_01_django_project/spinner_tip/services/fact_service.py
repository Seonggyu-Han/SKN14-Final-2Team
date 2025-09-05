import random
from .facts_repo import FactsRepository

class FactService:
    def __init__(self, repo: FactsRepository | None = None):
        self.repo = repo or FactsRepository()
        self._cache = None

    def get_random_fact(self) -> str:
        if self._cache is None:
            self._cache = self.repo.load()
        return random.choice(self._cache)
    
    def clear_cache(self):
        """캐시를 초기화하여 다음 호출 시 데이터를 다시 로드합니다."""
        self._cache = None