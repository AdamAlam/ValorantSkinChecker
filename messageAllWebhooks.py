from discord import Webhook, RequestsWebhookAdapter
import json


strToSend = "Enter message here"


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
