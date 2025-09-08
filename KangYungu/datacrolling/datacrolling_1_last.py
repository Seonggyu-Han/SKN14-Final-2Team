import re
import csv
import time
import sys
from pathlib import Path
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

BASE = "https://www.bysuco.com"

ROOT_DIR = Path(__file__).resolve().parent
OUT_CSV = ROOT_DIR / "bysuco_1_all.csv"

PRICE_NODE_SEL = "strong.discountPrice"
SIZE_WRAP_SEL = ".productOptionBtnWrap"
SIZE_BTN_LIST_SEL = ".optionBtn"
ACTIVE_CLASS = "checked"
SOLDOUT_CLASS_CAND = ("soldout", "disabled")

PAGINATION_WRAP_SEL = "div.ui.pagination.first.menu"
PAGE_ITEM_SEL = f"{PAGINATION_WRAP_SEL} a[type='pageItem']"

WON_RE = re.compile(r"(\d[\d,]{2,})\s*원")
SIZE_NORM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(ml|mL|ML)", re.IGNORECASE)

def tidy_description(text: str, mode: str = "escape_newlines") -> str:
    if not text:
        return ""
    text = re.sub(r"\r\n|\r|\n", "\n", text)
    if mode == "escape_newlines":
        text = text.replace("\n", r"\n")
    elif mode == "remove_newlines":
        text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text

def norm_price_text(txt: str):
    if not txt:
        return None
    m = WON_RE.search(txt)
    digits = m.group(1).replace(",", "") if m else re.sub(r"[^\d]", "", txt)
    return int(digits) if digits.isdigit() else None

def setup_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,2200")
    opts.add_argument("--lang=ko-KR")
    opts.add_experimental_option("prefs", {"profile.default_content_setting_values.images": 2})
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(40)
    return driver

def get_text(el):
    try:
        t = (el.text or "").strip()
        return t if t else (el.get_attribute("textContent") or "").strip()
    except:
        return ""

def read_price_now(driver, timeout=3.0):
    end = time.time() + timeout
    last = ""
    while time.time() < end:
        try:
            node = driver.find_element(By.CSS_SELECTOR, PRICE_NODE_SEL)
            txt = get_text(node)
            last = txt or last
            price = norm_price_text(txt)
            if price is not None:
                return price
        except:
            pass
        time.sleep(0.08)
    return norm_price_text(last)

def wait_price_text_change(driver, prev_text: str, timeout=1.5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            cur = get_text(driver.find_element(By.CSS_SELECTOR, PRICE_NODE_SEL))
            if cur and cur != prev_text:
                return True
        except:
            pass
        time.sleep(0.06)
    return False

def click_js(driver, el):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.05)
        try:
            el.click()
        except:
            driver.execute_script("arguments[0].click();", el)
    except:
        pass

def is_btn_soldout(btn):
    try:
        cls = (btn.get_attribute("class") or "").lower()
        if any(c in cls for c in SOLDOUT_CLASS_CAND):
            return True
        if (btn.get_attribute("disabled") or
            str(btn.get_attribute("aria-disabled")).lower() == "true"):
            return True
    except:
        pass
    return False

def is_btn_checked(btn):
    try:
        cls = (btn.get_attribute("class") or "").lower()
        return ACTIVE_CLASS in cls
    except:
        return False

def normalize_size_label(label: str) -> str:
    if not label:
        return ""
    m = SIZE_NORM_RE.search(label)
    if m:
        num, unit = m.group(1), "ml"
        return f"{num}{unit}"
    digits = re.sub(r"[^\d]", "", label)
    return f"{digits}ml" if digits else label.strip().lower()

def pick_first_visible_wrap(driver):
    wraps = driver.find_elements(By.CSS_SELECTOR, SIZE_WRAP_SEL)
    for w in wraps:
        try:
            if w.is_displayed() and w.size.get("height", 0) > 0 and w.size.get("width", 0) > 0:
                return w
        except:
            continue
    return None

