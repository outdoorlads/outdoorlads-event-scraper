import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://www.outdoorlads.com"
LISTING_URL = BASE_URL + "/events?page={}"
OUTPUT_FILE = "odl_events.json"

REGION_MAP = {
    "ENGLAND (Central)": "Central",
    "ENGLAND (North East)": "North East",
    "ENGLAND (North West)": "North West",
    "ENGLAND (South East)": "South East",
    "ENGLAND (South West)": "South West",
    "WALES (North)": "North Wales",
    "WALES (South)": "South Wales",
    "SCOTLAND": "Scotland",
    "NORTHERN IRELAND": "Northern Ireland",
    "REST OF EUROPE": "EU",
    "REST OF WORLD": "Worldwide",
    "Online": "Online"
}


def get_event_links_from_listing(page_number):
    url = LISTING_URL.format(page_number)
    print(f"Scraping listing page {page_number}: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select("a.events-listing__item")
    return [BASE_URL + link['href'] for link in links if link.get('href')]


def clean_number(text):
    match = re.search(r'\d+', text)
    return match.group(0) if match else "0"


def map_region(raw_text):
    for key, value in REGION_MAP.items():
        if key.lower() in raw_text.lower():
            return value
    return "Unknown"


def extract_event_details(event_url):
    print(f"Scraping event: {event_url}")
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_text(selector):
        el = soup.select_one(selector)
        return el.text.strip() if el else "Unknown"

    title = get_text("h1.page__title div.field.title")
    month = get_text("div.event-date span.event-date__month")
    day = get_text("div.event-date span.event-date__day")
    year = get_text("div.event-date div")
    date = f"{month} {day} {year}" if "Unknown" not in [month, day, year] else "Unknown"

    event_type = get_text(".hero__event-type .field.name")
    region_text = soup.select_one("meta[property='og:description']")
    region = map_region(region_text['content']) if region_text and region_text.has_attr('content') else "Unknown"

    summary_el = soup.select_one(".field-description")
    summary = summary_el.get_text(separator="\n", strip=True) if summary_el else "No description available."

    availability = get_text(".event__attending p:nth-of-type(2)")
    attending = get_text(".event__attending p:nth-of-type(1)")
    attending_number = clean_number(attending)
    availability_number = clean_number(availability)

    # Add distance & difficulty if available
    difficulty = get_text(".field.field-event-difficulty-desc")
    difficulty = difficulty if difficulty != "Unknown" else ""

    return {
        "Title": title,
        "Date": f"Saturday {date}",
        "Region": region,
        "Event Type": event_type,
        "Places Left": availability_number,
        "Waitlist": "0",  # Add dynamic logic later if needed
        "People Attending": attending_number,
        "Summary": summary,
        "Difficulty & Distance": difficulty,
        "Link": event_url
    }


def scrape_all_events():
    all_events = []
    for page in range(0, 100):
        event_links = get_event_links_from_listing(page)
        if not event_links:
            break
        for link in event_links:
            try:
                event_data = extract_event_details(link)
                all_events.append(event_data)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error scraping {link}: {e}")
    return all_events


def save_to_json(events):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(events)} events to {OUTPUT_FILE}")


if __name__ == "__main__":
    events = scrape_all_events()
    save_to_json(events)
