import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
from datetime import datetime

BASE_URL = "https://www.outdoorlads.com/events?page={}"

def get_event_links(page_url):
    res = requests.get(page_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = [urljoin("https://www.outdoorlads.com", a['href'])
             for a in soup.select('a.events-listing__item')]
    print(f"Found {len(links)} event links on {page_url}")
    return links

def get_event_details(event_url):
    res = requests.get(event_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.select_one('h1').text.strip()

    date_el = soup.select_one('.date-display-single')
    date = date_el.text.strip() if date_el else "Unknown"

    start_time_label = soup.find('div', string="Start time")
    start_time = start_time_label.find_next_sibling('div').text.strip() if start_time_label else "Unknown"

    region_label = soup.find('div', string="Region")
    region = region_label.find_next_sibling('div').text.strip() if region_label else "Unknown"

    location_label = soup.find('div', string="Venue")
    location = location_label.find_next_sibling('div').text.strip() if location_label else "Unknown"

    event_type_label = soup.find('div', string="Event type")
    event_type = event_type_label.find_next_sibling('div').text.strip() if event_type_label else "Unknown"

    availability_el = soup.select_one('.availability')
    availability = availability_el.text.strip() if availability_el else "Unknown"

    waitlist = "0"
    if 'waitlist' in availability.lower():
        waitlist = ''.join(filter(str.isdigit, availability.lower().split('waitlist')[1]))

    summary_el = soup.select_one('.event-description .field-item')
    summary = summary_el.text.strip() if summary_el else "No description available."

    return {
        "Title": title,
        "Date": date,
        "Start Time": start_time,
        "Region": region,
        "Location": location,
        "Event Type": event_type,
        "Availability": availability,
        "Waitlist": waitlist,
        "Summary": summary,
        "Link": event_url
    }

def scrape_events():
    all_events = []
    for page in range(0, 100):
        page_url = BASE_URL.format(page)
        print(f"Scraping page {page}: {page_url}")
        event_links = get_event_links(page_url)

        if not event_links:
            print("No more events, stopping.")
            break

        for event_link in event_links:
            print(f"Scraping event: {event_link}")
            try:
                event_details = get_event_details(event_link)
                all_events.append(event_details)
                time.sleep(1)  # Be respectful
            except Exception as e:
                print(f"Error scraping {event_link}: {e}")

    return all_events

def save_to_json(events, filename="odl_events.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=2, ensure_ascii=False)
    print(f"{len(events)} events saved to {filename}")

if __name__ == "__main__":
    events_data = scrape_events()
    if events_data:
        save_to_json(events_data)
    else:
        print("No events were scraped.")
