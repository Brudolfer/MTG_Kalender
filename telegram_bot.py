from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from telegram import Update
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re
import os
import subprocess

TZ = ZoneInfo("Europe/Berlin")
MANUAL_FILE = "manual_events.json"

# ---------------------------------------------------------
# Datei-Handling
# ---------------------------------------------------------
def load_manual_events():
    try:
        with open(MANUAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_manual_events(events):
    with open(MANUAL_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

def sync_to_github():
    try:
        subprocess.Popen(["python3", "sync_to_github.py"])
    except Exception as e:
        print("GitHub Sync Fehler:", e)

# ---------------------------------------------------------
# Event Parsing
# ---------------------------------------------------------
def parse_natural_event(text: str):
    text = text.strip()

    title = text.split(" am ")[0].strip()

    date_match = re.search(r"(\d{1,2})[.\-/](\d{1,2})(?:[.\-/](\d{2,4}))?", text)
    if not date_match:
        raise ValueError("Kein Datum gefunden.")

    day = int(date_match.group(1))
    month = int(date_match.group(2))
    year = int(date_match.group(3)) if date_match.group(3) else datetime.now(TZ).year

    time_match = re.search(r"(\d{1,2})[:.]?(\d{2})?\s*(?:–|-|bis)\s*(\d{1,2})[:.]?(\d{2})?", text)
    if time_match:
        sh = int(time_match.group(1))
        sm = int(time_match.group(2) or 0)
        eh = int(time_match.group(3))
        em = int(time_match.group(4) or 0)
    else:
        sh, sm, eh, em = 18, 0, 22, 0

    start = datetime(year, month, day, sh, sm, tzinfo=TZ)
    end = datetime(year, month, day, eh, em, tzinfo=TZ)

    loc_match = re.search(r"in\s+([A-Za-zÄÖÜäöüß\s]+)", text)
    location = loc_match.group(1).strip() if loc_match else "Unbekannt"

    return {
        "title": title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "location": location,
        "url": "",
        "description": text,
        "all_day": False,
        "source": "MANUAL"
    }

# ---------------------------------------------------------
# /events – Liste anzeigen
# ---------------------------------------------------------
async def list_events(update: Update, context):
    events = load_manual_events()

    if not events:
        await update.message.reply_text("Es sind keine Events gespeichert.")
        return

    msg = "📅 *Gespeicherte Events:*\n\n"
    for idx, ev in enumerate(events):
        msg += f"*{idx}*: {ev['title']} – {ev['start']} – {ev['location']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------------------------------------------------------
# /delete – Event löschen
# ---------------------------------------------------------
async def delete_event(update: Update, context):
    events = load_manual_events()

    if len(context.args) != 1:
        await update.message.reply_text("Bitte nutze: /delete <ID>")
        return

    try:
        idx = int(context.args[0])
    except:
        await update.message.reply_text("Ungültige ID.")
        return

    if idx < 0 or idx >= len(events):
        await update.message.reply_text("Diese ID existiert nicht.")
        return

    deleted = events.pop(idx)
    save_manual_events(events)
    sync_to_github()

    await update.message.reply_text(
        f"🗑️ Event gelöscht:\n"
        f"{deleted['title']} – {deleted['start']} – {deleted['location']}"
    )

# ---------------------------------------------------------
# Normaler Text → Event speichern
# ---------------------------------------------------------
async def handle_message(update: Update, context):
    text = update.message.text

    try:
        event = parse_natural_event(text)
    except Exception as e:
        await update.message.reply_text(f"Ich konnte das Event nicht verstehen: {e}")
        return

    events = load_manual_events()
    events.append(event)
    save_manual_events(events)
    sync_to_github()

    await update.message.reply_text(
        f"Event gespeichert:\n"
        f"📌 {event['title']}\n"
        f"📅 {event['start']}\n"
        f"📍 {event['location']}"
    )

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    token = os.environ["BOT_TOKEN"]
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("events", list_events))
    app.add_handler(CommandHandler("delete", delete_event))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()