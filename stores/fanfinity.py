import requests
from datetime import datetime

API_URL = "https://www.fanfinity.gg/wp-json/wp/v2/event?per_page=100"

def fetch_fanfinity_events():
    events = []

    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Fanfinity API Fehler:", e)
        return events

    for item in data:
        title = item.get("title", {}).get("rendered", "").strip()
        url = item.get("link", "")

        # Datum aus Custom Fields
        acf = item.get("acf", {})
        date_str = acf.get("event_date")  # z.B. "2026-05-12"

        if not date_str:
            continue

        try:
            start = datetime.fromisoformat(date_str)
            end = start.replace(hour=23, minute=59)
        except:
            continue

        events.append({
            "title": title,
            "url": url,
            "start": start,
            "end": end,
            "store": "Fanfinity",
            "location": "Online",
            "description": f"Event von Fanfinity: {title}\n{url}"
        })

    print(f"Fanfinity Events gefunden: {len(events)}")
    return events
