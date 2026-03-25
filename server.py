from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import zipfile, os, time, requests, json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from urllib.parse import urlparse, parse_qs
import random
from bs4 import BeautifulSoup

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Data(BaseModel):
    links: list[str]

# 🧹 ZIP delete helper
def delete_file(path: str):
    try:
        time.sleep(600)
        if os.path.exists(path):
            os.remove(path)
            print("🧹 Deleted:", path)
    except Exception as e:
        print("❌ Delete error:", e)


# ================= FLIPKART IMAGE =================
# ================= FLIPKART IMAGE (FAST VERSION) =================
@app.post("/extract-live")
def extract_live(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)

        downloaded = []
        total = len(data.links)

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        for i, link in enumerate(data.links):
            try:
                yield f"data: {json.dumps({'status': f'Processing {i+1}/{total}'})}\n\n"

                r = requests.get(link, headers=headers, timeout=15)

                soup = BeautifulSoup(r.text, "html.parser")

                # 🔥 og:image
                meta = soup.find("meta", property="og:image")
                img_url = meta["content"] if meta else None

                # 🔥 fallback
                if not img_url:
                    imgs = soup.find_all("img")
                    for img in imgs:
                        src = img.get("src")
                        if src and "rukminim" in src:
                            img_url = src
                            break

                if img_url:
                    filename = img_url.split("/")[-1].split("?")[0]
                    path = f"images/{filename}"

                    img_res = requests.get(img_url, timeout=15)

                    with open(path, "wb") as f:
                        f.write(img_res.content)

                    downloaded.append(path)

                    yield f"data: {json.dumps({'status': f'Downloaded {filename}'})}\n\n"

                else:
                    yield f"data: {json.dumps({'status': 'Image not found'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        if not downloaded:
            yield f"data: {json.dumps({'status': 'No images found', 'done': True})}\n\n"
            return

        zip_path = f"images_{int(time.time())}.zip"

        with zipfile.ZipFile(zip_path, 'w') as z:
            for file in downloaded:
                z.write(file, os.path.basename(file))

        for file in downloaded:
            try:
                os.remove(file)
            except:
                pass

        background_tasks.add_task(delete_file, zip_path)

        yield f"data: {json.dumps({'done': True, 'zip': zip_path})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ================= DOWNLOAD =================
@app.get("/download/{filename}")
def download_file(filename: str):
    if not os.path.exists(filename):
        return {"error": "File not found"}

    return FileResponse(
        path=filename,
        filename="images.zip",
        media_type="application/zip"
    )


# ================= AMAZON IMAGE =================
USER_AGENTS = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119 Safari/537.36",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.amazon.in/",
        "Connection": "keep-alive"
    }

def extract_asin(link):
    if len(link) == 10 and link.isalnum():
        return link
    if "/dp/" in link:
        return link.split("/dp/")[1].split("/")[0]
    if "/gp/product/" in link:
        return link.split("/gp/product/")[1].split("/")[0]

    parsed = urlparse(link)
    params = parse_qs(parsed.query)
    if "field-asin" in params:
        return params["field-asin"][0]

    return None


@app.post("/extract-amazon-live")
def extract_amazon(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)
        downloaded = []
        total = len(data.links)

        for i, link in enumerate(data.links):
            try:
                yield f"data: {json.dumps({'status': f'Processing {i+1}/{total}'})}\n\n"

                asin = extract_asin(link)
                if not asin:
                    yield f"data: {json.dumps({'status': 'Invalid ASIN'})}\n\n"
                    continue

                url = f"https://www.amazon.in/dp/{asin}"
                r = requests.get(url, headers=get_headers(), timeout=20)

                soup = BeautifulSoup(r.text, "html.parser")
                img = soup.select_one("#landingImage")

                img_url = img.get("data-old-hires") if img else None

                if img_url:
                    path = f"images/{asin}.jpg"
                    img_res = requests.get(img_url, headers=get_headers(), timeout=20)

                    with open(path, "wb") as f:
                        f.write(img_res.content)

                    downloaded.append(path)

                    yield f"data: {json.dumps({'status': f'Downloaded {asin}'})}\n\n"
                else:
                    yield f"data: {json.dumps({'status': 'Image not found'})}\n\n"

                time.sleep(random.uniform(2,5))

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        if not downloaded:
            yield f"data: {json.dumps({'status': 'No images found', 'done': True})}\n\n"
            return

        zip_path = f"amazon_{int(time.time())}.zip"

        with zipfile.ZipFile(zip_path, 'w') as z:
            for file in downloaded:
                z.write(file, os.path.basename(file))

        for file in downloaded:
            try:
                os.remove(file)
            except:
                pass

        background_tasks.add_task(delete_file, zip_path)

        yield f"data: {json.dumps({'done': True, 'zip': zip_path})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ================= REVIEW FIX =================
@app.post("/fix-flipkart-link")
def fix_flipkart(data: Data):

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    fixed_links = []

    for link in data.links:
        try:
            driver.get(link)
            time.sleep(3)

            final_url = driver.current_url

            pid = None
            if "pid=" in final_url:
                pid = final_url.split("pid=")[1].split("&")[0]

            if pid:
                fixed_links.append(f"https://www.flipkart.com/reviews/{pid}")
            else:
                fixed_links.append("❌ PID not found")

        except Exception as e:
            fixed_links.append(f"❌ Error: {str(e)}")

    driver.quit()

    return {"fixed": fixed_links}


# ================= FIND REVIEW PAGE =================
@app.post("/find-review-page")
def find_review(data: Data):

    base_url = data.links[0]

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    def is_review_page():
        try:
            body = driver.page_source.lower()

            # 🔥 better detection
            return (
                "ratings & reviews" in body
                or "customer review" in body
                or "reviews" in driver.title.lower()
            )
        except:
            return False

    found_url = None

    # 🔥 Phase 1 (1–100)
    for i in range(1, 101):
        try:
            url = f"{base_url}:{i}"
            driver.get(url)
            time.sleep(3)

            if is_review_page():
                found_url = url
                break
        except:
            pass

    # 🔥 Phase 2 (jump 100–1000)
    if not found_url:
        for i in range(100, 1001, 100):
            try:
                url = f"{base_url}:{i}"
                driver.get(url)
                time.sleep(3)

                if is_review_page():
                    found_url = url
                    break
            except:
                pass

    driver.quit()

    if found_url:
        return {"found": True, "url": found_url}
    else:
        return {"found": False}