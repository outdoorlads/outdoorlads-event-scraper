import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

BASE_URL = "https://www.outdoorlads.com"
LISTING_URL = f"{BASE_URL}/events"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com"
}

def get_event_details(link):
    try:
        res = requests.get(link, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        summary_el = soup.select_one('.event-description .field-items .field-item')
        summary = summary_el.text.strip() if summary_el else ''

        time_el = soup.find(text="Start time")
        if time_el:
            time_row = time_el.find_parent('div')
            start_time = time_row.find_next('div').text.strip() if time_row else ''
        else:
            start_time = ''

        availability_el = soup.find("div", class_="availability")
        availability = availability_el.text.strip() if availability_el else "Unknown"

        waitlist = "0"
        if "waitlist" in availability.lower():
            waitlist = ''.join(filter(str.isdigit, availability.split("waitlist")[1]))

        return start_time, summary, availability, waitlist
    except Exception as e:
        print(f"Error getting details from {link}: {e}")
        return '', '', 'Unknown', '0'

def fetch_events():
    res = requests.get(LISTING_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.content, 'html.parser')

    events = soup.select('.view-content > div')
    results = []

    for event in events:
        title_el = event.select_one('.field-content a')
        title = title_el.text.strip() if title_el else ''
        link = BASE_URL + title_el['href'] if title_el else ''

        date_month = event.select_one('.events-listing__month')
        date_day = event.select_one('.events-listing__day')
        date_year = event.select_one('.tw-text-md')

        if date_month and date_day and date_year:
            date_str = f"{date_day.text.strip()} {date_month.text.strip()} {date_year.text.strip()}"
        else:
            date_str = ''

        location_el = event.select_one('.event-location')
        location = location_el.text.strip() if location_el else ''

        event_type_el = event.select_one('.event-type')
        event_type = event_type_el.text.strip() if event_type_el else ''

        # Visit individual event page
        start_time, summary, availability, waitlist = get_event_details(link)
        time.sleep(1)

        results.append({
            'title': title,
            'link': link,
            'date': date_str,
            'start_time': start_time,
            'location': location,
            'event_type': event_type,
            'availability': availability,
            'waitlist': waitlist,
            'summary': summary
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = fetch_events()
    df['scraped_at'] = datetime.now()
    df.to_json('odl_events.json', orient='records', indent=2)
