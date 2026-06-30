# Chikako Vision — polka tahlili prototipi

Agent yuborgan polka rasmini AI ko'rib chiqib, Chikako va raqobatchilarni baholaydi.

## Fayllar
- `analyzer.py` — AI vision yadrosi (asosiy mantiq shu yerda)
- `main.py` — FastAPI server (FlutterFlow ilova shu yerga rasm yuboradi)
- `test_local.py` — terminaldan bitta rasmni sinab ko'rish uchun
- `requirements.txt` — kerakli kutubxonalar

---

## 1-qadam: API kalit olish (Gemini, bepul start bor)

1. https://aistudio.google.com saytiga kiring (Google akkaunt bilan)
2. "Get API key" → "Create API key" bosing
3. Kalitni nusxalang (AIza... bilan boshlanadi)

> Boshqa provayderni xohlasangiz: `analyzer.py` ichidagi `PROVIDER` ni
> `"claude"` yoki `"openai"` ga o'zgartiring va o'sha xizmatdan kalit oling.

---

## 2-qadam: O'rnatish va sinash (kompyuteringizda)

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# API kalitni kiritish (Windows uchun: set GEMINI_API_KEY=...)
export GEMINI_API_KEY="bu_yerga_kalit"

# Bitta rasmni sinab ko'rish
python test_local.py polka.jpg
```

Natija shunday chiqadi:
```
  Chikako bormi:      True
  Chikako facing:     16
  Joylashuv:          ko'z darajasida
  UMUMIY BALL:        8 / 10
  Raqobatchilar:
    - MERRYPO: 12 facing, ko'z darajasida
  ...
```

Avval shu bosqichni o'tkazing — AI sizning haqiqiy rasmlaringizni qanchalik
to'g'ri baholashini o'z ko'zingiz bilan ko'rasiz. Agar yaxshi ishlasa, keyingi
bosqichga o'tamiz.

---

## 3-qadam: Serverni ishga tushirish (lokal)

```bash
uvicorn main:app --reload
```

Brauzerda `http://localhost:8000` ochilsa — server ishlayapti.
`http://localhost:8000/docs` da `/analyze` endpointini bevosita sinash mumkin.

---

## 4-qadam: Render.com'ga qo'yish (sizning backend turgan joy)

1. Bu papkani GitHub'ga yuklang (yoki mavjud repога papka qo'shing)
2. Render'da "New Web Service" → repоni ulang
3. Sozlamalar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment → `GEMINI_API_KEY` qo'shing (kalitni kiriting)
5. Deploy

Tayyor bo'lgach, FlutterFlow ilovangiz rasmlarni
`https://sizning-servis.onrender.com/analyze` ga yuboradi.

---

## Keyingi bosqichlar (hozir yo'q, rejaga)

