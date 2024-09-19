from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Uncomment and configure WebDriver if needed
# options = Options()
# options.add_argument("--headless")  
# options.add_argument("--disable-gpu")  
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome()
driver = webdriver.Chrome()

def extract_player_links():
    driver.get("https://fbref.com/en/")
    print("Page title:", driver.title)
    
    driver.find_element(By.ID, "players").find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a").click()

    new_element_locator = ((By.XPATH, "/html/body/div[3]/div[6]/div[4]/div[2]"))
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(new_element_locator))

    new_elements = driver.find_element(*new_element_locator).find_elements(By.CSS_SELECTOR, "a")

    links = [element.get_attribute("href") for element in new_elements]
    # print(len(links))
    return links

def extract_bio_links(player_link):
    driver.get(player_link)
    bio_links = []
    
    try:
        player_bio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[6]/div[1]/div[2]"))
        )
        p_tags = player_bio.find_elements(By.TAG_NAME, 'p')
        # print(len(p_tags))
        for p_tag in p_tags:
            try:
                a_tag = p_tag.find_element(By.TAG_NAME, "a")
                link_url = a_tag.get_attribute("href")
                bio_links.append(link_url)
            except Exception as e:
                print(f"No <a> tag found in this <p>: {e}")
    except Exception as e:
        print(f"An error occurred while finding player bio: {e}")

    return bio_links

def extract_data_from_page(url):
    driver.get(url)

    # Extract the h1 tag
    h1_tag = driver.find_element(By.XPATH, "//h1/span").text
    # print(f"H1 Tag: {h1_tag}")

    # Extract all p tags
    p_tags = driver.find_elements(By.XPATH, "//p")
    p_texts = [p.text for p in p_tags]
    # print("P Tags:")
    # for p in p_texts:
    #     print(p)

    player_info = {}
    if h1_tag:
        player_info['name'] = h1_tag

    for p in p_texts:
        if 'Position:' in p:
            parts = p.split('Footed:')
            player_info['position'] = parts[0].replace('Position:', '').strip()
            player_info['footed'] = parts[1].strip() if len(parts) > 1 else ''
        elif 'Born:' in p:
            born_parts = p.split('in')
            player_info['born'] = born_parts[0].replace('Born:', '').strip()
            player_info['birth_place'] = born_parts[1].strip() if len(born_parts) > 1 else ''
        elif 'National Team:' in p:
            player_info['national_team'] = p.replace('National Team:', '').strip()

    # Define super keys
    super_keys = {
        "Playing Time": ["MP", "Starts", "Min", "90s"],
        "Performance": ["GA", "GA90", "SoTA", "Saves", "Save%", "W", "D", "L", "CS", "CS%"],
        "Penalty Kicks": ["PKatt", "PKA", "PKsv", "PKm", "Save%", "Matches"],
        "Per 90 Minutes": ["Gls", "Ast", "G+A", "G-PK", "G+A-PK", "Matches"]
    }

    # Define table data within the function using table IDs
    tables = [
        ('stats_keeper_nat_tm', 'Goalkeeping Stats'),
        ('stats_standard_nat_tm', 'Standard Stats'),
        ('stats_playing_time_nat_tm', 'Playing Time Stats'),
        ('stats_misc_nat_tm', 'Miscellaneous Stats'),
        ('stats_shooting_dom_lg','Shooting Stats: Domestic Leagues'),
        ('stats_passing_expanded','Passing'),
        ('stats_passing_types_expanded','Pass Type'),
        ('stats_gca_expanded','Goal and Shot Creation'),
        ('stats_defense_expanded','Defensive Actions'),
        ('stats_possession_expanded','Possession'),
        ('stats_standard_dom_lg', 'Standard Stats: Domestic Leagues'),
        ('stats_shooting_dom_lg', 'Shooting: Domestic Leagues'),
        ('stats_passing_dom_lg','Passing: Domestic Leagues'),
        ('stats_passing_types_dom_lg','Pass Types: Domestic Leagues'),
        ('stats_gca_dom_lg','Goal and Shot Creation: Domestic Leagues'),
        ('stats_defense_dom_lg','Defensive Actions: Domestic Leagues'),
        ('stats_possession_dom_lg','Possession: Domestic Leagues'),
        ('stats_playing_time_dom_lg','Playing Time: Domestic Leagues'),
        ('stats_misc_dom_lg','Miscellaneous Stats: Domestic Leagues'),
        ('stats_player_summary_fde1981a','Player Club Summary'),
        ('stats_standard_dom_cup','Standard Stats: Domestic Cups'),
        ('stats_shooting_dom_cup','Shooting: Domestic Cups'),
        ('stats_playing_time_dom_cup','Playing Time: Domestic Cups'),
        ('stats_misc_dom_cup','Miscellaneous Stats: Domestic Cups')
    ]

    all_tables_data = {
        "player_bio": player_info,
        "tables": []
    }

    for table_id, table_name in tables:
        try:
            # Wait until the table element is visible using table ID
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, table_id))
            )
            
            # Extract headers using thead and th within the located table
            headers = [th.text.strip() for th in table.find_elements(By.XPATH, ".//thead/tr[2]/th")]
            
            # Initialize the table data dictionary with super keys
            table_data = {key: {} for key in super_keys.keys()}
            table_data['Other'] = {}  # For any keys not covered by super keys
            
            # Extract rows from tbody
            body_rows = table.find_elements(By.XPATH, ".//tbody/tr")
            
            for row in body_rows:
                cols = row.find_elements(By.XPATH, ".//th | .//td")
                cols = [col.text.strip() for col in cols]
                
                for header, value in zip(headers, cols):
                    added = False
                    for super_key, sub_keys in super_keys.items():
                        if header in sub_keys:
                            table_data[super_key][header] = value
                            added = True
                            break
                    if not added:
                        table_data['Other'][header] = value
            
            # print(f"\nTable Name: {table_name}")
            # print(f"Data for table with ID: {table_id}")
            # for super_key, data in table_data.items():
            #     print(f"{super_key}: {data}")
            
            all_tables_data["tables"].append({table_name: table_data})
        
        except Exception as e:
            print(f"Error processing table {table_name}: {e}")

    
    return all_tables_data
def main():
    all_player_data = []
    player_links = extract_player_links()
    
    for player_link in player_links[:1]:
        bio_links = extract_bio_links(player_link)
        
        for bio_link in bio_links[:3]:
            table_data = extract_data_from_page(bio_link)
            if table_data:
                all_player_data.append(table_data)

    if all_player_data:
        df = pd.DataFrame(all_player_data)
        json_data = df.to_json(orient='records', indent=2)
        # print("JSON: Standard Stats")
        # print(json_data)
        with open('standard_stats.json', 'w') as f:
            f.write(json_data)

    driver.quit()
if __name__ == "__main__":
    main()