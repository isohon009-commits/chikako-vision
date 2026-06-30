"""
Dublikat aniqlash — bu rasm avval ishlatilganmi.

Har bir rasmning "barmoq izi" (perceptual hash) hisoblanadi.
Bu oddiy fayl hash emas — biroz qirqilgan, siqilgan yoki o'lchamı
o'zgargan rasmni ham "o'sha rasm" deb taniydi.

Barmoq izlari hashes.json fayliga saqlanadi.
(Keyinchalik bu baza — PostgreSQL/SQLite — bilan almashtiriladi.)
"""

import os
import json
from PIL import Image
import imagehash

DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(__file__))
os.makedirs(DATA_DIR, exist_ok=True)
HASH_DB = os.path.join(DATA_DIR, "hashes.json")

# Ikki rasm necha "qadam" farq qilsa, bir xil deb hisoblaymiz.
# 0 = aynan bir xil. 5 dan kichik = deyarli aniq dublikat.
DUPLICATE_THRESHOLD = 5


def _load_db():
    if not os.path.exists(HASH_DB):
        return []
    with open(HASH_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data):
    with open(HASH_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_and_store(image_path, agent="", store="", date=""):
    """
    Rasmni tekshiradi: avval ko'rilganmi? Keyin barmoq izini saqlaydi.
    Natija: dict {is_duplicate, matched_with, reason}
    """
    img = Image.open(image_path)
    h = imagehash.phash(img)   # perceptual hash
    h_str = str(h)

    db = _load_db()

    # Mavjud izlar bilan solishtirish
    for record in db:
        existing = imagehash.hex_to_hash(record["hash"])
        diff = h - existing   # qancha farqli (Hamming masofa)
        if diff <= DUPLICATE_THRESHOLD:
            return {
                "is_duplicate": True,
                "matched_with": {
                    "agent": record.get("agent"),
                    "store": record.get("store"),
                    "date": record.get("date"),
                },
                "reason": (
                    f"Bu rasm avval ishlatilgan! "
                    f"(agent: {record.get('agent')}, do'kon: {record.get('store')}, "
                    f"sana: {record.get('date')})"
                ),
            }

    # Dublikat emas -> yangi iz qo'shamiz
    db.append({"hash": h_str, "agent": agent, "store": store, "date": date})
    _save_db(db)
    return {
        "is_duplicate": False,
        "matched_with": None,
        "reason": "Yangi rasm — avval ishlatilmagan",
    }
