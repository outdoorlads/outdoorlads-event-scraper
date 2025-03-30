import requests
from bs4 import BeautifulSoup
import json
import re

# Function to extract integer from availability string
def extract_availability(availability_text):
    match = re.search(r'\d+', availability_text)
    return int(match.group()) if match else 0

# URL of the OutdoorLads events page
url = 'https://www.outdoorlads.com/events'

# Send a GET request to the URL
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; YourBot/1.0; +http://yourdomain.com/bot)'
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise an error for bad status codes

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all event elements (update the selector based on the actual HTML structure)
events = soup.find_all('div', class_='event-class')  # Replace 'event-class' with the actual class name

# Initialize a list to store event data
event_data = []

# Loop through each event element to extract data
for event in events:
    title = event.find('h2').get_text(strip=True)  # Adjust the tag and class as needed
    region = event.find('div', class_='region-class').get_text(strip=True)  # Adjust as needed
    availability_text = event.find('div', class_='availability-class').get_text(strip=True)  # Adjust as needed
    availability = extract_availability(availability_text)

    # Append the extracted data to the list
    event_data.append({
        'title': title,
        'region': region,
        'availability': availability
    })

# Define the path to the JSON file
json_file_path = 'outdoorlads_events.json'

# Write the fresh data to the JSON file
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(event_data, json_file, ensure_ascii=False, indent=4)

print(f"Data has been successfully written to {json_file_path}")
