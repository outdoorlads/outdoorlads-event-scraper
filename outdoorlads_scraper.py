import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

BASE_URL = "https://www.outdoorlads.com"

def extract_availability(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

def extract_event_data(event_url):
    res = requests.get(event_url)
    soup = BeautifulSoup(res.content, 'html.parser')

    title = soup.find("div", class_="field title").get_text(strip=True)
    date_parts = soup.select_one("div.event-date")
    day = date_parts.select_one("span.event-date__day").text.strip()
    month = date_parts.select_one("span.event-date__month").text.strip()
    year = date_parts.find(text=re.compile(r'\d{4}')).strip()
    full_date = f"{day} {month} {year}"

    region_text = soup.select_one("div.field-description").text.lower()
    region = "Unknown"
    for r in ['North West', 'Central', 'South East', 'South West', 'Central Scotland', 'North Wales']:
        if r.lower() in region_text:
            region = r
            break

    event_type = soup.select_one("div.event-type .name")
    event_type = event_type.text.strip() if event_type else "Unknown"

    summary = soup.select_one("div.field-description")
    summary = summary.get_text(strip=True).split("\n")[0] if summary else "No description available."

    attending_text = soup.find("div", class_="event__attending")
    attending = 0
    availability = 0
    waitlist = 0
    if attending_text:
        lines = attending_text.get_text(separator="|").split("|")
        for line in lines:
            if "attending" in line:
                attending = extract_availability(line)
            elif "places left" in line:
                availability = extract_availability(line)
            elif "waitlist" in line:
                waitlist = extract_availability(line)

    return {
        "Title": title,
        "Date": full_date,
        "Region": region,
        "Event Type": event_type,
        "Availability": availability,
        "Waitlist": waitlist,
        "Attending": attending,
        "Summary": summary,
        "Link": event_url
    }

def get_event_links():
    res = requests.get(f"{BASE_URL}/events")
    soup = BeautifulSoup(res.content, 'html.parser')
    event_links = []
    for link in soup.select("a.event-teaser__image-link"):
        href = link.get("href")
        if href and href.startswith("/events/"):
            full_url = BASE_URL + href
            event_links.append(full_url)
    return event_links

def main():
    all_event_data = []
    links = get_event_links()
    for link in links:
        try:
            data = extract_event_data(link)
            all_event_data.append(data)
        except Exception as e:
            print(f"Error parsing {link}: {e}")

    with open("outdoorlads_events.json", "w", encoding="utf-8") as f:
        json.dump(all_event_data, f, ensure_ascii=False, indent=2)
    print(f"Scraped {len(all_event_data)} events.")

if __name__ == "__main__":
    main()
