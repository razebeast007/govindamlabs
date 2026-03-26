from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import requests, re, os, zipfile, time, threading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinkInput(BaseModel):
    links: list[str]

# ---------- AUTO DELETE ----------
def auto_delete(path):
    def delete():
        time.sleep(600)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=delete).start()

# ---------- FLIPKART IMAGE ----------
@app.post("/extract-live")
def extract_flipkart(data: LinkInput):
    def event_stream():
        images = []

        for i, link in enumerate(data.links):
            yield f"data: {{\"status\": \"Processing {i+1}/{len(data.links)}\"}}\n\n"

            try:
                html = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}).text

                # ✅ FIXED REGEX
                matches = re.findall(r'https://rukminim[^\"]+?\.(?:jpeg|jpg)', html)

                if matches:
                    img = matches[0]
                    if "?q=" not in img:
                        img += "?q=90"
                    images.append(img)

            except:
                pass

        if not images:
    zip_name = f"empty_{int(time.time())}.zip"
    zip_path = f"/root/govindamlabs/{zip_name}"

    with zipfile.ZipFile(zip_path, "w") as z:
        pass

    auto_delete(zip_path)

    yield f"data: {{\"status\": \"No images found ❌\", \"filename\": \"{zip_name}\", \"done\": true}}\n\n"
    return


# ---------- AMAZON IMAGE ----------
@app.post("/extract-amazon-live")
def extract_amazon(data: LinkInput):
    def event_stream():
        images = []

        for i, link in enumerate(data.links):
            yield f"data: {{\"status\": \"Processing {i+1}/{len(data.links)}\"}}\n\n"

            try:
                html = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}).text

                # ✅ LARGE IMAGE ONLY
                matches = re.findall(r'https://m\.media-amazon\.com/images/I/[^\"]+', html)

                if matches:
                    images.append(matches[0])

            except:
                pass

        # ---------- FLIPKART ----------
    if not images:
    zip_name = f"empty_{int(time.time())}.zip"
    zip_path = f"/root/govindamlabs/{zip_name}"

    with zipfile.ZipFile(zip_path, "w") as z:
        pass

    auto_delete(zip_path)

    yield f"data: {{\"status\": \"No images found ❌\", \"filename\": \"{zip_name}\", \"done\": true}}\n\n"
    return


# ---------- FIX LINK ----------
@app.post("/fix-flipkart-link")
def fix_link(data: LinkInput):
    fixed = []

    for link in data.links:
        try:
            res = requests.get(link, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})

            # ✅ IMPROVED
            final_text = res.text + res.url

            match = re.search(r'pid=([A-Z0-9]+)', final_text)

            if match:
                pid = match.group(1)
                fixed.append(f"https://www.flipkart.com/reviews/{pid}")
            else:
                fixed.append("❌ PID not found")

        except:
            fixed.append("❌ Error")

    return {"fixed": fixed}


# ---------- REVIEW FINDER ----------
@app.post("/find-review-page")
def find_review(data: LinkInput):
    for link in data.links:
        try:
            match = re.search(r'/reviews/([A-Z0-9]+)', link)
            if not match:
                continue

            pid = match.group(1)

            # 🔥 NORMAL SEARCH
            for i in range(1, 101):
                url = f"https://www.flipkart.com/reviews/{pid}:{i}"
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

                time.sleep(2)

                if "customer review" in html.lower() or "ratings & reviews" in html.lower():
                    return {"url": url}

            # 🔥 JUMP SEARCH
            for i in range(100, 1100, 100):
                url = f"https://www.flipkart.com/reviews/{pid}:{i}"
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

                time.sleep(2)

                if "customer review" in html.lower() or "ratings & reviews" in html.lower():
                    return {"url": url}

        except:
            pass

    return {"error": "No review found"}


# ---------- DOWNLOAD ----------
@app.get("/download/{filename}")
def download(filename: str):
    path = f"/root/govindamlabs/{filename}"
    if os.path.exists(path):
        return FileResponse(path, filename=filename)
    return {"error": "File not found"}