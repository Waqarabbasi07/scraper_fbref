from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime, timedelta

def setup_selenium():
    driver = webdriver.Chrome()
    return driver

def fetch_html_content_with_selenium(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load fully
    html_content = driver.page_source
    return html_content

def extract_headings_and_tables(soup):
    headings_and_tables = []

    sections = soup.find_all('div', class_='table_wrapper tabbed')
    
    for section in sections:
        heading_div = section.find('div', class_='section_heading')
        if heading_div:
            heading = heading_div.find('h2').get_text(strip=True)
            table = section.find('table')
            if table:
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                headers = headers[1:]
                
                rows = []
                for row in table.find('tbody').find_all('tr'):
                    row_data = {}
                    cols = row.find_all('td')
                    for idx, header in enumerate(headers):
                        if idx < len(cols):
                            row_data[header] = cols[idx].get_text(strip=True)
                        else:
                            row_data[header] = None  
                    rows.append(row_data)
                headings_and_tables.append({"heading": heading, "rows": rows})

    return headings_and_tables

def main():
    start_date = datetime.strptime("2024-08-18", "%Y-%m-%d")  # Set the start date
    end_date = datetime.strptime("2024-08-17", "%Y-%m-%d")  # Set the end date
    
    driver = setup_selenium()
    
    try:
        while start_date >= end_date:
            date_str = start_date.strftime("%Y-%m-%d")
            url = f"https://fbref.com/en/matches/{date_str}"
            print(f"Fetching data for {date_str}...")
            html_content = fetch_html_content_with_selenium(driver, url)
            soup = BeautifulSoup(html_content, 'html.parser')
            data = extract_headings_and_tables(soup)
            
            # Save data as JSON
            with open(f"matches_tab_{date_str}.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
            
            print(f"Data for {date_str} has been saved to matches_tab_{date_str}.json")
            
            start_date -= timedelta(days=1)
            
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
