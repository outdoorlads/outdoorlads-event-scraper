# OutdoorLads Event Scraper

This project contains a Python script designed to scrape event information from the [OutdoorLads website](https://www.outdoorlads.com/events). It navigates through the event list pages and extracts detailed event data.

**Current Location Context (for potential geo-specific scraping, if needed):** Liverpool, England, United Kingdom.
**Current Time During Generation (for reference):** Saturday, March 29, 2025 at 5:13 PM.

## :warning: Disclaimer & Important Considerations

* **Terms of Service & `robots.txt`**: **YOU MUST** check the [OutdoorLads Terms of Service](https://www.outdoorlads.com/terms) and [robots.txt](https://www.outdoorlads.com/robots.txt) before using this script to ensure compliance.
* **Responsible Scraping**: This script includes delays between requests (`DELAY_LIST_PAGE`, `DELAY_EVENT_PAGE`). **Do not** reduce these significantly, and consider increasing them to avoid overloading the server.
* **Website Changes**: Websites change frequently. The HTML structure targeted by this script **will** eventually change, breaking the scraper. The CSS selectors used in `outdoorlads_scraper.py` are subject to change.
* **Maintenance Required**: You will need to periodically check if the script still works and update the CSS selectors when the website structure changes.

## Features

* Handles pagination across event list pages.
* Scrapes detailed information from individual event pages:
    * Title
    * Date
    * Start Time
    * Region
    * Location
    * Event Type
    * Availability (Places Remaining)
    * Waitlist count
    * Summary/Description
    * Direct Link
* Saves extracted data to a CSV file (`outdoorlads_events.csv`).
* Includes configurable delays and user-agent.
* Includes a GitHub Actions workflow (`.github/workflows/scrape.yml`) for automated daily scraping.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2.  **Install Python:** Ensure you have Python 3.7+ installed.
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Using a virtual environment is recommended)*
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Configuration

Before running the script, you **must** configure the CSS Selectors:

1.  **Open `outdoorlads_scraper.py`**.
2.  **Inspect Live Website:** Use your browser's Developer Tools (F12 or Right-click -> Inspect) on `outdoorlads.com/events` and individual event pages.
3.  **Update Selectors:** Find the sections marked with `<<< CHECK SELECTOR` or `<<< CRITICAL: UPDATE THESE SELECTORS !!!`. Replace the example selectors (like `soup.find('h1', class_='page-title')`) with the actual selectors from the website.
4.  **User Agent (Optional):** Consider updating the `HEADERS` dictionary with your contact information if you want to be transparent about your scraping activity.
5.  **Delays (Optional):** Adjust `DELAY_LIST_PAGE` and `DELAY_EVENT_PAGE` if needed, but avoid setting them too low.

## Running Locally

Once configured, run the script from your terminal:

```bash
python outdoorlads_scraper.py
```
