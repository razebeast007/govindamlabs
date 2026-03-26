from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import zipfile, os, time, requests, json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Data(BaseModel):
    links: list[str]


# 🔥 HEADERS (important)
def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }


# 🧹 AUTO DELETE ZIP (10 min)
def delete_file(path: str):
    time.sleep(600)
    if os.path.exists(path):
        os.remove(path)


# ================= FLIPKART IMAGE =================
@app.post("/extract-live")
def extract_flipkart(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)

        downloaded = []
        total = len(data.links)

        for i, link in enumerate(data.links):
            try:
                yield f"data: {json.dumps({'status': f'Processing {i+1}/{total}'})}\n\n"

                # 🔥 resolve short link
                r = requests.get(link, headers=get_headers(), allow_redirects=True, timeout=20)
                final_url = r.url

                # 🔥 PID extract
                pid = None
                if "pid=" in final_url:
                    pid = final_url.split("pid=")[1].split("&")[0]

                if not pid:
                    continue

                # 🔥 page load
                page = requests.get(final_url, headers=get_headers(), timeout=20)
                soup = BeautifulSoup(page.text, "html.parser")

                # 🔥 BEST METHOD (og:image)
                meta = soup.find("meta", property="og:image")
                if not meta:
                    continue

                img_url = meta.get("content")

                # 🔥 ensure high quality
                if "q=" in img_url:
                    img_url = img_url.split("?")[0]

                img_url = img_url + "?q=90"

                # 🔥 download
                path = f"images/{pid}.jpg"

                img_res = requests.get(img_url, timeout=20)
                with open(path, "wb") as f:
                    f.write(img_res.content)

                downloaded.append(path)

                yield f"data: {json.dumps({'status': f'Downloaded {pid}'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'status': str(e)})}\n\n"

        if not downloaded:
            yield f"data: {json.dumps({'status': 'No images', 'done': True})}\n\n"
            return

        # 📦 ZIP
        zip_path = f"flipkart_{int(time.time())}.zip"

        with zipfile.ZipFile(zip_path, 'w') as z:
            for file in downloaded:
                z.write(file, os.path.basename(file))

        # 🧹 cleanup images
        for file in downloaded:
            os.remove(file)

        background_tasks.add_task(delete_file, zip_path)

        yield f"data: {json.dumps({'done': True, 'zip': zip_path})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ================= AMAZON =================
@app.post("/extract-amazon-live")
def extract_amazon(data: Data, background_tasks: BackgroundTasks):

    def event_stream():
        os.makedirs("images", exist_ok=True)
        downloaded = []

        for link in data.links:
            try:
                asin = link.split("/dp/")[1].split("/")[0]

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
            os.remove(file)

        background_tasks.add_task(delete_file, zip_path)

        yield f"data: {json.dumps({'done': True, 'zip': zip_path})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ================= FIX LINK =================
@app.post("/fix-flipkart-link")
def fix_link(data: Data):

    fixed_links = []

    for link in data.links:
        try:
            r = requests.get(link, headers=get_headers(), allow_redirects=True, timeout=20)
            final_url = r.url

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

    base = data.links[0]

    # 🔥 1 to 100
    for i in range(1, 101):
        try:
            url = f"{base}:{i}"
            r = requests.get(url, headers=get_headers(), timeout=20)

            time.sleep(1)

            if "customer review" in r.text.lower():
                return {"found": True, "url": url}
        except:
            pass

    # 🔥 100 jumps
    for i in range(100, 1001, 100):
        try:
            url = f"{base}:{i}"
            r = requests.get(url, headers=get_headers(), timeout=20)

            time.sleep(1)

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