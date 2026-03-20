import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

TZ = ZoneInfo("Europe/Berlin")

MONTHS_DE = {
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12
}


def is_modern_or_rcq(title: str) -> bool:
    """Filtert nur Modern-Events oder RCQs heraus."""
    title = title.lower()

    include = [
        "modern",
        "rcq",
        "regional championship qualifier",
        "qualifier",
    ]

    exclude = [
        "commander",
        "edh",
        "draft",
        "sealed",
        "prerelease",
        "pre-release",
        "standard",
        "pauper",
        "booster",
        "casual",
        "painting",
        "workshop",
        "warhammer",
        "40k",
        "age of sigmar",
        "pokémon",
        "pokemon",
        "lorcana",
        "yu-gi-oh",
        "yugioh",
        "flesh and blood",
        "fab",
        "one piece",
        "star wars",
        "spearwars",
        "spear wars",
        "tabletop",
        "boardgame",
        "brettspiel",
    ]

    if any(x in title for x in exclude):
        return False

    return any(x in title for x in include)


def fetch_dd_munich_events():
    print("Hole Events von Deck & Dice / DD Munich...")

    url = "https://www.dd-munich.de/event-list"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print("Fehler bei DD Munich:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = []

    # Jede Kalenderzelle enthält 0–n Events
    for cell in soup.select('[data-hook^="calendar-cell-"]'):
        aria = cell.get("aria-label", "")
        data_hook = cell.get("data-hook", "")

        # Datum extrahieren
        m = re.search(r"calendar-cell-(\d{4})-(\d{2})-(\d{2})T", data_hook)
        if not m:
            continue

        year = int(m.group(1))

        # "15. März" aus aria-label extrahieren
        m2 = re.match(r"\s*(\d{1,2})\.\s+([A-Za-zäöüÄÖÜ]+)", aria)
        if not m2:
            continue

        day = int(m2.group(1))
        month_name = m2.group(2).lower()

        if month_name not in MONTHS_DE:
            continue

        month = MONTHS_DE[month_name]
        base_date = datetime(year, month, day, tzinfo=TZ)

        # Eventzeiten und Titel
        time_nodes = cell.select("div.B11jYK")
        title_nodes = cell.select("div.OyuNR8")

        for t_node, title_node in zip(time_nodes, title_nodes):
            time_text = t_node.get_text(strip=True)
            title = title_node.get_text(strip=True)

            # Filter anwenden
            if not is_modern_or_rcq(title):
                continue

            try:
                hour, minute = map(int, time_text.split(":"))
            except:
                continue

            start = base_date.replace(hour=hour, minute=minute)
            end = start + timedelta(hours=3)

            events.append({
                "title": title,
                "start": start,
                "end": end,
                "location": "Deck & Dice Munich",
                "url": url,
                "description": "",
            })

    print(f"DD Munich Modern/RCQ Events gefunden: {len(events)}")
    return events
