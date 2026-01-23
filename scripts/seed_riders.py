# scripts/seed_riders.py

import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from app import db
from app.models import Rider
from scripts.normalize import normalize_name

def seed_riders(event_code):
    url = f"https://live.isuresults.eu/events/2026_{event_code}/competitors"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".competitor-item-wrapper")
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    riders = []
    for row in soup.select(".competitor-item-wrapper"):
        try:
            rider_id = int(
                row.select_one(".competitor-index-col.col-index").text.strip()
            )
            name_el = row.select_one(".competitor-name-col a")
            raw_name = name_el.text.strip()
            profile = name_el.get("href") if name_el else None

            name = normalize_name(raw_name)
            gender_el = row.select_one(".competitor-gender-col")
            gender = gender_el.text.strip() if gender_el else None
            country_el = row.select_one(".divider-country-col")
            country = country_el.text.strip() if country_el else None

            riders.append(
                {
                    "id": rider_id,
                    "name": name,
                    "country": country,
                    "profile": profile,
                    "gender": gender,
                }
            )

        except Exception:
            pass

    return riders


@click.command(name="seed-riders")
@click.argument("event_code")
def seed_riders_command(event_code):
    """Seed riders using Selenium."""
    riders = seed_riders(event_code)

    added = 0
    for r in riders:
        if not Rider.query.get(r["id"]):
            db.session.add(
                Rider(
                    id=r["id"],
                    name=r["name"],
                    country=r["country"],
                    profile=r["profile"],
                    gender=r["gender"],
                )
            )
            added += 1

    db.session.commit()
    click.echo(f"Seeded {added} riders for event {event_code}")



