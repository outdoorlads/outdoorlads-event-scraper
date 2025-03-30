import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import time

BASE_URL = "https://www.outdoorlads.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/120.0.0.0 Safari/537.36"
}

events = []

for page_num in range(0, 100):
    print(f"Scraping page {page_num}...")
    page_url = f"{BASE_URL}/events?page={page_num}"
    page_response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(page_response.content, "html.parser")

    event_listings = soup.select('div.views-row')
    
    if not event_listings:
        print("No more events found, stopping.")
        break

    for event in event_listings:
        link_tag = event.select_one('.views-field-title a')
        if link_tag:
            event_link = urljoin(BASE_URL, link_tag['href'])
            event_title = link_tag.text.strip()

            event_page_response = requests.get(event_link, headers=headers)
            event_soup = BeautifulSoup(event_page_response.content, "html.parser")

            # Event details
            date = event_soup.select_one('.date-display-single').text.strip() if event_soup.select_one('.date-display-single') else "Unknown"
            
            start_time_label = event_soup.find('div', string="Start time")
            start_time = start_time_label.find_next_sibling('div').text.strip() if start_time_label else "Unknown"
            
            region_label = event_soup.find('div', string="Region")
            region = region_label.find_next_sibling('div').text.strip() if region_label else "Unknown"

            location_label = event_soup.find('div', string="Venue")
            location = location_label.find_next_sibling('div').text.strip() if location_label else "Unknown"

            event_type_label = event_soup.find('div', string="Event type")
            event_type = event_type_label.find_next_sibling('div').text.strip() if event_type_label else "Unknown"

            availability_el = event_soup.select_one('.availability')
            availability = availability_el.text.strip() if availability_el else "Unknown"

            waitlist = "0"
            if 'waitlist' in availability.lower():
                waitlist = ''.join(filter(str.isdigit, availability.lower().split('waitlist')[1]))

            summary_el = event_soup.select_one('.event-description .field-item')
            summary = summary_el.text.strip() if summary_el else "No description available."

            # Structured event data
            event_data = {
                "Title": event_title,
                "Date": date,
                "Start Time": start_time,
                "Region": region,
                "Location": location,
                "Event Type": event_type,
                "Availability": availability,
                "Waitlist": waitlist,
                "Summary": summary,
                "Link": event_link
            }

            events.append(event_data)
            print(f"Scraped event: {event_title}")
            time.sleep(1)  # respectful scraping delay

# Saving the results to a nicely formatted text file
with open("OutdoorLads_events.txt", "w", encoding="utf-8") as file:
    for event in events:
        file.write(f"{event['Title']}\n")
        file.write(f"Date: {event['Date']}\n")
        file.write(f"Start Time: {event['Start Time']}\n")
        file.write(f"Region: {event['Region']}\n")
        file.write(f"Location: {event['Location']}\n")
        file.write(f"Event Type: {event['Event Type']}\n")
        file.write(f"Availability: {event['Availability']}\n")
        file.write(f"Waitlist: {event['Waitlist']}\n")
        file.write(f"Summary: {event['Summary']}\n")
        file.write(f"Link: {event['Link']}\n")
        file.write("-" * 40 + "\n")

print(f"\nScraping completed. {len(events)} events saved to OutdoorLads_events.txt")
