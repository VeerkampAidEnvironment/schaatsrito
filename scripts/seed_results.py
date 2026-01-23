# scripts/seed_results.py

import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from app import db
from app.models import Event, Rider, EventResult

from scripts.normalize import normalize_name


def scrape_results(event_code, event_id):
    url = (
        f"https://live.isuresults.eu/events/2026_{event_code}"
        f"/competition/{event_id}/results"
    )

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # wait until at least one rider name appears
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".col-xs-9.col-sm-9.col-md-9.name")
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    names = []
    for el in soup.select(".col-xs-9.col-sm-9.col-md-9.name"):
        raw_name = el.get_text(strip=True)
        name = normalize_name(raw_name)
        if name:
            names.append(name)

    return names


@click.command("seed-results")
@click.argument("event_code")
def seed_results(event_code):
    """Seed event results using Selenium."""
    events = Event.query.all()

    total_added = 0

    for event in events:
        try:
            names = scrape_results(event_code, event.id)
        except Exception:
            click.echo(f"Skipping event {event.id} (no results)")
            continue

        # Remove existing results for this event (idempotent seeding)
        EventResult.query.filter_by(event_id=event.id).delete()

        position = 1
        for name in names:
            rider = Rider.query.filter_by(name=name).first()
            if not rider:
                click.echo(f"Unknown rider: {name}")
                continue

            db.session.add(
                EventResult(
                    event_id=event.id,
                    rider_id=rider.id,
                    position=position,
                )
            )
            total_added += 1
            position += 1

    db.session.commit()
    click.echo(f"Seeded {total_added} result entries")
