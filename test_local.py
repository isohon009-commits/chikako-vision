"""
Lokal test — bitta rasmni terminaldan tahlil qilib ko'rish uchun.

Ishlatish:
    python test_local.py rasm.jpg
"""

import sys
import json
from analyzer import analyze_image_bytes, PROVIDER, MY_BRAND


def main():
    if len(sys.argv) < 2:
        print("Foydalanish: python test_local.py <rasm_fayli>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        image_bytes = f.read()

    # Fayl turini aniqlash
    media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"

    print(f"\nProvayder: {PROVIDER} | Brend: {MY_BRAND}")
    print(f"Rasm tahlil qilinmoqda: {path} ...\n")

    result = analyze_image_bytes(image_bytes, media_type)

    # Chiroyli chiqarish
    print("=" * 50)
    print(f"  Haqiqiy polka:     {result.get('is_real_shelf')}")
    print(f"  {MY_BRAND} bormi:      {result.get('my_brand_found')}")
    print(f"  {MY_BRAND} facing:     {result.get('my_brand_facings')}")
    print(f"  Joylashuv:         {result.get('my_brand_position')}")
    print(f"  Taxlanish (1-10):  {result.get('neatness')}")
    print(f"  Polkadagi ulush:   {result.get('share_of_shelf_percent')}%")
    print(f"  Narx ko'rinadimi:  {result.get('price_tag_visible')}")
    print(f"  UMUMIY BALL:       {result.get('overall_score')} / 10")
    print("-" * 50)
    print("  Raqobatchilar:")
    for c in result.get("competitors", []):
        print(f"    - {c.get('name')}: {c.get('facings')} facing, {c.get('position')}")
    print("-" * 50)
    print("  Muammolar:")
    for issue in result.get("issues", []):
        print(f"    - {issue}")
    print("-" * 50)
    print(f"  Xulosa: {result.get('summary_uz')}")
    print("=" * 50)

    # To'liq JSON ham (backend xuddi shuni qaytaradi)
    print("\nTo'liq JSON:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
