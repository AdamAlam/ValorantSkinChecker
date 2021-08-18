from discord import Webhook, RequestsWebhookAdapter
import requests
import json
from datetime import datetime
import re
import aiohttp
import asyncio

with open("./account.json") as f:
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
    # print(f"\nAccess Token {access_token}\n")
    # id_token = data[1]
    # expires_in = data[2]

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
    # await session.close()

    # print(data)

    toDump = {"access": entitlements_token,
              "bearer": access_token, "id": user_id, "name": account['name']}

    with open("./auth.json", "w") as acc:
        acc.write(json.dumps(toDump))

    await session.close()
    
    print(f"entitlements_token:{entitlements_token}\n\naccess_token:{access_token}\n\nuser_id:{user_id}\n\naccount:{account['name']}")
    main(entitlements_token, access_token, user_id, account['name'])


def main(entitlements_token, access_token, user_id, name):
    today = datetime.today()
    datem = datetime(today.year, today.month, today.day,
                     today.hour, today.minute)
    sendDate = str(datem)

    with open("./auth.json") as f:
        actData = json.load(f)

    with open("./skins.json") as s:
        skinData = json.load(s)

    endpoint = f"https://pd.na.a.pvp.net/mmr/v1/players/{user_id}/competitiveupdates"
    headers = {
        "X-Riot-Entitlements-JWT": entitlements_token,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Riot-ClientPlatform":"ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-ClientVersion" : "release-02.01-shipping-6-511946"
    }

    mySkinsJson = requests.get(endpoint, headers=headers).json()
    print(mySkinsJson)

    # skinIds = []
    # for skin in mySkinsJson['SkinsPanelLayout']['SingleItemOffers']:
    #     skinIds.append(skin)

    # matches = 0
    # matchedSkins = []
    # for skin in skinData['skinLevels']:
    #     if matches >= 4:
    #         break
    #     id = skin['id'].lower()
    #     if id in skinIds:
    #         matches += 1
    #         matchName = skin['name']
    #         matchedSkins.append(matchName)
    # webhookURL = "https://discord.com/api/webhooks/874716318509699092/Ln1FTTDNGqSiRZMs8S4k69OH2aUgbSkPI8vbAVzsMfvtK4FQlunqWrpdTpNUWkFuf3kH"

    # webhook = Webhook.from_url(webhookURL, adapter=RequestsWebhookAdapter())
    # strToSend = f"{name}: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
    # webhook.send(strToSend)
    


if __name__ == '__main__':
    for account in accountData:
        asyncio.get_event_loop().run_until_complete(run(account))
        break
    