Bu prototip faqat **sifat baholash** qismi. To'liq tizimga keyin qo'shiladi:
- GPS tekshirish (rasm do'kon manziliga to'g'ri keladimi)
- Dublikat rasm aniqlash (image hash)
- Natijalarni bazaga saqlash (kim, qachon, qaysi do'kon)
- Web panel (shubhali tashriflar ro'yxati)

Avval shu prototip ishonchli ishlasin — keyin ustiga quramiz.

---

## YANGI: GPS + Dublikat tekshiruvi

Endi prototipda aldashni to'xtatuvchi qatlam ham bor.

Yangi fayllar:
- `gps_check.py` — rasm do'kon manziliga to'g'ri keladimi
- `duplicate_check.py` — bu rasm avval ishlatilganmi
- `verify.py` — uchala tekshiruvni (sifat + GPS + dublikat) birlashtiradi
- `test_verify.py` — to'liq tekshiruvni sinash uchun

### Sinash

Avval yangi kutubxonalarni o'rnating:
```
pip install -r requirements.txt
```

Keyin to'liq tekshiruvni ishga tushiring:
```
py test_verify.py polka.jpg
```

Natija: tashrif TOZA yoki SHUBHALI ekanini aytadi va nega shubhali ekanini ko'rsatadi.

### Sinab ko'rish g'oyalari
- **GPS shubhali:** `test_verify.py` ichida `STORE_LNG` ni o'zgartiring (masalan 70.9600) — masofa katta chiqib, shubhali deb belgilaydi.
- **Dublikat:** bir xil rasmni 2 marta ishga tushiring — ikkinchisida "avval ishlatilgan" deydi.

> `hashes.json` fayli avtomatik yaratiladi — bu rasmlarning barmoq izlari saqlanadigan joy.
> Keyinchalik bu oddiy fayl o'rniga baza (SQLite/PostgreSQL) ishlatiladi.

### Server endpointlari
- `POST /analyze` — faqat sifat baholash (rasm)
- `POST /verify` — to'liq tekshiruv (rasm + GPS koordinatalar)

---

## YANGI: Web panel + baza

Endi har tashrif bazaga saqlanadi va brauzerda boshqaruv panelida ko'rinadi.

Yangi fayllar:
- `database.py` — SQLite baza (tashriflar saqlanadi)
- `panel.html` — web boshqaruv paneli
- `seed_demo.py` — namuna ma'lumot (panelni darrov to'ldirib ko'rish uchun)

### Panelni ko'rish (3 qadam)

1. Namuna ma'lumot qo'shing (panelni bo'sh emas, to'liq ko'rish uchun):
```
py seed_demo.py
```

2. Serverni ishga tushiring:
```
uvicorn main:app --reload
```

3. Brauzerda oching:
```
http://localhost:8000/panel
```

Panelda ko'rasiz: jami tashrif, shubhalilar soni, o'rtacha ball, agentlar.
Har tashrif: TOZA yoki SHUBHALI, ball, polka ulushi, shubhali sabablar.
"Shubhali" tugmasi bilan faqat muammoli tashriflarni ko'rasiz.

### Haqiqiy ma'lumot

`py test_verify.py polka.jpg` ishga tushirsangiz, natija avtomatik bazaga
saqlanadi va panelda paydo bo'ladi. Ya'ni har tekshiruv panelda ko'rinadi.

Namuna ma'lumotni o'chirish uchun `visits.db` faylini o'chiring.

### Endpointlar
- `GET  /panel`   — web panel
- `GET  /stats`   — statistika
- `GET  /visits`  — tashriflar ro'yxati (`?suspicious=true` bilan faqat shubhalilar)
- `POST /verify`  — to'liq tekshiruv + bazaga saqlash

---

## RENDER'GA JOYLASH (internetga chiqarish)

Tizimni internetga chiqarsak, siz va agentlar istalgan joydan ochasiz.

Yangi fayllar:
- `render.yaml` — Render sozlamasi (avtomatik)
- `.gitignore` — keraksiz fayllarni repога qo'shmaslik uchun

### Muhim: ma'lumot saqlanishi
Render qayta yuklanganda oddiy fayllar o'chadi. Shuning uchun baza (`visits.db`)
va dublikat ro'yxati (`hashes.json`) **disk**da saqlanadi. Buning uchun:
- Render'da **Starter** tarif (oyiga ~$7) — diskli
- `DATA_DIR=/data` muhit o'zgaruvchisi (render.yaml'da bor)

### Qadamlar (GitHub orqali, kodsiz)

**1. GitHub'ga yuklash**
1. github.com'ga kiring (akkaunt yo'q bo'lsa — ro'yxatdan o'ting)
2. "New repository" → nom bering (masalan `chikako-vision`) → Create
3. "uploading an existing file" havolasini bosing
4. `chikako_vision` papkasidagi BARCHA fayllarni sudrab tashlang (drag-drop)
5. "Commit changes"

**2. Render'ga ulash**
1. render.com'ga kiring → "New" → "Blueprint"
2. GitHub repони ulang → render.yaml avtomatik o'qiladi
3. `GEMINI_API_KEY` so'raganda — kalitingizni kiriting
4. "Apply" / "Deploy"

**3. Ochish**
Deploy tugagach Render sizga manzil beradi (masalan
`https://chikako-vision.onrender.com`). Panelni ochish uchun:
```
https://chikako-vision.onrender.com/panel
```

> Eslatma: birinchi deploy'dan keyin baza bo'sh bo'ladi.
> `seed_demo` Render'da ishlamaydi — haqiqiy tashriflar `/verify` orqali keladi.

---

## YANGI: Agent ilovasi (web)

Agentlar telefonda ochib ishlatadigan web ilova — rasm + GPS + yuborish.

Yangi fayl: `agent.html` — agent ilovasi (telefonda ochiladi).

### Ochish
Render'ga joylangach, agentlar telefonida brauzerda ochadi:
```
https://chikako-vision.onrender.com/agent
```

Telefon ekraniga yorliq qo'ysa (Add to Home Screen), ilova kabi ochiladi.

### Qanday ishlaydi
1. Agent ism + telefon kiritadi (bir marta, keyin eslab qoladi)
2. Do'kon nomini yozadi
3. "Rasm olish" — kamera ochiladi, polka rasmini oladi
4. GPS avtomatik biriktiriladi
5. "Yuborish" — server tekshiradi, natija ko'rinadi
6. Yuborilgan tashrif panelda darrov paydo bo'ladi

### Eslatma
- GPS uchun brauzer ruxsat so'raydi — agent "Ruxsat berish" bosishi kerak
- Internet kerak (web ilova). Internetsiz ishlash kerak bo'lsa — keyin native (FlutterFlow)
- Panelда har tashrifning GPS joyi "📍 Rasm olingan joyni ko'rish" havolasi bilan ko'rinadi

### Hozircha yo'q (keyingi versiya)
- Do'kon ro'yxati + koordinatalar (GPS'ni do'konga solishtirish uchun)
- Zakaz olish (katalog, miqdor)
- Ovozli tahlil (cho'ntakда yozish kerak bo'lsa — native)
