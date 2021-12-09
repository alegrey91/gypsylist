#!/usr/bin/env python3

"""
gypsylist.py: A web scraper for nomadlist.com, to avoid site restrictions.
"""

__author__  = "alegrey91"
__license__ = "GPLv3"
__version__ = "0.0.1"

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import re
import argparse
import os

BROWSER_BOOT_TIME = 3
NOMADLIST_DOMAIN = "https://nomadlist.com/"

# Flag parsing
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', '-p', dest="path", type=str, required=True, help="URL path to do the request.")
parser.add_argument('--headless', '-H', dest="headless", action='store_true', default=False, required=False, help="Set browser in headless mode.")
parser.add_argument('--delay', '-d', dest="delay", type=int, default=5, required=False, help="Scroll pause time (default 5).")
parser.add_argument('--emoji', '-e', dest="emoji", action='store_true', default=False, required=False, help="Scroll pause time (default 5).")
args = parser.parse_args()

# Setup
options = Options()
options.headless = args.headless
options.add_argument("window-size=1400x600")
driver = webdriver.Firefox(options=options)
driver.get(NOMADLIST_DOMAIN + args.path)

# Get scroll height
time.sleep(BROWSER_BOOT_TIME)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(args.delay)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Retrieve page source code and close the browser
html = driver.page_source
driver.close()

# Selecting view-container div
main_page = BeautifulSoup(html, 'html.parser')
view = main_page.find("div", {"class": "view-container"})

# Selecting ul and list
view_container = BeautifulSoup(str(view), 'html.parser')
list_view = view_container.find("ul", {"class": "grid show view"})
country_number = 1
for li in list_view.find_all("li"):
    # Retrieve city name
    city_name = BeautifulSoup(str(li.find("h2", {"class": "itemName"})), 'html.parser')
    if city_name.get_text() == "{itemName}" or city_name.get_text() == "None":
        continue
    print("#{}".format(country_number))

    if args.emoji:
        print("🏙️  city: {}".format(city_name.get_text()))
    else:
        print("city: {}".format(city_name.get_text()))

    # Retrieve country name
    city_country = BeautifulSoup(str(li.find("h3", {"class": "itemSub"})), 'html.parser')
    if args.emoji:
        print("🌎 country: {}".format(city_country.get_text()))
    else:
        print("country: {}".format(city_country.get_text()))

    # Find information parsing span
    city_span = BeautifulSoup(str(li), 'html.parser')
    regex = r"class=((?<![\\])['\"])(rating-(?:.(?!(?<![\\])\1))*.?)\1"

    for content in city_span.find_all("span", {"class": "action"}):
        matches = re.finditer(regex, str(content.contents), re.MULTILINE)

        # Get matching groups
        for matchNum, match in enumerate(matches, start=1):
            item = match.group(2).split(" ")[0].split("-")[1]
            rank = match.group(2).split(" ")[2][1:]

            # Formatting output
            if args.emoji:
                if item == "main":
                    item = "⭐️ overall"
                elif item == "cost":
                    item = "💵 cost"
                elif item == "internet":
                    item = "📡 internet"
                elif item == "fun":
                    item = "😀 fun"
                elif item == "safety":
                    item = "👮 safety"
                else:
                    continue
            print("{}: {}/5".format(item, rank))
    country_number += 1

    print()

