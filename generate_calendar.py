from datetime import datetime
from ics import Calendar, Event

from bb_spiele import fetch_bb_spiele_events
from funtainment import fetch_funtainment_events

def is_modern_or_rcq(title: str) -> bool:
    title = title.lower()

    include = [
        "modern",
        "rcq",
        "regional championship qualifier",
        "qualifier",
    ]

    exclude = [
        "commander",
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
    ]

    if any(x in title for x in exclude):
        return False

    return any(x in title for x in include)

def main():
    print("Script gestartet")
    print("Erzeuge Kalender...")

    all_events = []

    # BB-Spiele
    all_events.extend([
        ev for ev in fetch_bb_spiele_events()
        if is_modern_or_rcq(ev["title"])
    ])

    # Funtainment
    all_events.extend([
        ev for ev in fetch_funtainment_events()
        if is_modern_or_rcq(ev["title"])
    ])

    print(f"Gesamtanzahl Events: {len(all_events)}")

    cal = Calendar()

    for ev in all_events:
        e = Event()
        e.name = ev["title"]
        e.begin = ev["start"]
        e.end = ev["end"]
        e.location = ev["location"]
        e.url = ev["url"]
        e.description = ev["description"]
        cal.events.add(e)

    with open("magic.ics", "w", encoding="utf-8") as f:
        f.writelines(cal)

    print("ICS erzeugt: magic.ics")

if __name__ == "__main__":
    main()
