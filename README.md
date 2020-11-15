# Gavin's OSRS Account Creator - GUI Edition

Gavin's OSRS Account Creator is a python program that is used to create Runescape accounts without the use of captcha solvers or proxies(optional.) Includes OSBot/Tribot CLI integration to automatically run scripts after creation, custom username/password, etc in an easy to use GUI.

# Feature List

  - OSRS Account settings
    - Custom username prefix
    - Custom password
  - Creator Settings
    - Number of accounts to create
    - Custom sleep timer between account creations (for IP cooldown, etc)
    - Proxy support (username/password or IP Authentication supported)
  - Bot Client Settings (Tribot/OSBot - optional)
    - Use any script in your account's repo (script arguments supported)
    - OSBot:
      - Can use a local script via script name or an SDN script via script ID(https://osbot.org/forum/topic/155007-how-to-find-script-id-for-free-scripts/)
      - For OSBot, make sure the "script args" field is set to "none" if you dont want to provide arguments. 
  - Creator GUI features
    - Multithreaded so no freezes or glitches while creating accounts
    - Save full console output to log file
    - Clear contents of console
    - Create accounts (Will run based on how many accounts to create setting)
        - Created accounts will save to created_accs.txt file in program's folder in username:password format
    - Proxy Manager
      - Add and remove proxies to use for account creation and bot client CLI
        - NOTE: If the proxy doesn't use a username and password, leave the fields blank.

Support, requests, etc can be found on discord: https://discord.gg/SjVjQvm

twocaptcha.com referral: https://2captcha.com?from=8817486

anticaptcha.com referral: http://getcaptchasolution.com/njbmecwjpo


## Usage

Edit the osrs_acc_creator_master/src/settings/settings.ini to include your license key and then you can run the Account Creator program.

## License
[GPL](https://choosealicense.com/licenses/gpl-3.0/)
