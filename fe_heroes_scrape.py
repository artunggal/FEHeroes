import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import csv
import pandas as pd
import numpy as np
from scipy import stats
import time
import re

ser = Service("./chromedriver")
op = webdriver.ChromeOptions()
browser = webdriver.Chrome(service=ser, options=op)

gg = "https://gamepress.gg/feheroes/heroes"
browser.get(gg)
respData = browser.page_source
browser.close()
nsoup = BeautifulSoup(respData, 'html.parser')
n_table = nsoup.find("table", id = "heroes-new-list")

gpress = []
hp = []
attack = []
speed = []
defense = []
res = []
total = []
color = []
weap = []
mov = []
rar = []
urls = []
other = []


for group in n_table.findAll("tr")[1::3]:
    gpress.append(group.attrs.get("data-name"))
    hp.append(group.attrs.get("data-hp"))
    attack.append(group.attrs.get("data-atk"))
    speed.append(group.attrs.get("data-spd"))
    defense.append(group.attrs.get("data-def"))
    res.append(group.attrs.get("data-res"))
    total.append(group.attrs.get("data-total"))
    color.append(group.attrs.get("data-element").split()[0])
    weap.append(group.attrs.get("data-element").split()[-1])
    # data-cat-1="331" - infantry
    # data-cat-1="306" - cavalier
    # data-cat-1="326" - armor
    # data-cat-1="316" - flying
    mov.append(group.attrs.get("data-cat-1"))
    rar.append(group.attrs.get("data-stars"))
    
    link = group.findAll("td")[0].find("a")["href"]
    url = "https://gamepress.gg" + link
    urls.append(url)
    other.append(group.attrs.get("data-cat-"))

dfn = pd.DataFrame(gpress, columns = ["Name"])
dfn["Color"] = color
dfn["Weapon"] = weap
dfn["MoveCode"] = mov
dfn["Rarities"] = rar
dfn["HP"] = hp
dfn["Atk"] = attack
dfn["Spd"] = speed
dfn["Def"] = defense
dfn["Res"] = res
dfn["Total"] = total

# for aether raids tier list - get href and tier 
ser = Service("./chromedriver")
op = webdriver.ChromeOptions()
# below two lines allow us to initiate "Headless Mode", which means that selenium works silently
op.add_argument('--headless')
op.add_argument('--disable-gpu')
browser = webdriver.Chrome(service=ser, options=op)
tlist = ("https://gamepress.gg/feheroes/aether-raids-tier-list")
browser.get(tlist)
tData = browser.page_source
browser.close()
tsoup = BeautifulSoup(tData, 'html.parser')

# create a dictionary containing characters and their tiers
char_dict = {}
i = 0
for field in tsoup.find_all('div', attrs={'class':'field__item'}):
    if field.find('div', id=lambda x: x and x.startswith('tier-')):
        i += 1
        for in_tier in field.find_all('div', attrs = {'class': 'tier-list-cell-row'}):
            unit = in_tier.attrs.get("data-title")
            char_dict[unit] = int(i)

# turns the dictionary into a df column, and adds it to our existing df
tiers = pd.DataFrame.from_dict(char_dict, orient = "index", columns = ["Tier"])
dfn = pd.merge(dfn, tiers, left_on = "Name", right_index = True, how = "left")

## this part of the script grabs page source data for each individual page
ser = Service("./chromedriver")
op = webdriver.ChromeOptions()
# below two lines allow us to initiate "Headless Mode", which means that selenium works silently
op.add_argument('--headless')
op.add_argument('--disable-gpu')
browser = webdriver.Chrome(service=ser, options=op)

all_char = []

for needed in urls:

    browser.get(needed)
    chardata = browser.page_source
    
    # has all of the html data
    soupy = BeautifulSoup(chardata, 'html.parser')
    all_char.append(soupy)
        
    # buffer for web driver
    time.sleep(4)
    
    #group.findAll("td")[12] is total
browser.quit()

##################

title = []
w_upgrades = []
personal = []
origin = []
img = []
is_legend = []
move_t = []
is_duo = []
col2 = []
weap2 = []
# below are new additions
tier = []
# banner can be a list to easily get banner count
banner = []
num_banner = []

