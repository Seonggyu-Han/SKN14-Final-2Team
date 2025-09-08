import json
from pathlib import Path
from typing import List

# 1) 코드 내 리스트(업로드된 perfume_facts.py)를 우선 사용
try:
    import sys
    from pathlib import Path
    # 상위 디렉토리의 perfume_facts.py를 import
    parent_dir = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(parent_dir))
    from perfume_facts import perfume_facts as _facts  # 코드 리스트
except Exception as e:
    print(f"Failed to import perfume_facts: {e}")
    _facts = None

DEFAULT_JSON_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "perfume_facts.json",  # 루트에 둘 때
    Path.cwd() / "perfume_facts.json",
]

class FactsRepository:
    """
    데이터 소스 추상화:
    - 우선순위: 코드 리스트 → JSON 파일 → 최소 폴백
    """
    def __init__(self, json_paths: list[Path] | None = None):
        self.json_paths = json_paths or DEFAULT_JSON_PATHS

    def load(self) -> List[str]:
        if _facts:
            return list(_facts)

        for p in self.json_paths:
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    return [str(x) for x in data]

        # 폴백 한 줄
        return ["향의 첫인상은 톱 노트, 그 다음이 미들 노트, 마지막이 베이스 노트입니다."]
