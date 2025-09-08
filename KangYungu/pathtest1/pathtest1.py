# pathtest1/pathtest1.py
import sys
from pathlib import Path

# 루트 추가 (스크립트가 하위폴더에서 실행돼도 루트를 보게 함)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pathtest2.pathtest2 import ping

if __name__ == "__main__":
    print(ping())
