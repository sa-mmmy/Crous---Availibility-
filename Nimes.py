import requests
import json
import asyncio
from pathlib import Path
from telegram import Bot

# ================= CONFIG =================

API_URL = "https://trouverunlogement.lescrous.fr/api/fr/search/42"
TELEGRAM_TOKEN = "7858135077:AAHfgvP2BLVJXbpHloSp_Q7jYanRqUzYwDA"
TELEGRAM_CHAT_ID = "6456218857"

STATE_FILE = Path("state.json")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# ---- NÎMES bounding box ----
NIMES_BBOX = {
    "lat_min": 43.80,
    "lat_max": 43.90,
    "lon_min": 4.30,
    "lon_max": 4.45
}

PAYLOAD = {
    "page": 0,
    "pageSize": 50,
    "need_aggregation": True
}

# ================= HELPERS =================

def is_in_nimes(residence):
    loc = residence.get("location")
    if not loc:
        return False

    lat = loc.get("lat")
    lon = loc.get("lon")

    if lat is None or lon is None:
        return False

    return (
        NIMES_BBOX["lat_min"] <= lat <= NIMES_BBOX["lat_max"]
        and NIMES_BBOX["lon_min"] <= lon <= NIMES_BBOX["lon_max"]
    )

def load_previous_ids():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def save_current_ids(ids):
    STATE_FILE.write_text(json.dumps(sorted(ids)))

# ================= MAIN =================

async def main():
    print("🔍 Fetching CROUS data...")

    all_items = []
    page = 0

    # ---- Pagination ----
    while True:
        PAYLOAD["page"] = page
        r = requests.post(API_URL, headers=HEADERS, json=PAYLOAD, timeout=15)
        data = r.json()

        items = data.get("results", {}).get("items", [])
        if not items:
            break

        all_items.extend(items)
        page += 1

    print(f"📦 Total items fetched: {len(all_items)}")

    # ---- Keep only available lodges ----
    available = [i for i in all_items if i.get("available") is True]

    # ---- Filter Nîmes ----
    nimes_available = [
        i for i in available
        if is_in_nimes(i.get("residence", {}))
    ]

    print(f"📍 Available in Nîmes: {len(nimes_available)}")

    current_ids = {i["id"] for i in nimes_available}
    previous_ids = load_previous_ids()

    # ---- First run: init state ----
    if not STATE_FILE.exists():
        save_current_ids(current_ids)
        print("🆕 First run detected — state initialized, no notification sent.")
        return

    new_ids = current_ids - previous_ids

    if not new_ids:
        print("😴 No new availability.")
        return

    # ---- Build Telegram message ----
    new_items = [i for i in nimes_available if i["id"] in new_ids]

    lines = [f"🚨 {len(new_items)} NEW CROUS logement(s) à Nîmes:\n"]

    for l in new_items:
        res = l["residence"]
        loc = res["location"]
        area = l["area"]["min"]
        beds = l["bedCount"]

        maps = f"https://maps.google.com/?q={loc['lat']},{loc['lon']}"

        lines.append(
            f"🏠 {res['label']}\n"
            f"📐 {area} m² — 🛏 {beds} lit(s)\n"
            f"📍 {maps}\n"
        )

    message = "\n".join(lines)

    # ---- Send Telegram ----
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    print("✅ Telegram notification sent")

    # ---- Save state ----
    save_current_ids(current_ids)

# ================= RUN =================

asyncio.run(main())
