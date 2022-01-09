from discord import Webhook, RequestsWebhookAdapter
import requests
import json
from datetime import datetime
import re
import aiohttp
import asyncio

with open("/root/ValorantSkinChecker/account.json") as f:
# with open("./account.json") as f:
    accountData = json.load(f)


async def run(account, sendStr):
    session = aiohttp.ClientSession()
    data = {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token",
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        "type": "auth",
        "username": account["username"],
        "password": account["password"]
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data) as r:
        data = await r.json()
    # print(data)
    pattern = re.compile(
        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    try:
        data = pattern.findall(data['response']['parameters']['uri'])[0]
    except:
        return
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

    main(entitlements_token, access_token, user_id,
         account['name'], account['matches'], account['discord'], sendStr)

def main(entitlements_token, access_token, user_id, name, wantedMatches, discord, sendStr):
    today = datetime.today()
    datem = datetime(today.year, today.month, today.day,
                     today.hour, today.minute)
    # rn = str(datem)[5:10]
    sendDate = str(datem)[5:10]

    # with open("./skins.json", encoding="utf8") as skinJson:
    with open("/root/ValorantSkinChecker/skins.json") as skinJson:
        skinData = json.load(skinJson)

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
    # with open("/root/ValorantSkinChecker/webhooks.json") as webhooks:
    '''with open("./webhookTest.json") as webhooks:
        webhooksJSON = json.load(webhooks)'''


    '''for webhook in webhooksJSON:
        wburl = Webhook.from_url(
            webhooksJSON[webhook], adapter=RequestsWebhookAdapter())
        if not wanted:
            try:
                strToSend = f"{name}: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
            except IndexError:
                strToSend = f"{name}: {sendDate} "
                for skin in matchedSkins:
                    strToSend += f"{skin} "

        else:
            try:
                for i in range(len(matchedSkins)):
                    if matchedSkins[i].lower() in wantedMatches:
                        matchedSkins[i] = f"***{matchedSkins[i]}***"
                strToSend = f"***MATCH FOUND*** <@{discord}>: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
            except IndexError:
                strToSend = f"***MATCH FOUND*** <@{discord}>: {sendDate} "
                for skin in matchedSkins:
                    strToSend += f"{skin} "
        wburl.send(strToSend)'''
    if not wanted:
        try:
            strToSend = f"{name}: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
        except IndexError:
            strToSend = f"{name}: {sendDate} "
            for skin in matchedSkins:
                strToSend += f"{skin} "
    else:
        try:
            strToSend = f"***MATCH FOUND*** <@{discord}>: {sendDate} {matchedSkins[0]} | {matchedSkins[1]} | {matchedSkins[2]} | {matchedSkins[3]}"
        except IndexError:
            strToSend = f"***MATCH FOUND*** <@{discord}>: {sendDate} "
            for skin in matchedSkins:
                strToSend += f"{skin} "
    sendStr.append(strToSend)


if __name__ == '__main__':
    sendStr = []
    toSend = ""
    for account in accountData:
        asyncio.get_event_loop().run_until_complete(run(account, sendStr))
    with open("./webhooks.json") as webhooks:
    # with open("./webhookTest.json") as webhooks:
        webhooksJSON = json.load(webhooks)
    for i in range(len(sendStr)-1):
        toSend += f"{sendStr[i]}\n\n"
    toSend += f"{sendStr[-1]}"
        
    for webhook in webhooksJSON:
        wburl = Webhook.from_url(
        webhooksJSON[webhook], adapter=RequestsWebhookAdapter())
        wburl.send(toSend)
    
        