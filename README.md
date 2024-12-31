# README

## Overview

This script is a web scraping application designed to extract data from a real estate website and store it in a SQLite database. The script performs two main tasks:

1. **Scraping Links:** Extracts agent profile URLs from multiple pages on the website and stores them in a database.
2. **Scraping Details:** Visits each extracted profile URL to retrieve details such as company name, CEO, and contact information.

The script utilizes Selenium with undetected ChromeDriver, BeautifulSoup for HTML parsing, and SQLite for database management.

## Features

- Scrapes agent profile links from paginated results.
- Extracts detailed information (company name, CEO, phone) from each profile page.
- Stores scraped data in a structured SQLite database.
- Implements state management to track scraping progress.

## Requirements

### Python Libraries

- `selenium`
- `undetected_chromedriver`
- `beautifulsoup4` (BeautifulSoup)
- `pysqlite3`

Install required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Setup

Ensure you have Python installed on your machine. Clone this repository and navigate to the script directory.

### 2. Run the Script

Execute the script to perform both link scraping and detail extraction:

```bash
python main.py
```

### 3. Database

The script creates a SQLite database (`my_database.db`) with a table named `scraped_links` to store the extracted data.

### Table Schema

| Column     | Type    | Description                                                |
| ---------- | ------- | ---------------------------------------------------------- |
| id         | INTEGER | Auto-incrementing unique identifier.                       |
| url        | TEXT    | Profile URL.                                               |
| source_url | TEXT    | URL of the page where the link was found.                  |
| page       | INT     | Page number from which the link was scraped.               |
| company    | TEXT    | Company name extracted from the profile.                   |
| CEO        | TEXT    | CEO name extracted from the profile.                       |
| phone      | TEXT    | Contact number extracted from the profile.                 |
| state      | INTEGER | Processing state: 0 (new), 1 (in progress), 2 (completed). |

### Functions

#### 1. `setup_database()`

Initializes the SQLite database and ensures the required table exists.

#### 2. `scrape_links()`

Scrapes agent profile links from all paginated results and stores them in the database.

#### 3. `scrape_details()`

Visits each profile URL to scrape and store company, CEO, and phone details.

#### 4. Helper Functions

- `extract_page_number(url)`: Extracts page number from a URL.
- `insert_links(hrefs, source_url, page)`: Inserts scraped links into the database.
- `update_link(url, company, CEO, phone)`: Updates profile details in the database.
- `fetch_next_link()`: Retrieves the next unprocessed link from the database.
- `reset_state()`: Resets state of in-progress links to unprocessed.
- `extract_text_from_html(html_content)`: Extracts clean text from HTML content.

## Notes

- The script uses random sleep intervals to reduce the likelihood of being detected as a bot.
- Ensure you comply with the website's Terms of Service before scraping.

## Customization

You can modify the following constants and classes to adapt the script for other websites:

- `company_name_class`: CSS class for the company name element.
- `ceo_name_class`: CSS class for the CEO name element.
- `call_button_class`: CSS class for the call button element.
- `number_class`: CSS class for the phone number element.

## Troubleshooting

- If scraping fails due to CAPTCHA challenges, consider using proxies or headless browser settings.
- Ensure the website structure has not changed. Update CSS selectors accordingly.
