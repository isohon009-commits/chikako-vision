"""
To'liq tekshiruvni sinash — sifat + GPS + dublikat birga.

Ishlatish:
    py test_verify.py polka.jpg

GPS'ni sinash uchun pastdagi koordinatalarni o'zgartiring.
Dublikatni sinash uchun bir xil rasmni 2 marta ishga tushiring.
"""

import sys
import json
from verify import verify_visit

# === SINOV KOORDINATALARI (o'zgartirib sinab ko'ring) ===
# Rasm olingan joy (agent telefonidan keladi)
PHOTO_LAT = 40.5283
PHOTO_LNG = 70.9425

# Do'konning ro'yxatdagi manzili (bazadan keladi)
STORE_LAT = 40.5283
STORE_LNG = 70.9425
# Yuqoridagi ikkisini bir xil qo'ysangiz -> GPS to'g'ri.
# STORE'ni boshqacha qilsangiz (masalan 70.9600) -> shubhali chiqadi.
# =========================================================


def main():
    if len(sys.argv) < 2:
        print("Foydalanish: py test_verify.py <rasm_fayli>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"\nTashrif tekshirilmoqda: {path} ...\n")

    result = verify_visit(
        path,
        photo_lat=PHOTO_LAT, photo_lng=PHOTO_LNG,
        store_lat=STORE_LAT, store_lng=STORE_LNG,
        agent="Aziz", store="Qo'qon-12", date="2026-06-30",
    )

    print("=" * 55)
    if result["needs_human_review"]:
        print("  NATIJA:  ⚠  SHUBHALI — odam ko'rishi kerak")
    else:
        print("  NATIJA:  ✓  TOZA — odam ko'rishi shart emas")
    print("=" * 55)

    if result["flags"]:
        print("  Shubhali sabablar:")
        for fl in result["flags"]:
            print(f"    • {fl}")
    else:
        print("  Hech qanday muammo topilmadi.")
    print("-" * 55)

    v = result["vision"]
    print(f"  Sifat bali:   {v.get('overall_score')}/10 | "
          f"Ulush: {v.get('share_of_shelf_percent')}% | "
          f"Facing: {v.get('my_brand_facings')}")

    if result["gps"]:
        print(f"  GPS:          {result['gps']['reason']}")

    print(f"  Dublikat:     {result['duplicate']['reason']}")
    print("=" * 55)


if __name__ == "__main__":
    main()
