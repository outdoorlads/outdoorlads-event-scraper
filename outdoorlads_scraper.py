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
            details['Summary
