import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Berlin")

def fetch_countdown_events():
    url = "https://countdown-spielewelt.de/?post_type=tribe_events&ical=1&eventDisplay=list"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw = response.text
    except Exception as e:
        print("Fehler beim Laden des Countdown-ICS:", e)
        return []

    events = []
    current = {}
    in_event = False

    for line in raw.splitlines():
        line = line.strip()

        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
            continue

        if line == "END:VEVENT":
            in_event = False

            title = current.get("title", "").strip().lower()

            # ⭐ Filter: Nur Legacy-Turniere
            if "monatliches magic legacy turnier" in title:

                original_title = current.get("title", "").strip()

                # ⭐ Companion-Code extrahieren (z.B. YEJ6RVV)
                match = re.search(r"\b([A-Z0-9]{6,8})\b$", original_title)
                code = match.group(1) if match else None

                # ⭐ Code aus Titel entfernen
                if code:
                    clean_title = original_title.replace(code, "").strip()
                else:
                    clean_title = original_title

                # ⭐ Description setzen (mit Companion-Link)
                desc = ""
                if code:
                    desc = (
                        f"Companion Code: {code}\n"
                        f"Companion Link: https://magic.wizards.com/en/products/companion-app/tournament/{code}"
                    )

                current["title"] = clean_title
                current["description"] = desc
                current.setdefault("location", "Countdown Spielewelt Landsberg")
                current.setdefault("url", "")
                current.setdefault("all_day", False)

                events.append(current)

            continue

        if not in_event:
            continue

        # SUMMARY
        if line.startswith("SUMMARY:"):
            current["title"] = line.replace("SUMMARY:", "").strip()

        # DTSTART
        elif line.startswith("DTSTART"):
            dt = line.split(":")[1]
            current["start"] = datetime.strptime(dt, "%Y%m%dT%H%M%S").replace(tzinfo=TZ)

        # DTEND
        elif line.startswith("DTEND"):
            dt = line.split(":")[1]
            current["end"] = datetime.strptime(dt, "%Y%m%dT%H%M%S").replace(tzinfo=TZ)

        # LOCATION
        elif line.startswith("LOCATION:"):
            current["location"] = line.replace("LOCATION:", "").strip()

        # URL
        elif line.startswith("URL:"):
            current["url"] = line.replace("URL:", "").strip()

    return events
