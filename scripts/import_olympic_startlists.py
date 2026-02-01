# scripts/import_olympic_startlists.py

# =========================
# Imports
# =========================
import re
import json
import requests
from unidecode import unidecode
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rapidfuzz import process, fuzz  # ✅ NEW

from app import create_app, db
from app.models import Rider, EventStartlistProvisional


# =========================
# Static Olympic Events
# =========================
EVENTS = [
    # Men’s events
    {"id": 8, "name": "500 m Men", "discipline": "500 m", "start_datetime": "2026-02-14T16:00:00", "gender": "M"},
    {"id": 4, "name": "1000 m Men", "discipline": "1000 m", "start_datetime": "2026-02-11T18:30:00", "gender": "M"},
    {"id": 15, "name": "1500 m Men", "discipline": "1500 m", "start_datetime": "2026-02-19T16:30:00", "gender": "M"},
    {"id": 2, "name": "5000 m Men", "discipline": "5000 m", "start_datetime": "2026-02-08T16:00:00", "gender": "M"},
    {"id": 6, "name": "10,000 m Men", "discipline": "10000 m", "start_datetime": "2026-02-13T16:00:00", "gender": "M"},
    {"id": 21, "name": "Mass Start Men", "discipline": "Mass Start", "start_datetime": "2026-02-21T15:00:00", "gender": "M"},
    {"id": 13, "name": "Team Pursuit Men", "discipline": "Team Pursuit", "start_datetime": "2026-02-17T14:30:00", "gender": "M"},
    # Women’s events
    {"id": 10, "name": "500 m Women", "discipline": "500 m", "start_datetime": "2026-02-15T16:00:00", "gender": "F"},
    {"id": 3, "name": "1000 m Women", "discipline": "1000 m", "start_datetime": "2026-02-09T17:30:00", "gender": "F"},
    {"id": 16, "name": "1500 m Women", "discipline": "1500 m", "start_datetime": "2026-02-20T16:30:00", "gender": "F"},
    {"id": 1, "name": "3000 m Women", "discipline": "3000 m", "start_datetime": "2026-02-07T16:00:00", "gender": "F"},
    {"id": 5, "name": "5000 m Women", "discipline": "5000 m", "start_datetime": "2026-02-12T16:30:00", "gender": "F"},
    {"id": 22, "name": "Mass Start Women", "discipline": "Mass Start", "start_datetime": "2026-02-21T15:00:00", "gender": "F"},
    {"id": 14, "name": "Team Pursuit Women", "discipline": "Team Pursuit", "start_datetime": "2026-02-17T14:30:00", "gender": "F"},
]


# =========================
# Manual EventDescription → local event ID mapping
# =========================
EVENT_DESCRIPTION_TO_ID = {
    "Women's 500m": 10,
    "Women's 1000m": 3,
    "Women's 1500m": 16,
    "Women's 3000m": 1,
    "Women's 5000m": 5,
    "Women's Mass Start": 22,
    "Women's Team Pursuit": 14,
    "Men's 500m": 8,
    "Men's 1000m": 4,
    "Men's 1500m": 15,
    "Men's 5000m": 2,
    "Men's 10000m": 6,
    "Men's Mass Start": 21,
    "Men's Team Pursuit": 13,
}


# =========================
# Helpers
# =========================
def normalize(text: str) -> str:
    text = unidecode(text).lower()
    text = text.replace("-", " ")  # ✅ important for hyphenated surnames
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    return session


# =========================
# Main
# =========================
def main():
    app = create_app()

    with app.app_context():
        session = create_session()

        # -------------------------------------------------
        # 1. Load Olympic athletes
        # -------------------------------------------------
        with open("data/olympics_athletes.json", "r", encoding="utf-8") as f:
            olympics_data = json.load(f)

        athletes = olympics_data["Data"]
        olympic_skaters = []

        for a in athletes:
            events = []
            for ev in a.get("Events", []):
                if ev.get("DisciplineCode") != "SSK":
                    continue

                events.append({
                    "eventCode": ev["EventCode"],
                    "discipline": ev["EventDescription"],
                    "gender": a["GenderCode"],
                })

            if not events:
                continue

            full_name = f"{a['GivenName']} {a['FamilyName']}"
            olympic_skaters.append({
                "name": full_name,
                "normalized": normalize(full_name),
                "noc": a["OrganisationCode"],
                "gender": a["GenderCode"],
                "events": events,
            })

        print(f"✔ Olympic skaters loaded: {len(olympic_skaters)}")

        # -------------------------------------------------
        # 2. Fetch ISU skaters
        # -------------------------------------------------
        isu_skaters = []

        for page in range(1, 29):
            r = session.get(
                "https://api.isuresults.eu/skaters/",
                params={"page": page},
                timeout=30
            )
            r.raise_for_status()

            for sk in r.json()["results"]:
                full_name = f"{sk['firstName']} {sk['lastName']}"
                isu_skaters.append({
                    "id": sk["id"],
                    "name": full_name,
                    "normalized": normalize(full_name),
                })

        isu_names = [sk["normalized"] for sk in isu_skaters]
        isu_by_normalized = defaultdict(list)

        for sk in isu_skaters:
            isu_by_normalized[sk["normalized"]].append(sk)

        # -------------------------------------------------
        # 3. Fuzzy match skaters
        # -------------------------------------------------
        MATCH_THRESHOLD = 60

        matched = []
        unmatched = []

        for o in olympic_skaters:
            result = process.extractOne(
                o["normalized"],
                isu_names,
                scorer=fuzz.token_sort_ratio
            )

            if not result:
                unmatched.append(o["name"])
                continue

            match_name, score, _ = result

            if score >= MATCH_THRESHOLD:
                matched.append((o, isu_by_normalized[match_name][0], score))
                if score < 95:
                    print(f"⚠️ Low-confidence match ({score}%): {o['name']} → {isu_by_normalized[match_name][0]['name']}")
            else:
                unmatched.append(o["name"])

        print(f"✔ Matched skaters: {len(matched)}")
        print(f"⚠️ Unmatched skaters: {len(unmatched)}")

        # -------------------------------------------------
        # 4. Insert provisional startlists
        # -------------------------------------------------
        inserted = 0

        for o, isu, score in matched:
            rider = Rider.query.filter_by(id=isu["id"]).first()

            if not rider:
                continue

            for ev in o["events"]:
                event_id = EVENT_DESCRIPTION_TO_ID.get(ev["discipline"])

                if not event_id:
                    print(f"⚠️ No event ID mapping for {ev['discipline']}")
                    continue

                exists = EventStartlistProvisional.query.filter_by(
                    event_id=event_id,
                    rider_id=rider.id
                ).first()

                if exists:
                    continue

                db.session.add(EventStartlistProvisional(
                    event_id=event_id,
                    rider_id=rider.id
                ))
                inserted += 1

        db.session.commit()
        print(f"\n✔ Inserted {inserted} provisional startlist rows")


# =========================
# CLI Command
# =========================
import click
from flask.cli import with_appcontext

@click.command("import_olympic_startlists")
@with_appcontext
def import_olympic_startlists_command():
    """Fetch Olympic speed skaters, match to ISU, and populate provisional startlists."""
    main()
