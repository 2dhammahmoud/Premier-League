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


# step 1 extraction 

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


# # ===========================================================
# # 📊 2) Team Statistics: Wins, Losses, Points, etc.
# # ===========================================================

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

    df_tavble = pd.DataFrame(teams_data)
    print(df)
else:
    print("Table not found!")

df_tavble.to_csv("premier_league_table.csv", index=False)


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




#  step 2 clean and regax
import re

# ----------------------------
# Match Results Cleaning
# ----------------------------

def clean_html(raw_html):
    return BeautifulSoup(str(raw_html), "html.parser").get_text().strip()

def extract_date(text):
    match = re.search(r'\d{2}/\d{2}/\d{4}', str(text))
    return match.group(0) if match else None

def extract_score(row):
    if pd.notnull(row['HomeTeamScore']) and pd.notnull(row['AwayTeamScore']):
        return f"{row['HomeTeamScore']}-{row['AwayTeamScore']}"
    return None

df.to_csv("cleaned_match_results.csv", index=False)
print("✅ Cleaned match results saved.")




# Apply cleaning if df (match results) exists
if 'df' in globals():
    for col in ['Location', 'HomeTeam', 'AwayTeam']:
        if col in df.columns:
           df[col] = df[col].apply(clean_html)
        else:
            print(f"⚠️ Column '{col}' not found in DataFrame. Skipping.")

else:
    print("⚠️ Match results DataFrame 'df' not found. Skipping match result cleaning.")

# ----------------------------
# Team Statistics Cleaning
# ----------------------------

