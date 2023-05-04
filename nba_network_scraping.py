import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
teams = 'https://www.nba.com/teams'

# Send a GET request to the URL and store the response
response = requests.get(teams)

# Parse the HTML content of the response using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all links to player pages on the "Players" page
teams_links = soup.find_all("a", class_="Anchor_anchor__cSc3P TeamFigureLink_teamFigureLink__uqnNO")
# passing_data = {}
with open('data/player_passing_data_v3.json', 'r') as fp:
                    passing_data = json.load(fp)
print(list(passing_data.keys()))
for teams_link in teams_links:
    if teams_link.text == 'Profile':
        team_name = teams_link['href'].split('/')[-2].title()
        if team_name not in list(passing_data.keys()):
            passing_data[team_name] = {}
        team_soup = BeautifulSoup(requests.get(f"https://www.nba.com{teams_link['href']}").content, "html.parser")
        for player_link in team_soup.find_all("a", class_="Anchor_anchor__cSc3P"):
            if len(player_link['href'].split('/'))==5 and 'player' in player_link['href']:
                player_url = player_link["href"]
                player_id_num = player_url.split('/')[2]
                player_name = ' '.join(player_url.split('/')[3].split('-')).title()
                if player_name not in passing_data[team_name].keys():
                    print(player_name, team_name)
                    # Set up the Chrome driver
                    driver = webdriver.Chrome(options=options)

                    # Navigate to the page
                    url = f"https://www.nba.com/stats/player/{player_id_num}/passes-dash?dir=D&sort=PASS"
                    driver.get(url)

                    # Wait for the table to load
                    wait = WebDriverWait(driver, 10)
                    try:
                        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Crom_table__p1iZz")))
                    except selenium.common.exceptions.TimeoutException:
                        continue


                    # Get the HTML of the table
                    table_html = table.get_attribute("outerHTML")
                    player_soup = BeautifulSoup(table_html, "html.parser")


                    passing_table = player_soup.find("table",class_= "Crom_table__p1iZz")
                    # if passing_table is None:
                    #     # If no passing data is found, skip to the next player
                    #     continue
                    # # Initialize an empty dictionary to store the player's passing data
                    player_passing_data = {}
                    # Loop through each row of the passing table
                    for row in passing_table.find_all("tr")[2:]:
                        # Get the name of the player passed to
                        player_passed_to = row.find_all("td")[0].text.strip()
                        last_name, first_name = player_passed_to.split(", ")
                        player_passed_to = "{} {}".format(first_name, last_name)
                        # Get the number of passes to that player
                        num_passes = float(row.find_all("td")[3].text.strip())
                        # Add the player and their number of passes to the player's passing data
                        player_passing_data[player_passed_to] = num_passes
                    # Get the name of the player from their page title
                    driver.quit()
                    # Add the player and their passing data to the overall passing data dictionary
                    passing_data[team_name][player_name] = player_passing_data
                    with open('player_passing_data.json', 'w') as fp:
                        json.dump(passing_data, fp)


