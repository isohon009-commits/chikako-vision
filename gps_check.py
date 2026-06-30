"""
GPS tekshiruvi — rasm olingan joy do'kon manziliga to'g'ri keladimi.

Agent telefoni rasm olganda GPS koordinata (lat, lng) biriktiradi.
Bu koordinatani do'konning ro'yxatdan o'tgan manzili bilan solishtiramiz.
Agar masofa juda katta bo'lsa -> shubhali (agent do'konda emas).
"""

import math

# Necha metrgacha "normal" deb hisoblaymiz. Undan uzoq -> shubhali.
MAX_DISTANCE_METERS = 150


def distance_meters(lat1, lng1, lat2, lng2):
    """Ikki nuqta orasidagi masofani metrda hisoblaydi (Haversine formulasi)."""
    R = 6371000  # Yer radiusi, metr
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def check_gps(photo_lat, photo_lng, store_lat, store_lng):
    """
    Rasm GPS'i va do'kon GPS'ini solishtiradi.
    Natija: dict {distance_m, suspicious, reason}
    """
    dist = distance_meters(photo_lat, photo_lng, store_lat, store_lng)
    suspicious = dist > MAX_DISTANCE_METERS
    return {
        "distance_m": round(dist, 1),
        "suspicious": suspicious,
        "reason": (
            f"Rasm do'kondan {round(dist)} m uzoqda olingan (chegara {MAX_DISTANCE_METERS} m)"
            if suspicious else
            f"GPS to'g'ri — do'kondan {round(dist)} m"
        ),
    }
