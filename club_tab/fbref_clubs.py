import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
driver = webdriver.Chrome()

url = 'https://fbref.com/en/squads/'


response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')

if table and table.find('thead'):
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
else:
    print("Table or table header not found.")
    headers = []

data = []
club_links = []

if table and table.find('tbody'):
    rows = table.find('tbody').find_all('tr')

    for row in rows:
        values = [td.text.strip() for td in row.find_all('td')]
        
        club_link_tag = row.find('td', {'data-stat': 'club_count'}).find('a')
        if club_link_tag:
            club_links.append('https://fbref.com' + club_link_tag['href'])
        
        if values:
            data.append(dict(zip(headers, values)))
else:
    print("Table body not found.")

# Print main table data
print("Data extracted from the main table:")
for item in data:
    print(item)
print(f"Total club links found: {len(club_links)}")
print("\nClub links:")
for link in club_links:
    print(link)

# Iterate over each club link and fetch the data from each page
for link in club_links:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the club-specific table
    table = soup.find('table', id='clubs')
    if table:
        thead = table.find('thead')
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all('th')]
        else:
            print("Table header not found on the club page.")
            headers = []

        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                values = [cell.get_text(strip=True) for cell in cells]
                data.append(dict(zip(headers, values)))
            
            # Print club-specific data
            print(f"\nData from {link}:")
            print("Headers:", headers)
            for entry in data:
                print(entry)
        else:
            print("Table body not found on the club page.")
    else:
        print(f"Table with id 'clubs' not found on the club page: {link}")
