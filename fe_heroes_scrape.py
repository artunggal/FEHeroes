import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import pandas as pd
import numpy as np

# specify the url
quote_page = "https://fireemblem.gamepress.gg/heroes"

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

opener = Request("https://feheroes.gamepedia.com/Stats_Table",
                headers = {"User-Agent": "Mozilla/5.0"})

# query the website and return the html to the variable 'webpage'

webpage = urlopen(opener).read()

# parse the html using beautiful soup and store in variable 'soup'
soup = BeautifulSoup(webpage, 'html.parser')


# Take out the <div> of name and get its value
right_table=soup.find('table', id = "max-stats-table")
length = len(right_table.findAll("tr"))

# variable placeholders for respective column info for data frame
name = []
color = []
weapon_type = []
mov_type = []
hp = []
atk = []
spd = []
defense = []
res = []
total = []

for row in right_table.findAll("tr"):
    val = []
    val = row["data-weapon-type"].split()
    color.append(val[0])
    weapon_type.append(val[1])
    mov_type.append(row["data-move-type"])
    cells = row.findAll('td')
    name.append(cells[0].findAll('a')[0]["title"])
    hp.append(cells[4].find(text=True))
    atk.append(cells[5].find(text=True))
    spd.append(cells[6].find(text=True))
    defense.append(cells[7].find(text=True))
    res.append(cells[8].find(text=True))
    total.append(cells[9].find(text=True))

# creating the data frame using pandas
df = pd.DataFrame(name,columns=['Name'])
df["Color"] = color
df['Weapon Type'] = weapon_type
df['Movement Type'] = mov_type
df['HP'] = hp
df['Attack'] = atk
df['Speed'] = spd
df['Defense'] = defense
df['Resistance'] = res
df['Total'] = total

################################

#grab universe from link
    
opener2 = Request("https://feheroes.gamepedia.com/Hero_list",
        headers = {"User-Agent": "Mozilla/5.0"})

# query the website and return the html to the variable 'webpage'

universe = urlopen(opener2).read()

# parse the html using beautiful soup and store in variable 'soup'
uni = BeautifulSoup(universe, 'html.parser')

left_table=uni.find('table')
length = len(left_table.findAll("tr"))

# variable placeholders for respective column info for data frame
nombre = []
origin = []
col = []
weap_type = []
move_type = []
rarities = []
st_tt = []
release = []
lgd = []

tab_vals = left_table.findAll("tr")

for ind in range(1, len(tab_vals)):
    val = []
    val = tab_vals[ind]["data-weapon-type"].split()
    cells = tab_vals[ind].findAll("td")
    
    nombre.append(cells[1].findAll('a')[0]["title"])
    origin.append(cells[2].find(text=True))
    rare = (cells[5].findAll(text=True))
    add = []
    legend = False
    for i in np.arange(len(rare)):
        app = "None"
        if str(rare[i]).find("–") != -1:
            rare[i] = str(rare[i]).replace("–", "")
        if rare[i].find(" ") != -1:
            rare[i] = str(rare[i]).replace(" ", "")
        if rare[i] == "TempestTrials":
            app = "Tempest Trials"
        if rare[i] == "GrandHeroBattle":
            app = "Grand Hero Battle"
        if rare[i] == "Story":
            app = "Story"
        if i + 1 == len(rare):
            st_tt.append(app)
        if rare[i] in ("3", "4", "5"):
            add.append(int(rare[i]))
        if rare[i] == "Legendary":
            legend = True
    lgd.append(legend)
    rarities.append(add)
    release.append(cells[6].find(text=True))
    
    
# creating the data frame using pandas
df2 = pd.DataFrame(nombre,columns=['Name'])
df2["Origin"] = origin
df2['Rarities'] = rarities
df2['Story/TT/GHB?'] = st_tt
df2['Release Date'] = release
df2["Legendary"] = lgd

# combining the two dataframes
heroes = pd.merge(df2, df, on = "Name")

heroes
