import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import json


driver = webdriver.Chrome()
url = 'https://fbref.com/en/countries/' 
driver.get(url)

time.sleep(2)


div_clubs = driver.find_element(By.ID, 'div_countries')

table = div_clubs.find_element(By.TAG_NAME, 'table')

thead = table.find_element(By.TAG_NAME, 'thead')
tbody = table.find_element(By.TAG_NAME, 'tbody')

headers = [th.get_attribute('data-stat') for th in thead.find_elements(By.TAG_NAME, 'th')]

data = []
for row in tbody.find_elements(By.TAG_NAME, 'tr'):
    values = [td.text for td in row.find_elements(By.TAG_NAME, 'td')]
    data.append(dict(zip(headers[1:], values)))  # headers[1:] because the first header is for the row header

for entry in data:
    print(entry)

        
with open('country_table_data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
