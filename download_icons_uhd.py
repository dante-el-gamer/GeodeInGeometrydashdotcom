import os
import sys
import time
import urllib.request
import concurrent.futures
from PIL import Image, ImageOps

API_BASE = "https://gdicon.oat.zone/icon.png"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/Icons"

TYPES = {
    "cube": (1, 485),
    "ship": (1, 169),
}

MAX_WORKERS = 5
RETRIES = 3
DELAY_BETWEEN_TYPES = 2

def grayscale_icon(img):
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    r, g, b, a = img.split()
    gray = ImageOps.grayscale(img)
    gray_rgb = gray.convert("RGB")
    r2, g2, b2 = gray_rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))

def download_one(args):
    icon_type, num = args
    dir_path = f"{OUTPUT_DIR}/{icon_type}"
    os.makedirs(dir_path, exist_ok=True)
    filepath = f"{dir_path}/{icon_type}_{num}.png"

    url = f"{API_BASE}?type={icon_type}&value={num}&color1=%23FFFFFF&color2=%23000000"
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GeodeInGD/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if len(data) < 100:
                print(f"  WARN: {icon_type}_{num} too small ({len(data)}b), retrying...")
                time.sleep(1)
                continue
            img = Image.open(os.fspath("/tmp/icon_dl.png")) if False else None
            import io
            img = Image.open(io.BytesIO(data))
            gray = grayscale_icon(img)
            gray.save(filepath, "PNG")
            return (icon_type, num, True, gray.size)
        except Exception as e:
            if attempt < RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                return (icon_type, num, False, str(e))

def main():
    for icon_type in TYPES:
        dir_path = f"{OUTPUT_DIR}/{icon_type}"
        if os.path.isdir(dir_path):
            for f in os.listdir(dir_path):
                fp = os.path.join(dir_path, f)
                if f.endswith(".png") and os.path.isfile(fp):
                    os.remove(fp)
            print(f"Cleaned {dir_path}")

    tasks = []
    for icon_type, (start, end) in TYPES.items():
        tasks.extend((icon_type, i) for i in range(start, end + 1))

    total = len(tasks)
    print(f"Downloading {total} icons ({MAX_WORKERS} workers)...")
    start_time = time.time()
    ok = 0
    fail = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_one, t): t for t in tasks}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            icon_type, num, success, extra = future.result()
            if success:
                ok += 1
                if done % 50 == 0 or done == total:
                    elapsed = time.time() - start_time
                    print(f"  [{done}/{total}] {icon_type}_{num} ({extra[0]}x{extra[1]}) - {elapsed:.0f}s")
            else:
                fail += 1
                print(f"  FAIL: {icon_type}_{num} - {extra}")

    elapsed = time.time() - start_time
    print(f"\nDone: {ok} OK, {fail} failed in {elapsed:.0f}s")
    print(f"Path: {OUTPUT_DIR}/{{cube,ship}}/")
    return fail == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
