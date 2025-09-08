from spinner_tip.services.fact_service import FactService
from spinner_tip.services.facts_repo import FactsRepository

def test_random_fact_not_empty():
    svc = FactService(FactsRepository(json_paths=[]))
    fact = svc.get_random_fact()
    assert isinstance(fact, str) and len(fact) > 0
