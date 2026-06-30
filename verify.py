"""
To'liq tekshiruv — uchta qatlamni birlashtiradi:
  1. AI sifat baholash (analyzer.py)
  2. GPS tekshiruvi (gps_check.py)
  3. Dublikat aniqlash (duplicate_check.py)

Va oxirida bitta xulosa beradi: bu tashrifni ODAM ko'rishi kerakmi?
Faqat shubhalilar "flag" qilinadi — qolganini odam ko'rmaydi.
"""

from analyzer import analyze_image_bytes
from gps_check import check_gps
from duplicate_check import check_and_store
from database import save_visit


def verify_visit(image_path, photo_lat=None, photo_lng=None,
                 store_lat=None, store_lng=None,
                 agent="", store="", date="", save=True):
    """Bitta tashrifni to'liq tekshiradi, bazaga saqlaydi va xulosa qaytaradi."""

    flags = []   # shubhali sabablar ro'yxati

    # --- 1. AI sifat baholash ---
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    media_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    vision = analyze_image_bytes(image_bytes, media_type)

    if not vision.get("is_real_shelf", True):
        flags.append("Rasm haqiqiy polka emas (soxta/aloqasiz bo'lishi mumkin)")
    if not vision.get("my_brand_found", False):
        flags.append("Chikako rasmda topilmadi")
    if vision.get("overall_score", 10) <= 4:
        flags.append(f"Past sifat bali: {vision.get('overall_score')}/10")

    # --- 2. GPS tekshiruvi ---
    gps = None
    if None not in (photo_lat, photo_lng, store_lat, store_lng):
        gps = check_gps(photo_lat, photo_lng, store_lat, store_lng)
        if gps["suspicious"]:
            flags.append(gps["reason"])

    # --- 3. Dublikat aniqlash ---
    dup = check_and_store(image_path, agent=agent, store=store, date=date)
    if dup["is_duplicate"]:
        flags.append(dup["reason"])

    # --- Yakuniy xulosa ---
    needs_review = len(flags) > 0

    result = {
        "needs_human_review": needs_review,     # ODAM ko'rishi kerakmi?
        "flags": flags,                         # nega shubhali
        "vision": vision,
        "gps": gps,
        "duplicate": dup,
    }

    # Bazaga saqlash
    if save:
        save_visit(result, agent=agent, store=store, visit_date=date)

    return result
