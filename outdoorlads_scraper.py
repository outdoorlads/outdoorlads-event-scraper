# -*- coding: utf-8 -*-
"""
OutdoorLads Event Scraper

This script scrapes event data from the OutdoorLads website (outdoorlads.com/events).
It handles pagination on the main event list and then visits each individual
event page to extract detailed information.

DISCLAIMER:
- ALWAYS check outdoorlads.com/robots.txt and their Terms of Service before running.
- Scraping may be against their terms; proceed at your own risk.
- Use responsibly: Adjust DELAYS to avoid overloading their server.
- Website structure WILL change. The CSS selectors below are examples and
  MUST be updated by inspecting the live website's HTML using browser
  developer tools (Right-click -> Inspect).
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urljoin # To construct absolute URLs
import re # For potentially extracting numbers
import os # To construct file paths relative to the script

# --- Configuration ---
BASE_URL = 'https://www.outdoorlads.com'
EVENTS_LIST_PATH = '/events'
# IMPORTANT: Identify your scraper responsibly! Replace with your details.
# Using a generic user agent can sometimes help avoid blocks, but a custom one is more transparent.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    # Alternatively, be more specific (replace with YOUR details):
    # 'User-Agent': 'OutdoorLadsEventDataCollector/1.1 (For AI Project; contact: your-email@example.com; +https://github.com/your-username/your-repo)'
}
# DELAYS - Increase if you get blocked or want to be more respectful
DELAY_LIST_PAGE = 7  # Seconds between requests for list pages (e.g., /events?page=1)
DELAY_EVENT_PAGE = 4 # Seconds between requests for individual event pages
MAX_PAGES_TO_TRY = 100 # Safety limit for pagination, adjust as needed
OUTPUT_FILENAME = 'outdoorlads_events.csv'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILEPATH = os.path.join(SCRIPT_DIR, OUTPUT_FILENAME)


# --- Helper Function to Get Soup ---
def get_soup(url):
    """Fetches a URL and returns a BeautifulSoup object, handles errors."""
    try:
        print(f"Fetching: {url}")
        # Consider adding proxies or rotating user-agents if facing blocks,
        # but that adds complexity and potential cost.
        response = requests.get(url, headers=HEADERS, timeout=25) # Increased timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        # Using lxml parser if installed - generally faster
        soup = BeautifulSoup(response.text, 'lxml')
        return soup
    except ImportError: # Fallback if lxml not installed
         soup = BeautifulSoup(response.text, 'html.parser')
         return soup
    except requests.exceptions.Timeout:
        print(f"Timeout error fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None

# --- Function to Scrape Details from a Single Event Page ---
def scrape_event_details(event_url):
    """Scrapes the required details from an individual event page."""
    soup = get_soup(event_url)
    if not soup:
        return None

    # Use a dictionary with default N/A values
    details = {
        'Title': 'N/A', 'Date': 'N/A', 'Start Time': 'N/A', 'Region': 'N/A',
        'Location': 'N/A', 'EventType': 'N/A', 'Availability': 'N/A',
        'Waitlist': 'N/A', 'Summary': 'N/A', 'Link': event_url
    }

    # --- !!! CRITICAL: UPDATE THESE SELECTORS !!! ---
    # Inspect the HTML of actual event pages using browser developer tools.
    # These examples are highly likely to be INCORRECT for the current site.
    try:
        # Event Title (Example: <h1 class="page-title">Event Name</h1>)
        title_tag = soup.find('h1', class_='page-title') # <<< CHECK SELECTOR
        if title_tag: details['Title'] = title_tag.text.strip()

        # Details Block (Example: <div class="event-info">...</div> or <aside>...)
        details_block = soup.find('div', class_='event-details-sidebar') # <<< CHECK SELECTOR
        if not details_block:
             details_block = soup.find('aside', id='event-sidebar') # <<< ALTERNATIVE GUESS - CHECK

        if details_block:
            # Date/Time (Example: <span class="event-date">Sat 20 Apr 2025</span> <span class="event-time">10:00am</span>)
            date_tag = details_block.find('span', class_='event-date') # <<< CHECK SELECTOR
            time_tag = details_block.find('span', class_='event-time') # <<< CHECK SELECTOR
            if date_tag: details['Date'] = date_tag.text.strip()
            if time_tag: details['Start Time'] = time_tag.text.strip()
            # More complex date/time might be in one tag requiring parsing:
            # dt_tag = details_block.find('div', class_='datetime')
            # if dt_tag: ... parse dt_tag.text ...

            # Labeled Data (Example: <div class="field"><div class="field__label">Region:</div><div class="field__item">Wales</div></div>)
            labels_map = {
                'Region': 'Region',
                'Location': 'Location',
                'Event Type': 'EventType',
                'Places Remaining': 'Availability', # Or maybe just "Availability:"
                'Waiting List': 'Waitlist'
            }
            # Find all potential label/value pairs
            # This selector is very generic - needs refinement based on actual structure
            all_items = details_block.find_all(['div', 'p', 'li'], class_=re.compile(r'(field|item|detail)')) # <<< GUESS - CHECK

            for item in all_items:
                 # Try finding label text within the item
                 label_tag = item.find(class_=re.compile(r'(label|title|heading)')) # <<< GUESS - CHECK
                 label_text = ""
                 if label_tag:
                     label_text = label_tag.text.strip().replace(':', '')
                 else: # Sometimes label is just bold text before value
                      bold_tag = item.find('strong')
                      if bold_tag: label_text = bold_tag.text.strip().replace(':','')

                 # Try finding value text (may need specific class or be sibling/child)
                 value_tag = item.find(class_=re.compile(r'(value|item|content)')) # <<< GUESS - CHECK
                 value_text = ""
                 if value_tag:
                     value_text = value_tag.text.strip()
                 else: # If no specific value tag, take item text excluding label
                      value_text = item.text.strip()
                      if label_text and value_text.startswith(label_text):
                           value_text = value_text[len(label_text):].strip().lstrip(':').strip()


                 if label_text in labels_map:
                     output_key = labels_map[label_text]
                     if output_key in ['Availability', 'Waitlist']:
                         match = re.search(r'\d+', value_text) # Extract number
                         details[output_key] = match.group(0) if match else value_text
                     else:
                         details[output_key] = value_text


        # Summary (Example: <div class="event-description">...</div> or <div property="content:encoded">)
        summary_block = soup.find('div', property='content:encoded') # <<< CHECK SELECTOR (Drupal)
        if not summary_block:
            summary_block = soup.find('div', class_='event-description') # <<< CHECK SELECTOR
        if summary_block:
            # Get text, replace multiple whitespace/newlines with single space
            details['Summary'] = ' '.join(summary_block.get_text(separator=' ', strip=True).split())

    except Exception as e:
        print(f"Error parsing details on {event_url}: {e}")
        # Log the error but keep default N/A values set earlier
        details['Summary'] = f"Error parsing details: {e}" # Add error info to summary

    # Basic validation/cleanup
    for key, value in details.items():
        if value is None:
            details[key] = 'N/A' # Ensure no None values

    return details


# --- Main Function to Loop Through Pages and Scrape ---
def scrape_all_events():
    """Loops through event list pages, finds event links, and scrapes details."""
    all_event_data = []
    page_num = 0


    print(f"Starting scrape. Max pages to check: {MAX_PAGES_TO_TRY}")
    while page_num < MAX_PAGES_TO_TRY:
        # Construct URL for the current list page
        # Note: Check if the site uses 0-based or 1-based pagination
        list_page_url = f"{BASE_URL}{EVENTS_LIST_PATH}?page={page_num}"
        list_soup = get_soup(list_page_url)

        if not list_soup:
            print(f"Failed to retrieve or parse list page {page_num}, stopping pagination.")
            break

        # --- !!! CRITICAL: UPDATE THIS SELECTOR !!! ---
        # Find the anchor tags (links) to individual event pages.
        # Example: Links might be within <article> tags, or specific divs.
        # Look for a pattern in the href like '/event/' or '/events/'
        event_links_tags = list_soup.select('div.view-content div.views-row h3 a[href*="/event/"]') # <<< GUESS - CHECK
        # Alternative: list_soup.select('article.event-card a.event-link[href*="/event/"]') # <<< GUESS - CHECK

        if not event_links_tags:
            # Sometimes the last page exists but is empty, or redirects.
            # Check if the content area looks empty as a secondary check.
            content_area = list_soup.find('div', class_='view-content') # <<< CHECK SELECTOR
            if not content_area or not content_area.text.strip():
                 print(f"No event links found or empty content on page {page_num}. Assuming end of list.")
                 break
            else:
                 # Found content but the selector failed - indicates selector needs fixing!
                 print(f"WARNING: Content found on page {page_num}, but link selector failed. Check CSS Selectors!")
                 print(f"Stopping pagination to avoid infinite loop.")
                 break


        print(f"Found {len(event_links_tags)} potential event links on page {page_num}")

        found_on_page = 0
        for link_tag in event_links_tags:
            relative_link = link_tag.get('href')
            if relative_link and relative_link.strip():
                found_on_page += 1
                # Ensure the link is absolute
                event_url = urljoin(BASE_URL, relative_link.strip())
                print(f"---> Scraping Event: {event_url}")
                event_details = scrape_event_details(event_url)
                if event_details:
                    all_event_data.append(event_details)
                # --- CRUCIAL DELAY ---
                print(f"--- Delaying {DELAY_EVENT_PAGE}s before next event ---")
                time.sleep(DELAY_EVENT_PAGE)

        if found_on_page == 0 and event_links_tags:
             print(f"Selector found {len(event_links_tags)} tags, but no valid hrefs extracted on page {page_num}. Check selector/HTML.")
             break # Stop if tags were found but no links extracted

        page_num += 1
        # --- CRUCIAL DELAY ---
        print(f"=== Delaying {DELAY_LIST_PAGE}s before scraping page {page_num} ===")
        time.sleep(DELAY_LIST_PAGE)

    if page_num == MAX_PAGES_TO_TRY:
        print(f"Reached maximum page limit ({MAX_PAGES_TO_TRY}). Stopping.")

    return all_event_data

# --- Function to Save Data ---
def save_data(data, filepath):
    """Saves the scraped data list of dictionaries to a CSV file."""
    if not data:
        print("No data to save.")
        return

    # Define CSV Headers - ensuring consistent order
    fieldnames = [
        'Title', 'Date', 'Start Time', 'Region', 'Location',
        'EventType', 'Availability', 'Waitlist', 'Summary', 'Link'
    ]
    print(f"Saving {len(data)} events to {filepath}...")
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Use extrasaction='ignore' in case scrape_event_details returns extra keys
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
        print("Data saved successfully.")
    except IOError as e:
        print(f"Error writing CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    print("==========================================")
    print(" Starting OutdoorLads Event Scraper ")
    print("==========================================")
    print(f"Output file will be: {OUTPUT_FILEPATH}")
    print("Reminder: Check robots.txt and Terms of Service.")
    print("Ensure CSS selectors in the script are up-to-date.")

    # --- Run the scraper ---
    start_time = time.time()
    scraped_data = scrape_all_events()
    end_time = time.time()
    duration = end_time - start_time

    print("\n==========================================")
    print(" Scraping Finished ")
    print("==========================================")
    print(f"Total events found: {len(scraped_data)}")
    print(f"Total time taken: {duration:.2f} seconds")

    # --- Save the data ---
    save_data(scraped_data, OUTPUT_FILEPATH)

    print("\nScript execution complete.")
