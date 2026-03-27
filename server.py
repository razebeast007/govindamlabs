from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import os
import time
import zipfile
import uuid
import json

app = FastAPI()

# -------- REQUEST MODEL --------
class LinkRequest(BaseModel):
    links: list[str]

# -------- SELENIUM --------
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=chrome_options)

# -------- DOWNLOAD --------
def download_image(url, folder):
    try:
        r = requests.get(url, stream=True, timeout=20)
        filename = url.split("/")[-1].split("?")[0]

        path = os.path.join(folder, filename)
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)

        return filename
    except:
        return None

# -------- SSE GENERATOR --------
def event_stream(links):
    driver = create_driver()

    folder = f"images_{uuid.uuid4().hex}"
    os.makedirs(folder, exist_ok=True)

    downloaded_files = []

    total = len(links)
    count = 0

    for link in links:
        count += 1

        try:
            yield f"data: {json.dumps({'status': f'Processing {count}/{total}'})}\n\n"

            driver.get(link)
            time.sleep(5)

            # og:image
            img_url = driver.execute_script("""
                var meta = document.querySelector("meta[property='og:image']");
                return meta ? meta.content : null;
            """)

            # backup
            if not img_url:
                imgs = driver.find_elements(By.TAG_NAME, "img")

for img in imgs:
    src = img.get_attribute("src")

    if src and ".jpeg?q=90" in src:
        img_url = src
        break

            if img_url:
                file = download_image(img_url, folder)
                if file:
                    downloaded_files.append(os.path.join(folder, file))
                    yield f"data: {json.dumps({'status': 'Image downloaded'})}\n\n"
                else:
                    yield f"data: {json.dumps({'status': 'Download failed'})}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'Image not found'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': f'Error: {str(e)}'})}\n\n"

        time.sleep(2)

    driver.quit()

    # -------- ZIP --------
    zip_name = f"{folder}.zip"

    with zipfile.ZipFile(zip_name, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))

    yield f"data: {json.dumps({'done': True, 'filename': zip_name})}\n\n"


# -------- API --------
@app.post("/extract-live")
async def extract_live(data: LinkRequest):
    return StreamingResponse(event_stream(data.links), media_type="text/event-stream")


# -------- DOWNLOAD --------
@app.get("/download/{filename}")
def download_file(filename: str):
    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/zip"
    )