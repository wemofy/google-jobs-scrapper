from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import urllib.parse

import json

position = "web developer"
city = "agra"
search_query = f"{position} in {city}"
search_query_encoded = urllib.parse.quote(search_query)  # Encode the search query for the URL
count = 10
link = f"https://www.google.com/search?q={search_query_encoded}&oq={search_query_encoded}&ibp=htl;jobs&sa=X&fpstate=tldetail"

options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(options=options)

start_time = time.time()
time.sleep(1)
browser.get(str(link))