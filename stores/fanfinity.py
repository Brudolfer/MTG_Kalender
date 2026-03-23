import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.fanfinity.gg/magic-the-gathering/"

def fetch_fanfinity_events():
    events = []

    response = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Jeder Event-Container ist ein Elementor-Section-Block
    containers = soup.select(".elementor-widget-wrap.elementor-element-populated section")

    for c in containers:
        # Titel + URL
        title_tag = c.select_one("h1.elementor-heading-title a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        url = title_tag["href"]

        # Datum (Fanfinity nutzt z.B. "May 2026")
        date_tag = c.select_one(".elementor-post-info__item--type-custom")
        date_text = date_tag.text.strip() if date_tag else None

        # Datum parsen
        parsed_date = None
        if date_text:
            try:
                parsed_date = datetime.strptime(date_text, "%B %Y")
            except:
                pass

        # Falls kein Datum erkannt → überspringen
        if not parsed_date:
            continue

        # Start/Ende setzen (ganzer Tag)
        start = parsed_date.replace(day=1, hour=9, minute=0)
        end = parsed_date.replace(day=1, hour=18, minute=0)

        events.append({
            "title": title,
            "url": url,
            "start": start,
            "end": end,
            "store": "Fanfinity",
            "location": "Online",
            "description": f"Event von Fanfinity: {title}\n{url}"
        })

    return events
