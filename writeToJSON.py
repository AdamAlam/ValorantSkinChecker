import requests
import json
from RSO_AuthFlow import *
from datetime import datetime
today = datetime.today()
datem = datetime(today.year, today.month, today.day)
rn = str(datem)[5:10]

with open("./auth.json") as f:
    actData = json.load(f)
    
with open("./account.json") as account:
    username = json.load(account)['username']

with open("./skins.json") as s:
    skinData = json.load(s)


endpoint = f"https://pd.na.a.pvp.net/store/v2/storefront/{actData['id']}"
headers = {
    "X-Riot-Entitlements-JWT": actData['access'],
    "Content-Type": "application/json",
    "Authorization": f"Bearer {actData['bearer']}"
}


mySkinsJson = requests.get(endpoint, headers=headers).json()


skinIds = []
for skin in mySkinsJson['SkinsPanelLayout']['SingleItemOffers']:
    skinIds.append(skin)
# print(skinIds)

matches = 0
matchedSkins = []
ids = []
for skin in skinData['skinLevels']:
    if matches >= 4:
        break
    id = skin['id'].lower()
    # ids.append(id)
    if id in skinIds:
        matches += 1
        matchName = skin['name']
        matchedSkins.append(matchName)

with open("./../DiscordValSkins/matches.json") as toWrite:
    updateThis = json.load(toWrite)
with open("./matches.json") as localMatches:
    localMatch = json.load(localMatches)
toAppend = {
    "date": rn,
    'skins': matchedSkins}

if toAppend not in updateThis:
    updateThis.append(toAppend)
    with open("./../DiscordValSkins/matches.json", "w") as writeNow:
        writeNow.write(json.dumps(updateThis, indent=2))
if toAppend not in localMatch:
    localMatch.append(toAppend)
    with open("./matches.json", "w") as writeNow1:
        writeNow1.write(json.dumps(localMatch, indent=2))
# print(f"{rn}: | ", end="")
# for i in matchedSkins:
#     print(i, end=" | ")
# print("")


# print(f"{skinIds}\n\n{ids}")
