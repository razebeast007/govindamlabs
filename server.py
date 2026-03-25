from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import zipfile, os, time, requests, json, random
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

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

# ================= DELETE ZIP =================
def delete_file(path: str):
    try:
        time.sleep(600)
        if os.path.exists(path):
            os.remove(path)
            print("🧹 Deleted:", path)
    except Exception as e:
        print("❌ Delete error:", e)


# ================= FLIPKART IMAGE (UNCHANGED - SELENIUM) =================
@app.post("/extract-live")
def extract_live(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=chrome_options)

        downloaded = []
        total = len(data.links)

        for i, link in enumerate(data.links):
            try:
                yield f"data: {json.dumps({'status': f'Processing {i+1}/{total}'})}\n\n"

                driver.get(link)
                time.sleep(3)

                img_url = driver.execute_script("""
                    var meta = document.querySelector("meta[property='og:image']");
                    return meta ? meta.content : null;
                """)

                if not img_url:
                    imgs = driver.find_elements(By.TAG_NAME, "img")
                    for img in imgs:
                        src = img.get_attribute("src")
                        if src and "rukminim" in src:
                            img_url = src
                            break

                if img_url:
                    filename = img_url.split("/")[-1].split("?")[0]
                    path = f"images/{filename}"

                    r = requests.get(img_url)
                    with open(path, "wb") as f:
                        f.write(r.content)

                    downloaded.append(path)

                    yield f"data: {json.dumps({'status': f'Downloaded {filename}'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        driver.quit()

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


# ================= AMAZON =================
USER_AGENTS = [
    "Mozilla/5.0",
    "Mozilla/5.0 (Windows NT 10.0)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.amazon.in/"
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
    return params.get("field-asin", [None])[0]


@app.post("/extract-amazon-live")
def extract_amazon(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)

        downloaded = []

        for link in data.links:
            try:
                asin = extract_asin(link)

                url = f"https://www.amazon.in/dp/{asin}"
                r = requests.get(url, headers=get_headers())

                soup = BeautifulSoup(r.text, "html.parser")
                img = soup.select_one("#landingImage")

                img_url = img.get("data-old-hires") or img.get("src")

                path = f"images/{asin}.jpg"
                img_res = requests.get(img_url, headers=get_headers())

                with open(path, "wb") as f:
                    f.write(img_res.content)

                downloaded.append(path)

                yield f"data: {json.dumps({'status': f'Downloaded {asin}'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        zip_path = f"amazon_{int(time.time())}.zip"

        with zipfile.ZipFile(zip_path, 'w') as z:
            for file in downloaded:
                z.write(file, os.path.basename(file))

        for file in downloaded:
            os.remove(file)

        background_tasks.add_task(delete_file, zip_path)

        yield f"data: {json.dumps({'done': True, 'zip': zip_path})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ================= FIX LINK (🔥 FINAL FIXED) =================
@app.post("/fix-flipkart-link")
def fix_flipkart(data: Data):

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    fixed_links = []

    for link in data.links:
        try:
            driver.get(link)

            # 🔥 wait for full redirect chain
            time.sleep(4)

            final_url = driver.current_url

            # 🔥 FIX dlhttp bug
            if "dlhttp" in final_url:
                final_url = final_url.split("dlhttp")[-1]

            final_url = final_url.replace("m.flipkart.com", "www.flipkart.com")

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


# ================= FIND REVIEW =================
@app.post("/find-review-page")
def find_review(data: Data):

    base_url = data.links[0]

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    def is_review_page():
        try:
            body = driver.page_source.lower()

            return (
                 "customer review" in body
            )
        except:
            return False

    found_url = None

    # 🔥 PHASE 1 (1 → 100)
    for i in range(1, 101):
        try:
            url = f"{base_url}:{i}"

            driver.get(url)

            # 🔥 WAIT FOR LOAD (IMPORTANT)
            time.sleep(3)

            if is_review_page():
                found_url = url
                break

        except:
            pass

    # 🔥 PHASE 2 (100 → 1000 jump)
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