for char in all_char:
    
    # get hero title
    char_title = ""
    for span in char.find("table", id = "hero-details-table").findAll("span"):
        char_title += span.text
    title.append(char_title)
    
    weapinfo = char.find("div", id = "weapon-skills")
    
    # retrieves whether the character has weapon-refines
    if weapinfo.findAll("div", {"id": "weapon-upgrades-section"})[0].find(
        "div", {"class": "view-content"}) is not None:
        w_upgrades.append(True)
    else:
        w_upgrades.append(False)

    # retrieves whether the character has a personal, non-inheritable weapon
    i = 0
    per = False
    for item in weapinfo.findAll("div", {"class": "views-element-container"
        })[0].findAll("tr"):
        if i == 0:
            i += 1
            continue
        if not item.findAll("div"):
            continue
        if "Non-Inheritable skill" in item.findAll("div")[-1].get_text():
            per = True
            break
    if per is False:
        personal.append(False)
    else:
        personal.append(True)

    # get origin information
    # need to start taking into account duos with origin of multiple games
    try:
        attempt_orig = char.find("div", {"class": 
         "field field--name-field-origin field--type-entity-reference field--label-hidden field__items"})
        games = attempt_orig.findAll("div", {"class": 'field__item'})
        if len(games) == 1:
            origin.append(games[0].text)
        else:
            game_lst = []
            for game in attempt_orig.findAll("div", {"class": 'field__item'}):
                game_lst.append(game.text)
            origin.append(game_lst)
    except AttributeError:
        origin.append("None")
        
    # get hero image link
    image = char.find("div", id = "hero-image").find("img")["src"]
    img.append("https://gamepress.gg" + image)

    att = char.find("div", id = "hero-atts")
    
    # get information about whether character is legendary/mythic
    is_legend.append(att.find("a", {"class": 
        "tipso-legendary"}) is not None)
    
    # get move type information
    move = att.find("div", {"class": 
        "field field--name-field-movement field--type-entity-reference field--label-hidden field__item"})
    move_t.append(move.get_text().replace("\n", "").replace(" ", ""))
    
    # get information about whether character is a duo character
    is_duo.append(char.find("div", {"class": "duo-skill-effect"}) is not None)
    
    # sanity check for color/weapon
    w_use = att.find("div", {"class": 
        "field field--name-field-attribute field--type-entity-reference field--label-hidden field__item"})
    colour, weapon = w_use.get_text().replace("\n", "").split()
    col2.append(colour)
    weap2.append(weapon)
    
    # get information regarding banners
    banner_h3 = char.find("h3", text="Banners Featured In")
    char_banner = []
    for row in banner_h3.find_next_siblings("div")[0].findAll('td'):
        char_banner.append(row.find("a").text)
    banner.append(char_banner)
    num_banner.append(len(char_banner))

# take all of the data obtained and creates new columns
dfn["Title"] = title
dfn["Refines"] = w_upgrades
dfn["Personal Weapon"] = personal
dfn["Legendary/Mythic"] = is_legend
dfn["Origin"] = origin
dfn["Duo"] = is_duo
dfn["Image"] = img
dfn["Movement"] = move_t
dfn["Banners"] = banner
dfn["Number of Banners"] = num_banner

# grabs data related to refreshers (dancers/singers)
refresh = []
dsurls = ["https://gamepress.gg/feheroes/command-skills/dance",
         "https://gamepress.gg/feheroes/command-skills/sing"]

ser = Service("./chromedriver")
op = webdriver.ChromeOptions()
# below two lines allow us to initiate "Headless Mode", which means that selenium works silently
op.add_argument('--headless')
op.add_argument('--disable-gpu')
brow = webdriver.Chrome(service=ser, options=op)
for lin in dsurls:
    brow.get(lin)
    ddata = brow.page_source
    dsoup = BeautifulSoup(ddata, "html.parser")
    since = dsoup.find("div", id = "block-gamepressbase-content")
    char = since.find("div", {"class": "views-element-container"}).findAll("a")
    for it in char[1::2]:
        refresh.append(it.get_text())
brow.quit()

# creates a column with a binary indicator of whether a unit is a refresher
ref = dfn["Name"].apply(lambda x: x in refresh)
dfn2 = dfn.copy()
dfn2["Refresher"] = ref

# goes through the 'Rarities' column to create two features: one for how the
# character is obtained in the game, and one for actual rarity

