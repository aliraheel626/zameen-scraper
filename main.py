import sqlite3
try:
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('my_database.db')  # 'my_database.db' is the name of the database file

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Create table as per requirement
    sql = '''
    CREATE TABLE scraped_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        source_url TEXT,
        page INT
    )'''
    cursor.execute(sql)

    # Commit your changes in the database
    conn.commit()

    # Close the connection
    conn.close()
except:
    pass


import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import random

import re

def extract_page_number(url):
    """
    Extracts the page number from a given URL.

    Args:
    url (str): The URL to extract the page number from.

    Returns:
    int or None: The extracted page number as an integer, or None if not found.
    """
    match = re.search(r'page=(\d+)', url)
    if match:
        return int(match.group(1))
    else:
        return None
def insert(hrefs, source_url, page):
    """
    Inserts hrefs into the database with a common source_url and page.
    
    Args:
    database_path (str): Path to the SQLite database file.
    hrefs (list of str): List of href URLs to be inserted.
    source_url (str): The source URL associated with the hrefs.
    page (int): The page number associated with the hrefs.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # SQL command to insert data
    insert_sql = '''
    INSERT INTO scraped_links (url, source_url, page)
    VALUES (?, ?, ?)
    '''

    # Loop through hrefs and execute the insert command for each
    for href in hrefs:
        cursor.execute(insert_sql, (href, source_url, page))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Example usage
# database_path = 'my_database.db'  # Path to your database file
# hrefs = ['http://example.com/link1', 'http://example.com/link2', ...]  # Example hrefs
# source_url = 'http://example.com/source'  # Example source URL
# page = 1  # Example page number
# insert(database_path, hrefs, source_url, page)  # Insert data

driver = uc.Chrome(use_subprocess=True)
driver.get('https://www.zameen.com/agents/Lahore-1/?page=204')
# Use list comprehension to get the 'href' attribute of each element
time.sleep(1)

while(True):
    source_url=driver.current_url
    page=extract_page_number(source_url)
    errors=driver.find_elements(By.CLASS_NAME,"errors_errorContainer__1-orG")
    hrefs=None
    if len(errors)==0:
        hrefs = [element.get_attribute('href') for element in driver.find_elements(By.CLASS_NAME,"agent-listing-card_cardListingItem__aX-UY") if element.get_attribute('href') is not None]
        insert(hrefs,source_url,page)
    else:
        driver.get(f'https://www.zameen.com/agents/Lahore-1/?page={page+1}')
        print(f'error on {page}')
        time.sleep(3)
        continue

        
    # Find the element (replace 'your_element_selector' with the actual selector)

    if page!=228:
        # Create an ActionChain
        actions = ActionChains(driver)
        element_to_scroll_to_and_click = driver.find_element(By.CLASS_NAME,'next')
        # driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll_to_and_click)
        # Move to the element and then click
        time.sleep(random.randint(1,3))
        actions.move_to_element(element_to_scroll_to_and_click).click().perform()
        # time.sleep(random.randint(1,2))
        # actions.click(element_to_scroll_to_and_click).perform()
        time.sleep(random.randint(5,10))
        print(page)
        continue
    break


# Print the list of hrefs
driver.quit()