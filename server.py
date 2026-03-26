from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import requests, re, os, zipfile, time, threading

app = FastAPI()

# ---------- MODEL ----------
class LinkInput(BaseModel):
    links: list[str]


# ---------- AUTO DELETE ZIP ----------
def auto_delete(path):
    def delete():
        time.sleep(600)  # 10 min
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

                matches = re.findall(r'https://rukminim\d\.flixcart\.com/image/[^\"]+', html)

                if matches:
                    img = matches[0] + "?q=90"
                    images.append(img)

            except:
                pass

        if not images:
            yield f"data: {{\"status\": \"No images\", \"done\": true}}\n\n"
            return

        # create zip
        zip_name = f"images_{int(time.time())}.zip"
        zip_path = f"/root/govindamlabs/{zip_name}"

        with zipfile.ZipFile(zip_path, "w") as z:
            for i, img in enumerate(images):
                try:
                    img_data = requests.get(img).content
                    file_name = f"{i}.jpg"
                    with open(file_name, "wb") as f:
                        f.write(img_data)
                    z.write(file_name)
                    os.remove(file_name)
                except:
                    pass

        auto_delete(zip_path)

        yield f"data: {{\"filename\": \"{zip_name}\", \"done\": true}}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------- AMAZON IMAGE ----------
@app.post("/extract-amazon-live")
def extract_amazon(data: LinkInput):
    def event_stream():
        images = []

        for i, link in enumerate(data.links):
            yield f"data: {{\"status\": \"Processing {i+1}/{len(data.links)}\"}}\n\n"

            try:
                html = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}).text

                matches = re.findall(r'"large":"(https://[^"]+)"', html)

                if matches:
                    images.append(matches[0])

            except:
                pass

        if not images:
            yield f"data: {{\"status\": \"No images\", \"done\": true}}\n\n"
            return

        zip_name = f"amazon_{int(time.time())}.zip"
        zip_path = f"/root/govindamlabs/{zip_name}"

        with zipfile.ZipFile(zip_path, "w") as z:
            for i, img in enumerate(images):
                try:
                    img_data = requests.get(img).content
                    file_name = f"{i}.jpg"
                    with open(file_name, "wb") as f:
                        f.write(img_data)
                    z.write(file_name)
                    os.remove(file_name)
                except:
                    pass

        auto_delete(zip_path)

        yield f"data: {{\"filename\": \"{zip_name}\", \"done\": true}}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------- FIX FLIPKART LINK ----------
@app.post("/fix-flipkart-link")
def fix_link(data: LinkInput):
    fixed = []

    for link in data.links:
        match = re.search(r'pid=([A-Z0-9]+)', link)
        if match:
            pid = match.group(1)
            fixed.append(f"https://www.flipkart.com/reviews/{pid}")
        else:
            fixed.append("❌ PID not found")

    return {"fixed": fixed}


# ---------- REVIEW FINDER ----------
@app.post("/find-review-page")
def find_review(data: LinkInput):
    for link in data.links:
        try:
            # extract PID
            match = re.search(r'/reviews/([A-Z0-9]+)', link)
            if not match:
                continue

            pid = match.group(1)

            # try 1–100
            for i in range(1, 101):
                url = f"https://www.flipkart.com/reviews/{pid}:{i}"
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

                if "customer review" in html.lower():
                    return {"url": url}

            # try jumps
            for i in range(100, 1100, 100):
                url = f"https://www.flipkart.com/reviews/{pid}:{i}"
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

                if "customer reviews" in html.lower():
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