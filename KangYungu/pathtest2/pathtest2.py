# pathtest2/pathtest2.py
from pathlib import Path

def ping():
    return f"[pathtest2] __file__={__file__} | cwd={Path().resolve()}"

if __name__ == "__main__":
    print(ping())
