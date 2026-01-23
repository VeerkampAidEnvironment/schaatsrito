import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from app import db
from app.models import Event, Rider, EventStartlist

from scripts.normalize import normalize_name


def scrape_startlist(event_code, event_id):
    url = (
        f"https://live.isuresults.eu/events/2026_{event_code}"
        f"/competition/{event_id}/start-list"
    )
    print(url)
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


@click.command("seed-startlists")
@click.argument("event_code")
def seed_startlists(event_code):
    """Seed event start lists using Selenium."""
    events = Event.query.all()

    total_added = 0

    for event in events:
        try:
            names = scrape_startlist(event_code, event.id)
        except Exception:
            click.echo(f"Skipping event {event.id} (no start list)")
            continue

        for name in names:
            rider = Rider.query.filter_by(name=name).first()
            if not rider:
                click.echo(f"Unknown rider: {name}")
                continue

            exists = EventStartlist.query.filter_by(
                event_id=event.id,
                rider_id=rider.id,
            ).first()

            if exists:
                continue

            db.session.add(
                EventStartlist(
                    event_id=event.id,
                    rider_id=rider.id,
                )
            )
            total_added += 1

    db.session.commit()
    click.echo(f"Seeded {total_added} startlist entries")

