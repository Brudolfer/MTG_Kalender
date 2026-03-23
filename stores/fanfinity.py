import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.fanfinity.gg/magic-the-gathering/"

def fetch_fanfinity_events():
    events = []

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Fanfinity Fehler:", e)
        return events

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select('div[data-elementor-type="loop-item"]')
    print(f"Fanfinity: Gefundene Loop-Items: {len(items)}")

    for item in items:
        # Titel
        title_tag = item.select_one("h1.elementor-heading-title a, h2.elementor-heading-title a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        url = title_tag["href"]

        # Datumsteile holen
        date_tags = item.select(".elementor-post-info__item--type-custom")

        if len(date_tags) < 2:
            continue

        # Tag = erstes Element
        day_text = date_tags[0].text.strip()

        # Monat + Jahr = zweites Element
        month_year_text = date_tags[1].text.strip()

        # Tag in int umwandeln
        try:
            day = int(day_text)
        except:
            print("Fanfinity: Konnte Tag nicht parsen:", day_text)
            continue

        # Monat + Jahr parsen
        try:
            month_year = datetime.strptime(month_year_text, "%B %Y")
        except:
            print("Fanfinity: Konnte Monat/Jahr nicht parsen:", month_year_text)
            continue

        # Kombiniertes Datum
        start = month_year.replace(day=day, hour=11, minute=0)
        end = month_year.replace(day=day, hour=20, minute=0)

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