def collect_detail(driver, detail_url: str):
    driver.get(detail_url)
    wait = WebDriverWait(driver, 10)

    try:
        brand = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.tit"))).get_attribute("textContent").strip()
    except:
        brand = ""
    try:
        name = driver.find_element(By.CSS_SELECTOR, "h3.desc.ellipsisTwo").text.strip()
    except:
        try:
            name = driver.find_element(By.CSS_SELECTOR, ".detailWrap h3.desc, .detailWrap .desc.ellipsisTwo").text.strip()
        except:
            name = ""
    try:
        description = driver.find_element(By.CSS_SELECTOR, "div.descWrap").text.strip()
    except:
        description = ""

    description = tidy_description(description, mode="escape_newlines")

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRICE_NODE_SEL)))
    except:
        pass
    rep_price = read_price_now(driver, timeout=2.0)

    rows = []

    wrap = pick_first_visible_wrap(driver)
    if not wrap:
        rows.append({
            "brand": brand, "name": name, "size_ml": "",
            "price_krw": rep_price,
            "detail_url": detail_url, "description": description,
        })
        return rows

    btns = wrap.find_elements(By.CSS_SELECTOR, SIZE_BTN_LIST_SEL)
    seen_labels = set()

    for idx in range(len(btns)):
        btns = wrap.find_elements(By.CSS_SELECTOR, SIZE_BTN_LIST_SEL)
        if idx >= len(btns):
            break
        btn = btns[idx]
        label = get_text(btn) or ""
        if not label:
            try:
                label = get_text(btn.find_element(By.CSS_SELECTOR, "i"))
            except:
                label = ""
        label = label.strip()
        norm_label = normalize_size_label(label)

        if norm_label in seen_labels:
            continue
        seen_labels.add(norm_label)

        if is_btn_soldout(btn):
            continue  # 품절은 스킵

        prev_price_text = ""
        price_nodes = driver.find_elements(By.CSS_SELECTOR, PRICE_NODE_SEL)
        if price_nodes:
            prev_price_text = get_text(price_nodes[0])

        click_js(driver, btn)

        end = time.time() + 1.0
        got_checked = is_btn_checked(btn)
        while (not got_checked) and time.time() < end:
            time.sleep(0.06)
            btns_after = wrap.find_elements(By.CSS_SELECTOR, SIZE_BTN_LIST_SEL)
            if idx < len(btns_after):
                btn = btns_after[idx]
            got_checked = is_btn_checked(btn)

        if not got_checked:
            continue  # 선택 불가 시 스킵

        _ = wait_price_text_change(driver, prev_price_text, timeout=1.2)
        price = read_price_now(driver, timeout=1.5) or rep_price

        rows.append({
            "brand": brand, "name": name, "size_ml": norm_label or label,
            "price_krw": price,
            "detail_url": detail_url, "description": description,
        })
        time.sleep(0.08)

    dedup = {}
    for r in rows:
        key = (r["brand"], r["name"], r["size_ml"])
        if key not in dedup:
            dedup[key] = r
        else:
            if (not dedup[key]["price_krw"]) and r["price_krw"]:
                dedup[key] = r
    return list(dedup.values())

def print_progress(done, total, ok, fail, width=40):
    ratio = 0 if total == 0 else done / max(total, 1)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    msg = f"\r[{bar}] {done}/{total} ({ratio*100:5.1f}%)  OK:{ok}  FAIL:{fail}"
    sys.stdout.write(msg)
    sys.stdout.flush()
    if done >= total:
        sys.stdout.write("\n")

def make_list_url(page:int) -> str:
    qs = {
        "num": 60,
        "page": page,
        "orderBy": "popular",
        "category_id[]": 2,
        "keyword": "",
        "kind": "bt",
    }
    from urllib.parse import urlencode
    return f"{BASE}/product?{urlencode(qs, doseq=True)}"

def detect_last_page(driver) -> int:
    """첫 페이지에서 .ui.pagination.first.menu a[type='pageItem']의 value 중 최댓값을 읽는다."""
    driver.get(make_list_url(1))
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".productList"))
        )
    except TimeoutException:
        pass
    time.sleep(0.6)
    last = 1
    items = driver.find_elements(By.CSS_SELECTOR, PAGE_ITEM_SEL)
    for a in items:
        val = a.get_attribute("value") or get_text(a)
        try:
            v = int(val)
            if v > last:
                last = v
        except:
            continue
    return max(1, last)

def collect_all_links(driver):
    """버튼 클릭 대신 page=1..last를 URL로 직접 순회(클릭 이슈 방지)."""
    last = detect_last_page(driver)
    print(f"Detected last page: {last}")
    all_links = []
    for p in range(1, last + 1):
        driver.get(make_list_url(p))
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".productList"))
            )
        except TimeoutException:
            pass
        time.sleep(0.6)
        cards = driver.find_elements(By.CSS_SELECTOR, ".productList .productThumbnail .item a[href^='/product/show/']")
        links = []
        for a in cards:
            href = a.get_attribute("href")
            if href and "/product/show/" in href:
                links.append(href)
        links = list(dict.fromkeys(links))
        all_links.extend(links)
    return list(dict.fromkeys(all_links))

def crawl_all_pages():
    driver = setup_driver(headless=True)
    rows = []
    try:
        links = collect_all_links(driver)
        total = len(links)
        done = ok = fail = 0
        print(f"Total items to crawl: {total}")
        print_progress(done, total, ok, fail)

        for link in links:
            try:
                item_rows = collect_detail(driver, link)
                rows.extend(item_rows)
                ok += 1
            except Exception:
                fail += 1
            finally:
                done += 1
                print_progress(done, total, ok, fail)
                time.sleep(0.15)
    finally:
        driver.quit()

    final = []
    seen = set()
    for r in rows:
        key = (r["brand"], r["name"], r["size_ml"], r["detail_url"])
        if key not in seen:
            seen.add(key)
            final.append(r)

    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=[
            "brand", "name", "size_ml", "price_krw", "detail_url", "description"
        ])
        w.writeheader()
        w.writerows(final)

    print(f"Saved {len(final)} rows → {OUT_CSV}")

if __name__ == "__main__":
    crawl_all_pages()
