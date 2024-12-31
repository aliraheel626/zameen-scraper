import re
import random
import time
import sqlite3
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

# Database setup


def setup_database():
    """
    Create or connect to the SQLite database and ensure the required table exists.
    """
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraped_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            source_url TEXT,
            page INT,
            company TEXT,
            CEO TEXT,
            phone TEXT,
            state INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions


def extract_page_number(url):
    """
    Extract the page number from a given URL.

    Args:
        url (str): The URL containing the page parameter.

    Returns:
        int: The page number if found, otherwise None.
    """
    match = re.search(r'page=(\d+)', url)
    return int(match.group(1)) if match else None


def insert_links(hrefs, source_url, page):
    """
    Insert scraped links into the database.

    Args:
        hrefs (list): List of href URLs to insert.
        source_url (str): The URL of the page the links were scraped from.
        page (int): The page number of the source URL.
    """
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO scraped_links (url, source_url, page)
        VALUES (?, ?, ?)
    ''', [(href, source_url, page) for href in hrefs])
    conn.commit()
    conn.close()


def update_link(url, company, CEO, phone):
    """
    Update the details of a link in the database.

    Args:
        url (str): The URL of the link to update.
        company (str): The company name to update.
        CEO (str): The CEO name to update.
        phone (str): The phone number to update.
    """
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE scraped_links
        SET company = ?, CEO = ?, phone = ?, state = 2
        WHERE url = ?
    ''', (company, CEO, phone, url))
    conn.commit()
    conn.close()


def fetch_next_link():
    """
    Fetch the next URL with state 0 and mark it as being processed (state 1).

    Returns:
        str: The URL to process, or None if no unprocessed URLs exist.
    """
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT url FROM scraped_links
        WHERE state = 0
        LIMIT 1
    ''')
    row = cursor.fetchone()
    if row:
        url = row[0]
        cursor.execute('''
            UPDATE scraped_links
            SET state = 1
            WHERE url = ?
        ''', (url,))
        conn.commit()
    conn.close()
    return row[0] if row else None


def reset_state():
    """
    Reset all links with state 1 back to state 0.
    """
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE scraped_links
        SET state = 0
        WHERE state = 1
    ''')
    conn.commit()
    conn.close()


def extract_text_from_html(html_content):
    """
    Extract text from HTML content using BeautifulSoup.

    Args:
        html_content (str): The raw HTML content.

    Returns:
        str: The extracted text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

# Web scraping functions


def scrape_links():
    """
    Scrape agent links from the website and store them in the database.
    """
    driver = uc.Chrome(use_subprocess=False)
    driver.get('https://www.zameen.com/agents/Lahore-1/?page=1')
    time.sleep(1)
    while True:
        hrefs = [
            element.get_attribute('href')
            for element in driver.find_elements(By.CLASS_NAME, "agent-listing-card_cardListingItem__aX-UY")
            if element.get_attribute('href') is not None
        ]
        source_url = driver.current_url
        page = extract_page_number(source_url)
        insert_links(hrefs, source_url, page)

        if page == 228:
            break

        next_button = driver.find_element(By.CLASS_NAME, 'next')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        ActionChains(driver).move_to_element(next_button).click().perform()
        time.sleep(random.randint(5, 10))

    driver.quit()


def scrape_details():
    """
    Scrape company, CEO, and phone details from the URLs in the database.
    """
    driver = uc.Chrome(use_subprocess=False, headless=True)
    company_name_class = 'introduction-card_detailHeader__1M_eJ'
    ceo_name_class = 'staff-card_agentStaffData__1zxZz'
    call_button_class = 'staff-card_callBtn__188RX'
    number_class = 'contact-popup_numberchip__24E__'

    while (url := fetch_next_link()) is not None:
        driver.get(url)
        time.sleep(random.randint(2, 5))

        try:
            company = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, company_name_class))
            )
            company = extract_text_from_html(
                company.get_attribute('innerHTML'))
        except TimeoutException:
            company = None

        try:
            ceo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, ceo_name_class))
            )
            ceo = extract_text_from_html(ceo.get_attribute('innerHTML'))
        except TimeoutException:
            ceo = None

        try:
            call_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, call_button_class))
            )
            ActionChains(driver).move_to_element(call_button).click().perform()
            time.sleep(random.randint(2, 5))
            number = driver.find_element(By.CLASS_NAME, number_class)
            number = extract_text_from_html(number.get_attribute('innerHTML'))
        except TimeoutException:
            number = None

        update_link(url, company, ceo, number)
        reset_state()

    driver.quit()


# Main execution
if __name__ == "__main__":
    setup_database()
    scrape_links()
    scrape_details()
