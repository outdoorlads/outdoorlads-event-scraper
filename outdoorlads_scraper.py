import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.outdoorlads.com"
LISTING_URL = BASE_URL + "/events?page={}"
OUTPUT_FILE = "odl_events.json"


def get_event_links_from_listing(page_number):
    """Scrapes event links from a listing page."""
    url = LISTING_URL.format(page_number)
    print(f"Scraping listing page {page_number}: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select("a.events-listing__item")
    return [BASE_URL + link['href'] for link in links if link.get('href')]


def extract_event_details(event_url):
    """Extract full details from an individual event page."""
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
    location = get_text(".events-listing__location .field-location-text")
    region = "Central"  # You can try to infer this better or keep static for now
    availability = get_text(".event__attending p:nth-of-type(2)")
    waitlist = "0"  # Waitlist isn't shown explicitly unless full — adjust if logic added
    attending = get_text(".event__attending p:nth-of-type(1)").split()[0]
    summary = get_text(".field-description p")

    return {
        "Title": title,
        "Date": f"Saturday {date}",
        "Region": region,
        "Location": location if location != "Unknown" else "Unknown",
        "Event Type": event_type,
        "Availability": availability if availability else "Unknown",
        "Waitlist": waitlist,
        "Attending": attending,
        "Summary": summary if summary else "No description available.",
        "Link": event_url
    }


def scrape_all_events():
    all_events = []
    for page in range(0, 100):  # loop through up to 100 pages
        event_links = get_event_links_from_listing(page)
        if not event_links:
            break  # No more events
        for link in event_links:
            try:
                event_data = extract_event_details(link)
                all_events.append(event_data)
                time.sleep(0.5)  # Rate limiting
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
