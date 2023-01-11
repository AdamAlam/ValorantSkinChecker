import asyncio
import aiohttp
import re
from datetime import datetime
import json
import requests
from discord import Webhook, RequestsWebhookAdapter, Embed
from time import time
startTime = time()

with open("/root/ValorantSkinChecker/account.json") as f:
    accountData = json.load(f)

with open("/root/ValorantSkinChecker/webhooks.json") as webhooks:
    webhooksJSON = json.load(webhooks)
urlArr = []
for webhook in webhooksJSON:
    urlArr.append(Webhook.from_url(
        webhooksJSON[webhook], adapter=RequestsWebhookAdapter()))

today = datetime.today()
datem = datetime(today.year, today.month, today.day,
                 today.hour, today.minute)
sendDate = str(datem)[5:10]

jsonArray = []


async def run(account):
    session = aiohttp.ClientSession()
    data = {
        "client_id": "play-valorant-web-prod",
        "nonce": 1,
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token"
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    r1 = await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

    data = {
        "type": "auth",
        "username": account["username"],
        "password": account["password"],
        "language": "en_US",
        "region": None,
        "remember": False,
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers) as r:
        data = await r.json()
    pattern = re.compile(
        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    try:
        data = pattern.findall(data['response']['parameters']['uri'])[0]
    except:
        print(f"Error with account {account['username']}")
        await session.close()
        return
    access_token = data[0]

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
        data = await r.json()
    entitlements_token = data['entitlements_token']

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
        data = await r.json()
    user_id = data['sub']
    headers['X-Riot-Entitlements-JWT'] = entitlements_token

    async with session.post(f'https://pd.na.a.pvp.net/name-service/v1/players', headers=headers) as r:
        data = json.loads(await r.text())
    toDump = {"access": entitlements_token,
              "bearer": access_token, "id": user_id}

    with open("/root/ValorantSkinChecker/auth.json", "w") as acc:
        acc.write(json.dumps(toDump))

    try:
        await session.close()
    except:
        print("Error when closing session")

    main(entitlements_token, access_token, user_id,
         account['name'], account['matches'], account['discord'])


def main(entitlements_token, access_token, user_id, name, wantedMatches, discord):

    with open("/root/ValorantSkinChecker/skins.json") as s:
        skinData = json.load(s)

    endpoint = f"https://pd.na.a.pvp.net/store/v2/storefront/{user_id}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlements_token,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    mySkinsJson = requests.get(endpoint, headers=headers).json()

    skinIds = []
    for skin in mySkinsJson['SkinsPanelLayout']['SingleItemOffers']:
        skinIds.append(skin)

    wanted = False
    matchedSkins = list(
        filter(lambda skin: skin['levels'][0]['uuid'] in skinIds, skinData['data']))
    for skin in matchedSkins:
        if skin['displayName'].lower() in wantedMatches:
            wanted = True

    matchedSkinsPics = []
    for skin in matchedSkins:
        toAppend = skin['displayIcon'] if skin['displayIcon'] else skin['chromas'][0]['displayIcon']
        matchedSkinsPics.append(toAppend)

    try:
        strToSend = Embed()
        strToSend.set_author(name=name)
        strToSend.description = f"[{matchedSkins[0]['displayName']}]({matchedSkinsPics[0]}) | [{matchedSkins[1]['displayName']}]({matchedSkinsPics[1]}) | [{matchedSkins[2]['displayName']}]({matchedSkinsPics[2]}) | [{matchedSkins[3]['displayName']}]({matchedSkinsPics[3]})"
        # for i in range(4):
        #     strToSend.add_field(name=i+1, value=f"[{matchedSkins[i]['displayName']}]({matchedSkinsPics[i]})")
    except:
        pass

    for wburl in urlArr:
        if wanted:
            wburl.send(f"***MATCH FOUND*** <@{discord}>")
        wburl.send(embed=strToSend)

    skinObect = {0: {}, 1: {}, 2: {}, 3: {}, "account": discord}
    for i in range(4):
        skinObect[i] = {"name": matchedSkins[i]
                        ['displayName'], "link": matchedSkinsPics[i]}
    jsonArray.append(skinObect)


if __name__ == '__main__':
    for wburl in urlArr:
        try:
            wburl.send(sendDate)
        except:
            pass
    for account in accountData:
        asyncio.get_event_loop().run_until_complete(run(account))
    with open("/root/ValorantSkinChecker/API/userSkinData.json", "w") as usd:
        usd.write(json.dumps(jsonArray))
    endTime = time()
    for wburl in urlArr:
        try:
            pass
            wburl.send(f"Completed in {round(endTime-startTime, 2)} seconds.")
        except:
            pass
