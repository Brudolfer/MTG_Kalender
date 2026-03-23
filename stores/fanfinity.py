import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.fanfinity.gg/magic-the-gathering/"

def scrape_fanfinity_events():
    events = []

    response = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Alle Event-Container finden
    containers = soup.select(".elementor-widget-wrap.elementor-element-populated section")

    for c in containers:
        # Titel
        title_tag = c.select_one("h1.elementor-heading-title a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        url = title_tag["href"]

        # Datum
        date_tag = c.select_one(".elementor-post-info__item--type-custom")
        if date_tag:
            date_text = date_tag.text.strip()
        else:
            date_text = None

        # Datum parsen (Fanfinity nutzt z.B. "May 2026")
        try:
            parsed_date = datetime.strptime(date_text, "%B %Y")
        except:
            parsed_date = None

        events.append({
            "title": title,
            "url": url,
            "date": parsed_date,
            "source": "Fanfinity"
        })

    return events
