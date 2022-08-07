import json
import urllib.request

def getSkinData():
    url = "https://valorant-api.com/v1/weapons/skins"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    jsonObject = json.dumps(data, indent=4)
    with open("/root/ValorantSkinChecker/skins.json", "w") as outfile:
        outfile.write(jsonObject)

if __name__ == "__main__":
    getSkinData()