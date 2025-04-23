# ======================== 📦 IMPORTS ========================
# All necessary imports grouped here
import requests
import pandas as pd
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# ===========================================================
# 🏟 1) Match Results: Scores, Dates, Venues
# ===========================================================

# Prompt for gameweek (commented for now)
gameweek = input("Enter Gameweek Number : ")
if not gameweek.isdigit():
    print("Please enter a valid number.")
    exit()

# Fetch fixture data from external source
url = "https://fixturedownload.com/feed/json/epl-2024"
response = requests.get(url)
fixtures = response.json()

# # Filter fixtures for the specified gameweek
matches = [match for match in fixtures if match['RoundNumber'] == int(gameweek)]

# If matches found, create DataFrame and display
if matches:
    df = pd.DataFrame(matches, columns=['RoundNumber', 'DateUtc', 'Location', 'HomeTeam', 'AwayTeam', 'HomeTeamScore', 'AwayTeamScore'])
    df['DateUtc'] = pd.to_datetime(df['DateUtc']).dt.strftime('%d/%m/%Y %H:%M')
    print(df)
else:
    print(f"❌ No matches found for Gameweek {gameweek}. Please try a different gameweek.")


# ===========================================================
# 📊 2) Team Statistics: Wins, Losses, Points, etc.
# ===========================================================

chromedriver_path = r"C:\python\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
url = 'https://www.premierleague.com/tables'
driver.get(url)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'allTablesContainer'))
)

html = driver.page_source
driver.quit()
soup = BeautifulSoup(html, 'html.parser')
table_container = soup.find('div', class_='allTablesContainer')
table = table_container.find('table') if table_container else None

if table:
    rows = table.find_all('tr')[1:]
    teams_data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 10:
            position = cols[0].get_text(separator=' ', strip=True).split()[0]
            raw_team = cols[1].get_text(separator=' ', strip=True)
            team_name = raw_team.split('\n')[0] if '\n' in raw_team else raw_team
            played = cols[2].get_text(strip=True)
            won = cols[3].get_text(strip=True)
            drawn = cols[4].get_text(strip=True)
            lost = cols[5].get_text(strip=True)
            goals_for = cols[6].get_text(strip=True)
            goals_against = cols[7].get_text(strip=True)
            goal_difference = cols[8].get_text(strip=True)
            points = cols[9].get_text(strip=True)

            teams_data.append({
                'Position': position,
                'Team': team_name,
                'Played': played,
                'Won': won,
                'Drawn': drawn,
                'Lost': lost,
                'Goals For': goals_for,
                'Goals Against': goals_against,
                'Goal Difference': goal_difference,
                'Points': points
            })

    df = pd.DataFrame(teams_data)
    print(df)
else:
    print("Table not found!")

df.to_csv("premier_league_table.csv", index=False)


# ===========================================================
# 🧍‍♂️ 3) Player Stats: Goals, Assists, Appearances
# ===========================================================

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
service = Service(chromedriver_path)

def scrape_stat(url, stat_name):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stats-table__container"))
        )
    except Exception as e:
        print(f"Error waiting for table to load: {e}")
        driver.quit()
        return pd.DataFrame()

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("tbody", class_="stats-table__container")
    if not container:
        print(f"Error: Could not find the stats table container for {stat_name}")
        return pd.DataFrame()

    rows = container.find_all("tr")
    data = []

    for row in rows:
        name_tag = row.find("a", class_="playerName")
        stat_tag = row.find("td", class_="stats-table__main-stat")

        if name_tag and stat_tag:
            player_name = name_tag.text.strip()
            stat_value = stat_tag.text.strip()

            if stat_value == '' or stat_value == '–':
                stat_value = None
            else:
                try:
                    stat_value = int(stat_value)
                except ValueError:
                    stat_value = None

            data.append({"Player": player_name, stat_name: stat_value})

    return pd.DataFrame(data)

urls = {
    "Goals": "https://www.premierleague.com/stats/top/players/goals",
    "Assists": "https://www.premierleague.com/stats/top/players/goal_assist",
    "Appearances": "https://www.premierleague.com/stats/top/players/appearances"
}

df_goals = scrape_stat(urls["Goals"], "Goals")
df_assists = scrape_stat(urls["Assists"], "Assists")
df_appearances = scrape_stat(urls["Appearances"], "Appearances")

df_goals.to_csv("goals_stats.csv", index=False)
df_assists.to_csv("assists_stats.csv", index=False)
df_appearances.to_csv("appearances_stats.csv", index=False)


# ===========================================================
# 📅 4) Fixture List and Schedules
# ===========================================================

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--log-level=3")

driver_path = r"C:\python\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.premierleague.com/fixtures")

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fixtures"))
    )
except:
    print("❌ Fixtures section not found.")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
    ).click()
    time.sleep(1)
except:
    pass

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

data = []

try:
    fixtures_container = driver.find_element(By.CLASS_NAME, "fixtures")
    print("✅ Fixtures container found.")
    
    date_containers = fixtures_container.find_elements(By.CLASS_NAME, "fixtures__date-container")
    print(f"Found {len(date_containers)} date containers.")
    
    for date_container in date_containers:
        date = date_container.find_element(By.CLASS_NAME, "fixtures__date").text.strip()
        matches_list = date_container.find_element(By.CLASS_NAME, "fixtures__matches-list")
        matches = matches_list.find_elements(By.CLASS_NAME, "match-fixture")

        for match in matches:
            home_team = match.find_element(By.CSS_SELECTOR, ".match-fixture__team-name .match-fixture__short-name").text.strip()
            away_team = match.find_elements(By.CSS_SELECTOR, ".match-fixture__team-name .match-fixture__short-name")[1].text.strip()
            kickoff_time = match.find_element(By.TAG_NAME, "time").text.strip()
            data.append([date, home_team, away_team, kickoff_time])

    if data:
        print("✅ Scraped fixtures data found.")
        csv_filename = 'premier_league_fixtures_2024_2025.csv'

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Home Team', 'Away Team', 'Kick-off Time'])
            writer.writerows(data)

        print(f"✅ Data saved to {csv_filename}")
    else:
        print("❌ No fixtures found.")

except Exception as e:
    print(f"Error while scraping fixtures: {e}")

driver.quit()