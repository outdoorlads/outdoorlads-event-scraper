import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

BASE_URL = "https://www.outdoorlads.com"

def get_event_details(link):
    try:
        res = requests.get(link)
        soup = BeautifulSoup(res.content, 'html.parser')
        summary = soup.select_one('.event-description .field-items .field-item').text.strip() if soup.select_one('.event-description .field-items .field-item') else ''
        time_el = soup.find(text="Start time")
        if time_el:
            time_row = time_el.find_parent('div')
            start_time = time_row.find_next('div').text.strip() if time_row else ''
        else:
            start_time = ''
        return start_time, summary
    except Exception:
        return '', ''

def fetch_events():
    page = 0
    results = []

    while True:
        url = f"{BASE_URL}/events?field_event_type_target_id=All&page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')

        events = soup.select('.views-row')
        if not events:
            break

        for event in events:
            title_el = event.select_one('.event-title a')
            link = BASE_URL + title_el['href'] if title_el else ''
            title = title_el.text.strip() if title_el else ''
            date = event.select_one('.event-date').text.strip() if event.select_one('.event-date') else ''
            location = event.select_one('.event-location').text.strip() if event.select_one('.event-location') else ''
            availability = event.select_one('.availability').text.strip() if event.select_one('.availability') else 'Unknown'

            # Fetch additional details from individual event page
            start_time, summary = get_event_details(link)
            time.sleep(1)  # be kind to the server

            results.append({
                'title': title,
                'link': link,
                'date': date,
                'start_time': start_time,
                'location': location,
                'availability': availability,
                'summary': summary
            })

        page += 1

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = fetch_events()
    df['scraped_at'] = datetime.now()
    df.to_json('odl_events.json', orient='records', indent=2)
