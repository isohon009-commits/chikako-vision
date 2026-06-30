"""
Chikako polka tahlili — AI vision yadrosi.
Bitta polka rasmini ko'rib, Chikako va raqobatchilarni baholaydi.

Provayderni almashtirish uchun faqat PROVIDER o'zgaruvchisini o'zgartiring:
  "gemini"  -> Google Gemini Flash (eng arzon, tavsiya etiladi)
  "claude"  -> Anthropic Claude (sifatliroq, qimmatroq)
  "openai"  -> OpenAI GPT
"""

import os
import json
import base64

# ============== SOZLAMA ==============
PROVIDER = "gemini"   # "gemini" | "claude" | "openai"

# Mahsulot kontekstini shu yerda o'zgartirasiz
MY_BRAND = "Chikako"
PRODUCT_CATEGORY = "bolalar tagliklari (pampers/trusiki) va gigiyena mahsulotlari"
# =====================================


# Modelga beriladigan ko'rsatma (prompt). Javob qat'iy JSON bo'lishi shart.
PROMPT = f"""Sen tajribali savdo (merchandising) nazoratchisisan. Senga do'kon polkasining rasmi beriladi.
Mening brendim: "{MY_BRAND}". Mahsulot turi: {PRODUCT_CATEGORY}.

Rasmni diqqat bilan ko'rib chiq va FAQAT quyidagi JSON formatida javob ber.
Hech qanday qo'shimcha matn, izoh yoki ``` belgilarisiz — toza JSON.

{{
  "is_real_shelf": true/false,            // Bu haqiqiy do'kon polkasimi yoki soxta/bo'sh/aloqasiz rasmmi
  "my_brand_found": true/false,           // {MY_BRAND} rasmda bormi
  "my_brand_facings": raqam,              // {MY_BRAND}ning oldindan ko'rinadigan paketlari soni (taxminiy)
  "my_brand_position": "matn",            // "ko'z darajasida" / "tepada" / "pastda" / "burchakda" — qayerda joylashgan
  "neatness": raqam,                      // Taxlanish tartibliligi 1-10 (tekis, old tomoni qaragan, toza)
  "competitors": [                        // Rasmdagi raqobatchi brendlar
    {{"name": "brend nomi", "facings": raqam, "position": "joyi"}}
  ],
  "share_of_shelf_percent": raqam,        // {MY_BRAND} tagliklar orasida polkaning necha % ini egallagan (taxminiy 0-100)
  "price_tag_visible": true/false,        // Narx yorlig'i ko'rinadimi
  "overall_score": raqam,                 // Umumiy ball 1-10 ({MY_BRAND} qanchalik yaxshi joylashtirilgan)
  "issues": ["muammo 1", "muammo 2"],     // Aniqlangan kamchiliklar (bo'lmasa bo'sh ro'yxat)
  "summary_uz": "matn"                    // O'zbek tilida 1-2 jumlalik qisqa xulosa
}}

Baholashda shularga e'tibor ber: {MY_BRAND} qancha joy egallagan, ko'z darajasidami,
toza taxlanganmi, raqobatchilar undan ko'rinarliroqmi. Ball berishda qattiqqo'l bo'l."""


def _strip_json(text: str) -> dict:
    """Model javobidan toza JSON ajratib oladi (``` yoki ortiqcha matn bo'lsa tozalaydi)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    # Birinchi { dan oxirgi } gacha
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


def analyze_image_bytes(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    """Rasm baytlarini olib, tahlil natijasini (dict) qaytaradi."""
    if PROVIDER == "gemini":
        result = _call_gemini(image_bytes, media_type)
    elif PROVIDER == "claude":
        result = _call_claude(image_bytes, media_type)
    elif PROVIDER == "openai":
        result = _call_openai(image_bytes, media_type)
    else:
        raise ValueError(f"Noma'lum PROVIDER: {PROVIDER}")
    return result


# ---------- GEMINI ----------
def _call_gemini(image_bytes: bytes, media_type: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content([
        PROMPT,
        {"mime_type": media_type, "data": image_bytes},
    ])
    return _strip_json(resp.text)


# ---------- CLAUDE ----------
def _call_claude(image_bytes: bytes, media_type: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return _strip_json(msg.content[0].text)


# ---------- OPENAI ----------
def _call_openai(image_bytes: bytes, media_type: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
            ],
        }],
    )
    return _strip_json(resp.choices[0].message.content)
