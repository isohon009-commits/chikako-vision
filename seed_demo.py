"""
Namuna ma'lumot — panelni darrov to'ldirib ko'rsatish uchun.
Bu faqat sinov uchun. Haqiqiy ishda ma'lumot agentlardan keladi.

Ishlatish:
    py seed_demo.py
"""

from database import init_db, save_visit

init_db()

# Turli xil namuna tashriflar
demo = [
    # (agent, store, sana, natija)
    ("Aziz",  "Qo'qon-12",  "2026-06-30", {
        "needs_human_review": False, "flags": [],
        "vision": {"overall_score": 9, "share_of_shelf_percent": 85, "my_brand_facings": 16,
                   "my_brand_found": True, "is_real_shelf": True,
                   "summary_uz": "Chikako polkaning asosiy qismini egallagan, ko'z darajasida, toza taxlangan."},
        "gps": {"distance_m": 12}, "duplicate": {"is_duplicate": False},
    }),
    ("Vali",  "Marg'ilon-3", "2026-06-30", {
        "needs_human_review": True, "flags": ["Bu rasm avval ishlatilgan! (agent: Aziz, do'kon: Qo'qon-12)"],
        "vision": {"overall_score": 8, "share_of_shelf_percent": 70, "my_brand_facings": 11,
                   "my_brand_found": True, "is_real_shelf": True,
                   "summary_uz": "Sifat yaxshi, lekin rasm dublikat — boshqa tashrifda ishlatilgan."},
        "gps": {"distance_m": 8}, "duplicate": {"is_duplicate": True},
    }),
    ("Sardor", "Farg'ona-7", "2026-06-30", {
        "needs_human_review": True, "flags": ["Rasm do'kondan 1479 m uzoqda olingan (chegara 150 m)"],
        "vision": {"overall_score": 7, "share_of_shelf_percent": 55, "my_brand_facings": 8,
                   "my_brand_found": True, "is_real_shelf": True,
                   "summary_uz": "Polka holati o'rtacha, ammo rasm do'kondan uzoqda olingan."},
        "gps": {"distance_m": 1479}, "duplicate": {"is_duplicate": False},
    }),
    ("Aziz",  "Qo'qon-5",   "2026-06-30", {
        "needs_human_review": True, "flags": ["Chikako rasmda topilmadi", "Past sifat bali: 3/10"],
        "vision": {"overall_score": 3, "share_of_shelf_percent": 8, "my_brand_facings": 2,
                   "my_brand_found": True, "is_real_shelf": True,
                   "summary_uz": "Chikako juda kam, tepada. Raqobatchilar ko'p joy egallagan."},
        "gps": {"distance_m": 20}, "duplicate": {"is_duplicate": False},
    }),
    ("Jasur", "Quva-1",     "2026-06-29", {
        "needs_human_review": True, "flags": ["Rasm haqiqiy polka emas (soxta/aloqasiz bo'lishi mumkin)"],
        "vision": {"overall_score": 1, "share_of_shelf_percent": 0, "my_brand_facings": 0,
                   "my_brand_found": False, "is_real_shelf": False,
                   "summary_uz": "Rasmda do'kon polkasi yo'q — soxta yoki aloqasiz rasm."},
        "gps": {"distance_m": 45}, "duplicate": {"is_duplicate": False},
    }),
    ("Vali",  "Marg'ilon-1", "2026-06-29", {
        "needs_human_review": False, "flags": [],
        "vision": {"overall_score": 8, "share_of_shelf_percent": 60, "my_brand_facings": 10,
                   "my_brand_found": True, "is_real_shelf": True,
                   "summary_uz": "Yaxshi joylashtirilgan, ko'z darajasida, tartibli."},
        "gps": {"distance_m": 15}, "duplicate": {"is_duplicate": False},
    }),
]

for agent, store, date, result in demo:
    save_visit(result, agent=agent, store=store, visit_date=date)

print(f"{len(demo)} ta namuna tashrif bazaga qo'shildi.")
print("Endi serverni ishga tushiring va panelni oching:")
print("  uvicorn main:app --reload")
print("  http://localhost:8000/panel")
