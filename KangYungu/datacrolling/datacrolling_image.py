import os
import pathlib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

CSV_PATH = r"C:\Workspaces\skn14-final-2team\KangYungu\dataset\perfume_for_image_with_id.csv"

DESKTOP = pathlib.Path(os.path.expanduser("~")) / "Desktop"
SAVE_DIR = DESKTOP / "perfume_images"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0 (image-downloader)"}

def pick_image_url_from_page(page_url: str) -> str | None:
    try:
        resp = SESSION.get(page_url, timeout=15, headers=HEADERS)
        resp.raise_for_status()
    except:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return urljoin(page_url, og["content"].strip())

    for wrap in soup.select('[class*="swiper"]'):
        img = wrap.find("img", src=True) or wrap.find("img", attrs={"data-src": True})
        if img:
            src = img.get("src") or img.get("data-src")
            return urljoin(page_url, src.strip())

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if not src:
            continue
        if any(tok in src.lower() for tok in ["logo", "icon", "sprite", "placeholder"]):
            continue
        return urljoin(page_url, src.strip())

    return None

def download_image(img_url: str, dest_stem: pathlib.Path) -> pathlib.Path | None:
    """무조건 JPG로 저장"""
    try:
        r = SESSION.get(img_url, timeout=20, headers=HEADERS, stream=True)
        r.raise_for_status()
    except:
        return None

    dest = dest_stem.with_suffix(".jpg")
    try:
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1024 * 64):
                if chunk:
                    f.write(chunk)
    except:
        return None
    return dest

def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8")
    total = len(df)

    for idx, row in df.iterrows():
        pid = int(row["id"])
        url = str(row["detail_url"]).strip()
        print(f"({idx+1}/{total})", end="\r")

        if not url or url.lower() == "nan":
            continue

        img_url = pick_image_url_from_page(url)
        if not img_url:
            continue

        download_image(img_url, SAVE_DIR / f"{pid}")

    print(f"완료")

if __name__ == "__main__":
    main()
