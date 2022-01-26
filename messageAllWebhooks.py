from discord import Webhook, RequestsWebhookAdapter
import json


strToSend = "From Adam: Hello everyone. Riot shut down user-specific API calls to retreive account speicific information. As a result, it is no longer possible to keep this bot running unless they change their API rules so that information specific to users can be accessed. Until then, skin updates will be paused. I will do a little more debugging to check whether the problem is on my end, but I am fairly certain that Riot has changed how users are able to use their API."


def main():
    urlArr = []
    with open("./webhooks.json") as webhooks:
        webhooksJSON = json.load(webhooks)

    for webhook in webhooksJSON:
        urlArr.append(Webhook.from_url(
            webhooksJSON[webhook], adapter=RequestsWebhookAdapter()))

    for wburl in urlArr:
        wburl.send(strToSend)


main()
