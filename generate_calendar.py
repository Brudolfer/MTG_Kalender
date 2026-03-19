import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ics import Calendar, Event

print("Script gestartet")

# Öffentliche Wizards-Eventseite (HTML, nicht API)
WIZARDS_URL = (
    "https://locator.wizards.com/events"
    "?searchType=magic-events"
    "&query=München"
    "&distance=100"
)

# MTGO Update Seite (kannst du später auch rauswerfen, wenn du willst)
MTGO_URL = "https://mtgoupdate.com/"


def fetch_wizards_events():
    print("Hole Wizards Events (HTML Scraper)...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html",
    }

    resp = requests.get(WIZARDS_URL, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []

    # Struktur kann sich ändern – das hier ist ein pragmatischer Start:
    cards = soup.select("div.event-card")

    for card in cards:
        title_el = card.select_one(".event-card-title")
        date_el = card.select_one(".event-card-date")
        time_el = card.select_one(".event-card-time")
        store_el = card.select_one(".event-card-store")
        address_el = card.select_one(".event-card-address")

        if not title_el or not date_el:
            continue

        title = title_el.get_text(strip=True)
        date_str = date_el.get_text(strip=True)
        time_str = time_el.get_text(strip=True) if time_el else "00:00"

        # Versuche ein paar gängige Formate
        dt = None
        for fmt in ("%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", fmt)
                break
            except ValueError:
                continue
        if dt is None:
            continue

        store = store_el.get_text(strip=True) if store_el else ""
        address = address_el.get_text(strip=True) if address_el else ""

        e = Event()
        e.name = f"{title} – {store}" if store else title
        e.begin = dt
        e.location = address
        e.description = "WPN Event (Scraper)"

        events.append(e)

    print(f"Wizards Events gefunden: {len(events)}")
    return events


def fetch_mtgo_events():
    print("Hole MTGO Events...")

    events = []
    try:
        resp = requests.get(MTGO_URL)
    except Exception as e:
        print(f"Fehler beim Laden von MTGO: {e}")
        return events

    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("table tbody tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 4:
            continue

        name, format_, date_str, time_str = cols[:4]

        # Nur Modern-Events
        if "Modern" not in format_:
            continue

        dt_str = f"{date_str} {time_str}"
        try:
            start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        e = Event()
        e.name = f"MTGO {name} ({format_})"
        e.begin = start_dt
        e.description = "MTGO Modern Event"
        events.append(e)

    print(f"MTGO Events gefunden: {len(events)}")
    return events


def generate_ics():
    print("Erzeuge Kalender...")

    cal = Calendar()

    wizards = fetch_wizards_events()
    mtgo = fetch_mtgo_events()

    print("Wizards Events:", len(wizards))
    print("MTGO Events:", len(mtgo))

    for e in wizards:
        cal.events.add(e)

    for e in mtgo:
        cal.events.add(e)

    print("Schreibe magic.ics...")
    with open("magic.ics", "w", encoding="utf-8") as f:
        f.writelines(cal)

    print("Fertig! Datei erzeugt.")


if __name__ == "__main__":
    generate_ics()