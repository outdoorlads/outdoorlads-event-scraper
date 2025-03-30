import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.outdoorlads.com/events?page={}"

def get_event_data(event):
    """Extract data from a single event element."""
    title = event.find("h2", class_="event-title").text.strip()
    date = event.find("span", class_="event-date").text.strip()
    start_time = event.find("span", class_="event-start-time").text.strip()
    region = event.find("span", class_="event-region").text.strip()
    location = event.find("span", class_="event-location").text.strip()
    event_type = event.find("span", class_="event-type").text.strip()
    availability = event.find("span", class_="event-availability").text.strip()
    waitlist = event.find("span", class_="event-waitlist").text.strip()
    summary = event.find("div", class_="event-summary").text.strip()
    link = event.find("a", class_="event-link")['href']
    
    return {
        "title": title,
        "date": date,
        "start_time": start_time,
        "region": region,
        "location": location,
        "event_type": event_type,
        "availability": availability,
        "waitlist": waitlist,
        "summary": summary,
        "link": link
    }

def scrape_events():
    """Scrape event data from the website."""
    events_data = []
    for page in range(1, 101):  # Adjust the range to scrape up to 100 pages
        url = BASE_URL.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = soup.find_all("div", class_="event")
        for event in events:
            event_data = get_event_data(event)
            events_data.append(event_data)
    
    return events_data

def save_to_csv(events_data, filename="events.csv"):
    """Save event data to a CSV file."""
    keys = events_data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(events_data)

if __name__ == "__main__":
    events_data = scrape_events()
    save_to_csv(events_data)
    print(f"Scraped {len(events_data)} events and saved to events.csv")
