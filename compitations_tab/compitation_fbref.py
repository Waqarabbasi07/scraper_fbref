from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup

def initialize_webdriver():
    return webdriver.Chrome()

def extract_headings_and_links(driver, url="https://fbref.com/en/comps/"):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    results = []
    table_wrappers = soup.find_all('div', class_='table_wrapper')

    for wrapper in table_wrappers:
        h2_tag = wrapper.find_previous('h2')
        h2_text = h2_tag.text.strip() if h2_tag else 'No heading found'
        table = wrapper.find('table')

        if table:
            links = []
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                link_tag = row.find('th', {'data-stat': 'league_name'}).find('a')
                if link_tag:
                    links.append({
                        'competition_name': link_tag.text.strip(),
                        'url': 'https://fbref.com' + link_tag['href']
                    })
            
            results.append({
                'heading': h2_text,
                'competitions': links
            })

    return results


def scrape_seasonal_data(driver, results):
    final_data = []
    
    for idx, h2_text in enumerate(results):
        heading = h2_text['heading']
        competitions = h2_text['competitions']
        links_seasonly = []
        table_data_seasonly = []
        
        for competition in competitions:
            url = competition['url']
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extracting keys from the table header (if present)
            thead = soup.find('div', id='div_seasons').find('thead')
            keys = [th.get_text() for th in thead.find_all('th')]
            
            # Extracting table values and links from tbody
            tbody = soup.find('div', id='div_seasons').find('tbody')
            rows = tbody.find_all('tr')

            for row in rows:
                values = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                left_cells = row.find_all('th', class_='left')
                for cell in left_cells:
                    link_tag = cell.find('a', href=True)
                    if link_tag:
                        full_link = "https://fbref.com" + link_tag['href']
                        links_seasonly.append(full_link)
                        print(f"Row data-row: {row.get('data-row')}, Link: {full_link}")

                row_data = dict(zip(keys, values))
                table_data_seasonly.append(row_data)

        final_data.append({
            'heading': heading,
            'table_data': table_data_seasonly,
            'extracted_links': links_seasonly
        })

    return final_data

def scrape_season_info(driver, final_data):
    season_data = []

    for entry in final_data:
        heading = entry['heading']
        links_seasonly = entry['extracted_links']
        table_data_seasonly = entry['table_data']

        for season_link in links_seasonly:
            driver.get(season_link)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

    
            info_div = soup.find('div', id='info', class_='comps open')

        
            h1_tags = [h1.get_text(strip=True) for h1 in info_div.find_all('h1')]
            p_tags = [p.get_text(strip=True) for p in info_div.find_all('p')]

    
            tables = soup.find_all('table', class_='stats_table')
            table_data = []

            for table in tables[:1]:
                # Extracting keys from thead
                keys = [th.get_text(strip=True) for th in table.thead.find_all('th')]

                # Extracting values from tbody
                rows = table.tbody.find_all('tr')
                values = []
                for row in rows:
                    row_values = [td.get_text(strip=True) for td in row.find_all('td')]
                    values.append(row_values)

                table_data.append({"keys": keys, "values": values})

            season_info = {
                "heading": heading,
                "season_link": season_link,
                "h1_tags": h1_tags,
                "p_tags": p_tags,
                "table_data": table_data
            }
            
            season_data.append(season_info)

    return season_data


def main():
    driver = initialize_webdriver()
    
    try:
        results = extract_headings_and_links(driver)
        final_data = scrape_seasonal_data(driver, results)
        season_data = scrape_season_info(driver, final_data)
        
        with open('season_data.json', 'w') as json_file:
            json.dump(season_data, json_file, indent=4)
        
        print(json.dumps(season_data, indent=4))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()