import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
import json
from webdriver_manager.chrome import ChromeDriverManager




def get_data_from_table(url, dataset_name):
    d = webdriver.Chrome(ChromeDriverManager().install())
    d.get(url)
    d.maximize_window() #For maximizing window
    d.implicitly_wait(20) #gives an implicit wait for 20 seconds
    d.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select/option[1]').click()
    html=d.page_source

    
    heads = d.find_elements(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/thead/tr/th')
    headers = [h.text for h in heads if h.text != '']
    headers = ['PLAYER', 'TEAM', 'AGE', 'FGM_LESS THAN 5FT.', 'FGA_LESS THAN 5FT.', 'FG%_LESS THAN 5FT.', 'FGM_5-9 FT.', 'FGA_5-9 FT.', 'FG%_5-9 FT.', 'FGM_10-14 FT.', 'FGA_10-14 FT.', 'FG%_10-14 FT.', 'FGM_15-19 FT.', 'FGA_15-19 FT.', 'FG%_15-19 FT.', 'FGM_20-24 FT.', 'FGA_20-24 FT.', 'FG%_20-24 FT.', 'FGM_25-29 FT.', 'FGA_25-29 FT.', 'FG%_25-29 FT.']
    stats_table = d.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/tbody')
    stats_table_html = stats_table.get_attribute('innerHTML')
    s = soup(stats_table_html,'html.parser')
    table_rows = stats_table.find_elements(By.XPATH, ".//tr")
    data = [[i.text for i in b.find_all('td')] for b in s.find_all('tr')]
    d.close()
    df=pd.DataFrame(data, columns=headers)
    df = df.replace(to_replace= r'\n', value= '', regex=True)
    df.to_csv(f'data/{dataset_name}.csv')
    return df
# url = 'https://www.nba.com/stats/players/traditional?PerMode=PerGame&dir=A&sort=MIN'
# url = 'https://www.nba.com/stats/players/traditional?PerMode=PerPossession&dir=A&sort=FGA'
datasets_to_scrape = {'PerPossData': 'https://www.nba.com/stats/players/traditional?PerMode=PerPossession&dir=A&sort=FGA', 'TouchData': 'https://www.nba.com/stats/players/touches', 'ShootingData':'https://www.nba.com/stats/players/shooting'}
for name, url in datasets_to_scrape.items():
    if name =='ShootingData':
        print(f'scraping {name}')
        df = get_data_from_table(url, dataset_name = name)

