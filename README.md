# Valorant Skin Checker

## Getting Started

1. Create account.json and webhooks.json files using the templates provided.
   1. Fill out our account information in accountTemplate.json
      - Note that password and skin matches are case sensitive.
   2. Add your discord webhook urls to webhooksTemplate.json
   3. Rename these files to **account.json** and **webhooks.json**.
2. Install Python Packages using Pip.
   - CD into your project directory using a terminal and run the command: ` python3 -m pip install -r requirements.txt`
3. CD into the project directory using a terminal and run `python3 CheckSkins.py`

## Automation

The most efficient way of using this tool is setting it to run at around 7:01 PM CT so that you get updates as soon as the shop updates. I have tried getting it to run at exactly 7:00 PM, the Riot Client API is a little slow and does not always return the updated shop.

This process can be automated through several tools. The tool that I currently use is crontab running on a CentOS machine as a DigitalOcean droplet. If you decide to go this route, you will have to change the [CheckSkins.py](CheckSkins.py) file so that it does not do relative opens. This means changing the path to the file everytime: `with open(<path to file>) as <file>` this appears in [CheckSkins.py](CheckSkins.py).

More information about Crontab can be found [here](https://man7.org/linux/man-pages/man5/crontab.5.html).

The command that I use is: `1 19 * * * /usr/bin/python3 /root/ValorantSkinChecker/CheckSkins.py`
