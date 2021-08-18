from discord import Webhook, RequestsWebhookAdapter
import requests
import json
from datetime import datetime
import re
import aiohttp
import asyncio

# For CentOS Server:
with open("/root/ValorantSkinChecker/account.json") as f:
    accountData = json.load(f)



async def run(account):
    session = aiohttp.ClientSession()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        'type': 'auth',
        'username': account['username'],
        'password': account['password']
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data) as r:
        data = await r.json()
    # print(data)
    pattern = re.compile(
        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(data['response']['parameters']['uri'])[0]
    access_token = data[0]

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
        data = await r.json()
    entitlements_token = data['entitlements_token']
    # print(f"Entitlement Token: {entitlements_token}\n")

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
        data = await r.json()
    user_id = data['sub']
    # print('User ID: ' + user_id)
    headers['X-Riot-Entitlements-JWT'] = entitlements_token

    # Example Request. (Access Token and Entitlements Token needs to be included!)
    async with session.post(f'https://pd.na.a.pvp.net/name-service/v1/players', headers=headers) as r:
        data = json.loads(await r.text())
    toDump = {"access": entitlements_token,
              "bearer": access_token, "id": user_id}

    with open("/root/ValorantSkinChecker/auth.json", "w") as acc:
        # with open("./auth.json", "w") as acc:
        acc.write(json.dumps(toDump))

    await session.close()
    main(entitlements_token, access_token, user_id, account['name'], account['matches'], account['discord'])


def main(entitlements_token, access_token, user_id, name, wantedMatches, discord):
    today = datetime.today()
    datem = datetime(today.year, today.month, today.day,
                     today.hour, today.minute)
    # rn = str(datem)[5:10]
    sendDate = str(datem)[5:10]

    # with open("./auth.json") as f:
    with open("/root/ValorantSkinChecker/auth.json") as f:
        actData = json.load(f)

    # with open("./skins.json") as s:
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
    # print(skinIds)

    wanted = False
    matches = 0
    matchedSkins = []
    for skin in skinData['skinLevels']:
        if matches >= 4:
            break
        id = skin['id'].lower()
        # ids.append(id)
        if id in skinIds:
            matches += 1
            matchName = skin['name']
            matchedSkins.append(matchName)
            if matchName.lower() in wantedMatches:
                wanted = True
    with open("/root/ValorantSkinChecker/webhooks.json") as webhooks:
        webhooksJSON = json.load(webhooks)
    
    for webhook in webhooks:
        wburl = Webhook.from_url(webhooksJSON[webhook], adapter=RequestsWebhookAdapter())
        if not wanted:
            strToSend = f"{name}: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
        else:
            strToSend = f"***MATCH FOUND*** <@{discord}>: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
        wburl.send(strToSend)


if __name__ == '__main__':
    for account in accountData:
        try:
            main(account)
        except:
            asyncio.get_event_loop().run_until_complete(run(account))
