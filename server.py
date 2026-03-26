from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
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
    except:
        pass

# ================= HEADERS =================
def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.flipkart.com/",
        "Connection": "keep-alive"
    }

# ================= FLIPKART IMAGE =================
@app.post("/extract-live")
def extract_live(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)

        downloaded = []
        total = len(data.links)

        for i, link in enumerate(data.links):
            try:
                yield f"data: {json.dumps({'status': f'Processing {i+1}/{total}'})}\n\n"

                final_url = None

                # 🔥 retry
                for _ in range(3):
                    try:
                        r = requests.get(link, headers=get_headers(), allow_redirects=True, timeout=20)
                        final_url = r.url
                        break
                    except:
                        time.sleep(2)

                if not final_url:
                    continue

                if "dlhttp" in final_url:
                    final_url = final_url.split("dlhttp")[-1]

                final_url = final_url.replace("m.flipkart.com", "www.flipkart.com")

                # PID
                pid = None
                if "pid=" in final_url:
                    pid = final_url.split("pid=")[1].split("&")[0]

                if not pid:
                    continue

                # 🔥 page fetch
                page = requests.get(final_url, headers=get_headers(), timeout=20)
                soup = BeautifulSoup(page.text, "html.parser")

                img_url = None

                # 🔥 main image
                img = soup.find("img", {"class": "_396cs4"})
                if img:
                    img_url = img.get("src")

                # 🔥 fallback
                if not img_url:
                    meta = soup.find("meta", property="og:image")
                    if meta:
                        img_url = meta.get("content")

                # 🔥 filter logo
                if img_url and "rukminim" not in img_url:
                    img_url = None

                if img_url:
                    filename = f"{pid}.jpg"
                    path = f"images/{filename}"

                    img_res = requests.get(img_url, timeout=20)
                    with open(path, "wb") as f:
                        f.write(img_res.content)

                    downloaded.append(path)

                    yield f"data: {json.dumps({'status': f'Downloaded {filename}'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        if not downloaded:
            yield f"data: {json.dumps({'status': 'No images', 'done': True})}\n\n"
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

# ================= AMAZON =================
def extract_asin(link):
    if "/dp/" in link:
        return link.split("/dp/")[1].split("/")[0]
    return None

@app.post("/extract-amazon-live")
def extract_amazon(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)
        downloaded = []

        for link in data.links:
            try:
                asin = extract_asin(link)
                if not asin:
                    continue

                url = f"https://www.amazon.in/dp/{asin}"

                r = requests.get(url, headers=get_headers(), timeout=20)
                soup = BeautifulSoup(r.text, "html.parser")

                img = soup.select_one("#landingImage")
                img_url = img.get("data-old-hires") or img.get("src")

                path = f"images/{asin}.jpg"

                img_res = requests.get(img_url, timeout=20)
                with open(path, "wb") as f:
                    f.write(img_res.content)

                downloaded.append(path)

                yield f"data: {json.dumps({'status': f'Downloaded {asin}'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        if not downloaded:
            yield f"data: {json.dumps({'done': True})}\n\n"
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

# ================= FIX LINK =================
@app.post("/fix-flipkart-link")
def fix_flipkart(data: Data):

    fixed_links = []

    for link in data.links:
        try:
            final_url = None

            for _ in range(3):
                try:
                    r = requests.get(link, headers=get_headers(), allow_redirects=True, timeout=20)
                    final_url = r.url
                    break
                except:
                    time.sleep(2)

            if not final_url:
                fixed_links.append("❌ Timeout")
                continue

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
            fixed_links.append(f"❌ {str(e)}")

    return {"fixed": fixed_links}

# ================= FIND REVIEW =================
@app.post("/find-review-page")
def find_review(data: Data):

    base_url = data.links[0]

    for i in range(1, 101):
        try:
            url = f"{base_url}:{i}"
            r = requests.get(url, headers=get_headers(), timeout=20)

            time.sleep(2)

            if "customer review" in r.text.lower():
                return {"found": True, "url": url}
        except:
            pass

    for i in range(100, 1001, 100):
        try:
            url = f"{base_url}:{i}"
            r = requests.get(url, headers=get_headers(), timeout=20)

            time.sleep(2)

            if "customer review" in r.text.lower():
                return {"found": True, "url": url}
        except:
            pass

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