try:
    team_stats_df = pd.read_csv("premier_league_table.csv")

    numeric_cols = ['Played', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against', 'Goal Difference', 'Points']
    for col in numeric_cols:
        team_stats_df[col] = pd.to_numeric(team_stats_df[col], errors='coerce')

    team_stats_df.to_csv("cleaned_team_stats.csv", index=False)
    print("✅ Team statistics cleaned and saved.")
except FileNotFoundError:
    print("⚠️ premier_league_table.csv not found.")

# ----------------------------
# Player Stats Cleaning & Merge
# ----------------------------

import pandas as pd

# Load CSVs
df_goals = pd.read_csv("top_scorers.csv").rename(columns={"Name": "Player"})
df_assists = pd.read_csv("top_assists.csv").rename(columns={"Name": "Player"})

# Merge on Player and Team
df2 = pd.merge(df_goals, df_assists, on=["Player", "Team"], how="outer", suffixes=('_goals', '_assists'))

# Combine appearances
df2["Appearances"] = df2["Appearances_goals"].combine_first(df2["Appearances_assists"])

# Replace NaNs with the least non-null value in each column
for col in ["Goals", "Assists", "Appearances", "RK_goals", "RK_assists"]:
    min_val = df2[col].dropna().min()
    df2[col] = df2[col].fillna(min_val).astype(int)

# Reorder columns as requested
df2 = df2[["Player", "Team", "Goals", "Assists", "Appearances", "RK_goals", "RK_assists"]]

# ✅ Print a preview
print(df2.head())

# Optional: Save the final version
df2.to_csv("player_combined_stats.csv", index=False)




# ----------------------------
# Fixture Cleaning
# ----------------------------

try:
    fixtures_df = pd.read_csv("premier_league_fixtures_2024_2025.csv")
    fixtures_df['Date'] = pd.to_datetime(fixtures_df['Date'], errors='coerce')
    fixtures_df.to_csv("cleaned_fixtures.csv", index=False)
    print("✅ Fixture data cleaned and saved.")
except FileNotFoundError:
    print("⚠️ premier_league_fixtures_2024_2025.csv not found.")



# analysis
import pandas as pd

print("\n===============================")
print("📊 ANALYSIS SECTION")
print("===============================\n")

# -------------------------------
# 🏟 Match Results Analysis
# -------------------------------
df['HomeGoals'] = pd.to_numeric(df['HomeTeamScore'], errors='coerce').fillna(0).astype(int)
df['AwayGoals'] = pd.to_numeric(df['AwayTeamScore'], errors='coerce').fillna(0).astype(int)
df['TotalGoals'] = df['HomeGoals'] + df['AwayGoals']


print("📌 Match Results Summary")
print(f"Total matches in the gameweek: {len(df)}")
print(f"Total unique teams: {df['HomeTeam'].nunique()}")

top_match = df.sort_values('TotalGoals', ascending=False).iloc[0]
print(f"🎯 Highest scoring match: {top_match['HomeTeam']} vs {top_match['AwayTeam']} - {top_match['TotalGoals']} goals\n")

# -------------------------------
# 📈 Team Performance
# -------------------------------
df_teams = pd.read_csv("cleaned_team_stats.csv")
df_teams[['Played', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against']] = df_teams[['Played', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against']].apply(pd.to_numeric, errors='coerce')

df_teams['Win Ratio'] = df_teams['Won'] / df_teams['Played'].replace(0, pd.NA)
df_teams['Loss Ratio'] = df_teams['Lost'] / df_teams['Played'].replace(0, pd.NA)
df_teams['Draw Ratio'] = df_teams['Drawn'] / df_teams['Played'].replace(0, pd.NA)

top_scoring_team = df_teams.sort_values("Goals For", ascending=False).iloc[0]
strongest_defense = df_teams.sort_values("Goals Against").iloc[0]
top_win_team = df_teams.sort_values("Win Ratio", ascending=False).iloc[0]

print("📌 Team Performance")
print(f"⚽ Best attacking team: {top_scoring_team['Team']} - {top_scoring_team['Goals For']} goals")
print(f"🛡 Strongest defense: {strongest_defense['Team']} - {strongest_defense['Goals Against']} goals conceded")
print(f"🏆 Highest win ratio: {top_win_team['Team']} - {top_win_team['Win Ratio']:.2%}\n")

# -------------------------------
# 🌟 Top Players
# -------------------------------
df_goals = pd.read_csv("goals_stats.csv")
df_assists = pd.read_csv("assists_stats.csv")
df_appearances = pd.read_csv("appearances_stats.csv")

print("📌 Top Player Stats")

if not df_goals.empty:
    top_scorer = df_goals.sort_values("Goals", ascending=False).iloc[0]
    print(f"⚽ Top scorer: {top_scorer['Player']} - {top_scorer['Goals']} goals")
else:
    print("⚽ No goal stats found.")

if not df_assists.empty:
    top_assist = df_assists.sort_values("Assists", ascending=False).iloc[0]
    print(f"🎯 Most assists: {top_assist['Player']} - {top_assist['Assists']} assists")
else:
    print("🎯 No assist stats found.")

if not df_appearances.empty:
    most_appearances = df_appearances.sort_values("Appearances", ascending=False).iloc[0]
    print(f"🧍‍♂ Most appearances: {most_appearances['Player']} - {most_appearances['Appearances']} matches\n")
else:
    print("🧍‍♂ No appearance stats found.")

# -------------------------------
# 🔄 Weekly Form Trends
# -------------------------------
print("📌 Weekly Goal Trends")

if 'RoundNumber' in df.columns:
    weekly_goals = df.groupby('RoundNumber')['TotalGoals'].sum().reset_index()
    most_goals_week = weekly_goals.sort_values("TotalGoals", ascending=False).iloc[0]
    print(f"📈 Most goals in a gameweek: Gameweek {most_goals_week['RoundNumber']} - {most_goals_week['TotalGoals']} goals\n")
else:
    print("❌ No gameweek data available for weekly trend analysis.")


# step4 visulization 

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Optional: Use nicer themes
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Assuming you already have the match data (df), player data (goals_stats.csv), and team performance data (df_teams)

# ------------------------------------------
# a. 📊 Bar Chart for Top Scorers
# ------------------------------------------

# Assuming goals_stats.csv contains player names and their goals scored
df_goals = pd.read_csv("goals_stats.csv")

# Sort by Goals and get the top 10 scorers
top_scorers = df_goals.sort_values('Goals', ascending=False).head(10)

# Plot Bar Chart for Top Scorers
plt.figure(figsize=(10, 6))
sns.barplot(x='Goals', y='Player', data=top_scorers, palette='viridis')

# Add titles and labels to the chart
plt.title('Top 10 Scorers of the Season')
plt.xlabel('Goals Scored')
plt.ylabel('Player')
plt.tight_layout()
plt.show()

# ------------------------------------------
# b. 📈 Line Chart for Team Performance Over the Season
# ------------------------------------------
# Convert Points to numeric

df_teams['Points'] = pd.to_numeric(df_teams['Points'], errors='coerce')

# Sort teams by Points (optional)
df_teams_sorted = df_teams.sort_values('Points', ascending=False)

# Create plot
plt.figure(figsize=(12, 6))
sns.scatterplot(data=df_teams_sorted, x='Team', y='Points', hue='Team', palette='tab20', s=100)

# Customize plot
plt.title('All 20 Teams - Total Points', fontsize=14)
plt.ylabel('Points')
plt.xlabel('Team')
plt.xticks(rotation=45)
plt.legend(title='Team', bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside plot
plt.tight_layout()
plt.show()
# # ------------------------------------------
# c. 📊 Heatmap for Venue-wise or Time-based Patterns (Goals Scored)
# ------------------------------------------

# Group by HomeTeam and AwayTeam for total goals
home_goals = df.groupby('HomeTeam')['HomeGoals'].sum()
away_goals = df.groupby('AwayTeam')['AwayGoals'].sum()

# Combine home and away goals into one DataFrame
venue_data = pd.DataFrame({
    'Home Goals': home_goals,
    'Away Goals': away_goals
}).fillna(0)  # Fill NaN with 0 for teams that only played home or away

# Create a heatmap for home vs away goals
plt.figure(figsize=(10, 8))
sns.heatmap(venue_data, annot=True, cmap='YlGnBu', fmt='.0f', linewidths=0.5)
plt.title("Home vs Away Goals (Venue-wise) - Heatmap")
plt.xlabel("Venue (Home vs Away)")
plt.ylabel("Team")
plt.tight_layout()
plt.show()

# ------------------------------------------
# Additional Heatmap for Goals Scored by Each Team per Gameweek
# ------------------------------------------

# Group by RoundNumber and Team to calculate total goals per week
weekly_goals = df.groupby(['RoundNumber', 'HomeTeam'])['HomeGoals'].sum().reset_index()
weekly_goals = weekly_goals.rename(columns={'HomeTeam': 'Team', 'HomeGoals': 'Goals'})

# Repeat for Away goals (or any other metrics)
away_goals_weekly = df.groupby(['RoundNumber', 'AwayTeam'])['AwayGoals'].sum().reset_index()
away_goals_weekly = away_goals_weekly.rename(columns={'AwayTeam': 'Team', 'AwayGoals': 'Goals'})

# Combine home and away goals into one DataFrame
all_goals = pd.concat([weekly_goals, away_goals_weekly])

# Pivot table to prepare data for heatmap (matchweek on x-axis, teams on y-axis)
heatmap_data = all_goals.pivot_table(index='Team', columns='RoundNumber', values='Goals', aggfunc='sum', fill_value=0)

# Create the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='.0f', linewidths=0.5)
plt.title("Goals Scored by Each Team per Gameweek")
plt.xlabel("Matchweek (RoundNumber)")
plt.ylabel("Team")
plt.tight_layout()
plt.show()


# ---------------------------------------------------------
# ---------------------------------------------------------
from pymongo import MongoClient
import pandas as pd

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create or connect to the database
db = client["premier_league"]

# Load CSVs
df_teams = pd.read_csv("cleaned_team_stats.csv")
df_players = pd.read_csv("player_combined_stats.csv")
df_results = pd.read_csv("cleaned_match_results.csv")
df_fixtures = pd.read_csv("cleaned_fixtures.csv")

# Convert DataFrames to dictionaries
teams_data = df_teams.to_dict("records")
players_data = df_players.to_dict("records")
results_data = df_results.to_dict("records")

# Add a unique 'FixtureID' by combining 'Date', 'Home Team', and 'Away Team'
df_fixtures['FixtureID'] = df_fixtures['Date'].astype(str) + '-' + df_fixtures['Home Team'] + '-' + df_fixtures['Away Team']

# Convert fixtures to dictionary with the new 'FixtureID'
fixtures_data = df_fixtures.to_dict("records")

# Debugging: Check the gameweek number and its deletion
if 'RoundNumber' in df_results.columns:
    gameweek_number = int(df_results['RoundNumber'].iloc[0])  # Extract RoundNumber for deletion
    print(f"Gameweek number to delete: {gameweek_number}")
    
    # Check if documents with the current gameweek exist in MongoDB
    existing_documents = db.match_results.find({'RoundNumber': gameweek_number})
    print(f"Found {len(list(existing_documents))} documents with RoundNumber {gameweek_number} before deletion")

    # Delete old match results for the current gameweek
    deletion_result = db.match_results.delete_many({'RoundNumber': gameweek_number})
    print(f"Deleted {deletion_result.deleted_count} documents for gameweek {gameweek_number}")
else:
    print("⚠️ 'RoundNumber' not found in match results. Skipping deletion.")

# ================================
# 🚫 Avoid Duplicate Insertions
# ================================

# Clear collections first if needed
db.teams.delete_many({})
db.players.delete_many({})
db.fixtures.delete_many({})

# For match_results, delete only specific gameweek
if 'RoundNumber' in df_results.columns:
    gameweek_number = int(df_results['RoundNumber'].iloc[0])
    db.match_results.delete_many({'RoundNumber': gameweek_number})

# Insert fresh cleaned data
db.teams.insert_many(teams_data)
db.players.insert_many(players_data)
db.match_results.insert_many(results_data)

# Insert fixtures without duplicates based on the new 'FixtureID'
for fixture in fixtures_data:
    if db.fixtures.count_documents({'FixtureID': fixture['FixtureID']}) == 0:
        db.fixtures.insert_one(fixture)

print("✅ MongoDB updated with new fixtures.")

# Example: Print first 2 team documents
for doc in db.teams.find().limit(2):
    print(doc)


# streamlit run streamlit_app.py