rar = []
ob = []
for row in dfn2["Rarities"]:
    st = []
    a = row.split("_")[0]
    if "Story" in row:
        ob.append("Story")
    elif "Grand_Hero_Battle" in row:
        ob.append("GHB")
    elif "Tempest_Trials" in row:
        ob.append("TT")
    elif "Enemy_Only" in row:
        ob.append("Enemy-Only")
    elif "Legacy" in row:
        ob.append("Legacy")
    else:
        ob.append("NA")
    for i in a.split("-"):
        if "2" in i or "3" in i or "4" in i or "5" in i:
            st.append(i)
    rar.append(st)

dfn2["Stars"] = rar
dfn2["Obtain"] = ob
# sanity check for color, since we found something off through data exploration
dfn2["Color"] = col2

# changes instances of no tier to "None"
dfn2["Tier"] = dfn2["Tier"].fillna("None")

# to get release date of characters
ser = Service("./chromedriver")
op = webdriver.ChromeOptions()
# below two lines allow us to initiate "Headless Mode", which means that selenium works silently
op.add_argument('--headless')
op.add_argument('--disable-gpu')
browser = webdriver.Chrome(service=ser, options=op)
r_list = ("https://feheroes.fandom.com/wiki/List_of_Heroes")
browser.get(r_list)
releaseData = browser.page_source
browser.close()
release_soup = BeautifulSoup(releaseData, 'html.parser')
release_table = release_soup.find_all('tr', attrs={'class':'hero-filter-element'})

# this function adjusts the title so that it matches with the GamePress data, allowing
# for merging

def title_fix(title):
    print(title)
    title_a, title_b = title.split(":")
    title_a = title_a.split(" ")[-1]
    return title_a + " :" + title_b

release_data_dict = {}
origin_data_dict = {}

# based on scraping that shows differences in used titles - this dictionary fixes the following needed changes
    # Tethys: typo ("Dancer")
    # Canas: "Wisdom Seeker in GPedia"
    # Hatari - no info
    # Niles - the word "be" is capitalized in Gpedia
    # Eliwood - Marquess Pherae in GPedia
    # Winter Tharja - quotes around "Normal Girl" in Gpedia
title_change_dict = {"Niles - Cruel to Be Kind": "Niles - Cruel to be Kind", 
                     "Eliwood - Marquess Pherae": "Eliwood - Marquess of Pherae",
                    'Tharja - "Normal Girl"': "Tharja - Normal Girl",
                    "Canas - Wisdom Seeker": "Canas - Seeker of Wisdom"}

for char in release_table:
    title = char.findAll("td")[1].text
    title = title.replace(":", " -")
    title = re.sub(r'\([^)]*\)', '', title)
    if title in title_change_dict.keys():
        title = title_change_dict[title]
    release_date = char.findAll("td")[7].text
    origin = char.findAll("td")[2].text
    release_data_dict[title] = release_date
    origin_data_dict[title] = origin

# fixes a typo in GamePress' data
dfn2.loc[dfn2["Name"] == "Tethys", "Title"] = "Tethys - Beloved Dancer"

# create a new copy of our dataframe
dfn3 = dfn2.copy()

# this function fixes additional issues with title conflicts between
# GamePress and GamePedia
def title_fix(title):
    to_ignore = ["Flame Emperor", "Black Knight", "Death Knight"]
    title_a, title_b = title.split(" -")
    if title_a in to_ignore:
        return title_a + " -" + title_b
    else:
        title_a = title_a.split(" ")[-1]
    return title_a + " -" + title_b

dfn3['Title'] = dfn3['Title'].apply(lambda x: re.sub(r'\([^)]*\) ', '', x)).apply(title_fix)
# split Title into two by the '-'. split the first half by space

release_df = pd.DataFrame.from_dict(release_data_dict, orient = "index", columns = ["Release Date"])
dfn3 = pd.merge(dfn3, release_df, left_on = "Title", right_index = True, how = "left")
origin_df = pd.DataFrame.from_dict(origin_data_dict, orient = "index", columns = ["Origin - GPedia"])
dfn3 = pd.merge(dfn3, origin_df, left_on = "Title", right_index = True, how = "left")

# rename our dataframe
heroes = dfn3
heroes[["HP", "Atk", "Spd", "Def", "Res"]] = heroes[["HP", "Atk", "Spd", "Def", "Res"]].apply(pd.to_numeric)

# set last_update variable to the current month and year
last_update = time.strftime("%m-%y")
# creates a file for .excel and .csv formats
heroes.to_excel("hero_data_" + last_update + ".xlsx", encoding='utf-8', index=False)
heroes.to_csv("hero_data_" + last_update + ".csv", encoding='utf-8', index=False)
