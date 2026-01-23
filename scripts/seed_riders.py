# scripts/seed_riders.py

import click
import requests
from app import db
from app.models import Rider

def seed_riders(event_code):
    url = f"https://api.isuresults.eu/events/2026_{event_code}/competitors/"
    response = requests.get(url)
    response.raise_for_status()  # fail if request fails

    data = response.json()
    riders = []

    for entry in data:
        skater = entry.get("skater")
        if not skater:
            continue

        rider_id = skater.get("id")
        first_name = skater.get("firstName") or ""
        last_name = skater.get("lastName") or ""
        name = f"{first_name} {last_name}".strip()
        country = skater.get("country")
        gender = skater.get("gender")
        profile = skater.get("personalBestUrl")  # optional
        photo = skater.get("photo")

        riders.append({
            "id": rider_id,
            "name": name,
            "country": country,
            "gender": gender,
            "profile": profile,
            "photo": photo,
        })

    return riders


@click.command(name="seed-riders")
@click.argument("event_code")
def seed_riders_command(event_code):
    """Seed riders using the ISU API."""
    riders = seed_riders(event_code)
    added = 0

    for r in riders:
        if not Rider.query.get(r["id"]):
            db.session.add(
                Rider(
                    id=r["id"],
                    name=r["name"],
                    country=r["country"],
                    gender=r["gender"],
                    profile=r["profile"],
                    photo=r["photo"],
                )
            )
            added += 1

    db.session.commit()
    click.echo(f"Seeded {added} riders for event {event_code}")
