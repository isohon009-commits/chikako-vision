"""
FastAPI server — agent ilovasi rasm yuboradi, panel ma'lumot oladi.

Endpointlar:
  GET  /panel    — web boshqaruv paneli (brauzerda ochasiz)
  GET  /stats    — umumiy statistika (panel uchun)
  GET  /visits   — tashriflar ro'yxati (panel uchun)
  POST /analyze  — faqat AI sifat baholash
  POST /verify   — to'liq tekshiruv (rasm + GPS + dublikat) + bazaga saqlash
"""

import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from analyzer import analyze_image_bytes
from verify import verify_visit
from database import get_visits, get_stats

app = FastAPI(title="Chikako Vision API")

HERE = os.path.dirname(__file__)


@app.get("/")
def health():
    return {"status": "ishlayapti", "panel": "/panel"}


@app.get("/panel")
def panel():
    """Web boshqaruv paneli."""
    return FileResponse(os.path.join(HERE, "panel.html"))


@app.get("/agent")
def agent_app():
    """Agent ilovasi (telefonda ochiladi)."""
    return FileResponse(os.path.join(HERE, "agent.html"))


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/visits")
def visits(suspicious: bool = False, agent: str = None):
    return get_visits(only_suspicious=suspicious, agent=agent)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Faqat AI sifat baholash."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Faqat rasm yuboring")
    image_bytes = await file.read()
    try:
        return analyze_image_bytes(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahlil xatosi: {e}")


@app.post("/verify")
async def verify(
    file: UploadFile = File(...),
    photo_lat: float = Form(None),
    photo_lng: float = Form(None),
    store_lat: float = Form(None),
    store_lng: float = Form(None),
    agent: str = Form(""),
    store: str = Form(""),
    date: str = Form(""),
):
    """To'liq tekshiruv: sifat + GPS + dublikat. Natija bazaga saqlanadi."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Faqat rasm yuboring")

    image_bytes = await file.read()
    suffix = ".png" if file.content_type == "image/png" else ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(image_bytes)
    tmp.close()

    try:
        result = verify_visit(
            tmp.name,
            photo_lat=photo_lat, photo_lng=photo_lng,
            store_lat=store_lat, store_lng=store_lng,
            agent=agent, store=store, date=date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tekshiruv xatosi: {e}")
    finally:
        os.unlink(tmp.name)

    return result
