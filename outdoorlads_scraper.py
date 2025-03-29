import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from urllib.parse import urljoin

BASE_URL = "https://www.outdoorlads.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/120.0.0.0 Safari/537.36"
}

def fetch_event_details(event_url):
    response = requests.get(event_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    summary_el = soup.select_one('.event-description .field-items .field-item')
    summary = summary_el.text.strip() if summary_el else "No description available."

    start_time_el = soup.find("div", string="Start time")
    start_time = start_time_el.find_next('div').text.strip() if start_time_el else "N/A"

    availability_el = soup.select_one('.availability')
    availability = availability_el.text.strip() if availability_el else "Unknown"

    waitlist = "0"
    if 'waitlist' in availability.lower():
        waitlist = ''.join(filter(str.isdigit, availability.lower().split('waitlist')[1]))

    return summary, start_time, availability, waitlist

def scrape_events():
    events_list = []
    page = 0

    while True:
        page_url = f"{BASE_URL}/events?page={page}"
        print(f"Scraping page {page}: {page_url}")

        res = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Save debug file for first page
        if page == 0:
            with open("debug_page_0.html", "w", encoding="utf-8") as debug_file:
                debug_file.write(res.text)

        events = soup.select('div.views-row')
        if not events:
            print("No more events found. Ending pagination.")
            break

        for event in events:
            title_el = event.select_one('.views-field-title a')
            title = title_el.text.strip() if title_el else "No title"

            relative_link = title_el.get('href', '')
            link = urljoin(BASE_URL, relative_link)

            date_el = event.select_one('.event-date')
            date = date_el.text.strip() if date_el else "No date"

            location_el = event.select_one('.event-location')
            location = location_el.text.strip() if location_el else "No location"

            event_type_el = event.select_one('.field-event-type')
            event_type = event_type_el.text.strip() if event_type_el else "Not specified"

            summary, start_time, availability, waitlist = fetch_event_details(link)
            time.sleep(1)  # Be polite to the server

            events_list.append({
                "title": title,
                "date": date,
                "start_time": start_time,
                "location": location,
                "event_type": event_type,
                "availability": availability,
                "waitlist": waitlist,
                "summary": summary,
                "link": link
            })

        page += 1
        if page >= 100:
            print("Reached 100-page limit. Ending scraping.")
            break

    df = pd.DataFrame(events_list)
    df['scraped_at'] = datetime.now()
    df.to_json('odl_events.json', orient='records', indent=2)
    print(f"Scraped {len(events_list)} events successfully.")

if __name__ == "__main__":
    scrape_events()
