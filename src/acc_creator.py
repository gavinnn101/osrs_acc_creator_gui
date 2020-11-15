"""Creates accounts based on settings.ini using our logic modules"""
#!/usr/bin/env python3
import sys
import random
import string
import sys
import time
from src.modules.helper_modules.utility import (timestamp, read_proxy, get_user_settings, get_tribot_settings, get_osbot_settings)
from src.modules.bot_client_cli.tribot_cli import use_tribot
from src.modules.bot_client_cli.osbot_cli import use_osbot
import requests


HEADERS = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Origin': 'https://secure.runescape.com',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://secure.runescape.com/l=en/a=0/m=account-creation/g=oldscape/create_account?mod=os-mobile&ssl=1&dest=/mobile/play',
    'Accept-Language': 'en-US,en;q=0.9',
}


try:
    PROXY_LIST = open("../src/settings/proxy_list.txt", "r")
except FileNotFoundError:
    sys.exit("proxy_list.txt wasn't found. "
             "Make sure it's in the settings directory.")

# The secret sauce
SITE_URL = "https://secure.runescape.com/l=en/a=0/m=account-creation/g=oldscape/create_account"


def get_ip() -> str:
    """
    Gets the user's external IP that will be used to create the account.
    Because of external dependency, we have a backup site to pull from if needed
    """
    users_ip = requests.get('https://api.ipify.org').text
    if not users_ip:
        users_ip = requests.get('http://ip.42.pl/raw').text
    return users_ip


def get_proxy() -> dict:
    """
    Returns our next proxy to use from the proxy_list.txt file.
    If we run out of proxies before we make all of the accounts, return to top.
    """
    try:
        proxy = {"https": (next(PROXY_LIST))}
        return proxy
    except StopIteration:
        # We'll return to the top of our list once we run out of proxies
        PROXY_LIST.seek(0)
        proxy = {"https": (next(PROXY_LIST))}
        return proxy


def get_payload() -> dict:
    """
    Generates and fills out our payload.
    returns:
    payload (dict): account creation payload data
    """
    # Get username/password options from settings.ini
    email = get_user_settings()[5]
    password = get_user_settings()[6]

    if not email:  # We aren't using a custom username prefix -> make it random
        email = ''.join([random.choice(string.ascii_lowercase + string.digits)
                         for n in range(6)]) + '@gmail.com'
    else:  # We're using a custom prefix for our usernames
        email = email + str(random.randint(1000, 9999)) + '@gmail.com'
    if not password:
        password = email[:-10] + str(random.randint(1, 9999))

    # Generate random birthday for the account
    day = str(random.randint(1, 25))
    month = str(random.randint(1, 12))
    year = str(random.randint(1980, 2006))  # Be at least 13 years old

    payload = {
        'theme': 'oldschool',
        'mod': 'os-mobile',
        'ssl': '1',
        'dest': '%2Fmobile%2Fplay',
        'email1': email,
        'onlyOneEmail': '1',
        'password1': password,
        'onlyOnePassword': '1',
        'day': day,
        'month': month,
        'year': year,
        'create-submit': 'create'
    }
    return payload


def check_account(submit):
    """Checks to make sure the account was successfully created"""
    if 'account_created?tracker=' in submit.url:
        return True
    else:
        return False


def save_account(payload, proxy=None):
    """Save the needed account information to created_accs.txt"""
    USE_PROXIES = get_user_settings()[0]
    if USE_PROXIES:
        proxy_auth_type = get_user_settings()[1]
        proxy_ip = read_proxy(proxy, proxy_auth_type)[2]
        proxy = proxy_ip

    else:
        proxy = get_ip()

    # Check if we want user friendly formatting or bot manager friendly
    acc_details_format = get_user_settings()[7]
    if acc_details_format:
        formatted_payload = (f"\nemail:{payload['email1']}, password:{payload['password1']},"
                             f" Birthday:{payload['month']}/{payload['day']}/{payload['year']},"
                             f" Proxy:{proxy}")
    else:
        formatted_payload = f"\n{payload['email1']}:{payload['password1']}"

    with open("../src/created_accs.txt", "a+") as acc_list:
        acc_list.write(formatted_payload)
    return formatted_payload


def create_account(append_text, progress_callback):
    """Creates our account and returns the registration info"""
    NUM_OF_ACCS = get_user_settings()[4]
    TRIBOT_ACTIVE = get_tribot_settings()[0]
    OSBOT_ACTIVE = get_osbot_settings()[0]
    USE_PROXIES = get_user_settings()[0]
    sleep_timer = get_user_settings()[8]

    accs_created = 0  # initialize
    failure_counter = 0  # initialize
    failure_threshold = 3  # If we fail this many times, the script will stop.

    progress_callback.emit(f"\nWe'll make: {NUM_OF_ACCS} accounts.")
    progress_callback.emit(f"Will we use proxies?: {USE_PROXIES}")
    progress_callback.emit(f"Will we use Tribot CLI?: {TRIBOT_ACTIVE}")
    progress_callback.emit(f"Will we use OSBot CLI?: {OSBOT_ACTIVE}")
    progress_callback.emit("\nNeed Support? Join the discord - https://discord.gg/SjVjQvm\n")

    while accs_created < NUM_OF_ACCS:
        if NUM_OF_ACCS == 0:
            break
        progress_callback.emit(f"\nSleeping for {sleep_timer} seconds...")
        time.sleep(sleep_timer)

        progress_callback.emit(f"{timestamp()}Starting create_account()")

        if USE_PROXIES:
            proxy = get_proxy()
        else:
            proxy = None

        progress_callback.emit(f"Proxy: {proxy}")

        payload = get_payload()
        submit = requests.post(SITE_URL, headers=HEADERS, data=payload, proxies=proxy)
        if submit.ok:
            if check_account(submit):
                progress_callback.emit("Account created successfully.")
                accs_created += 1
                formatted_payload = save_account(payload, proxy=proxy)
                progress_callback.emit(f"Account created with the details: {formatted_payload}")
                if TRIBOT_ACTIVE:
                    cmd = use_tribot(payload['email1'], payload['password1'], proxy)
                    progress_callback.emit("\nLoading Tribot with the following settings...")
                    progress_callback.emit(cmd)
                elif OSBOT_ACTIVE:
                    cmd = use_osbot(payload['email1'], payload['password1'], proxy)
                    progress_callback.emit("\nLoading OSBot with the following settings...")
                    progress_callback.emit(cmd)

            else:
                progress_callback.emit("Account creation failed.")
                failure_counter += 1
                if failure_counter == failure_threshold:
                    progress_callback.emit(f"Failed {failure_counter} times. Let your IP cool down or up the sleep timer.")
                    accs_created = NUM_OF_ACCS  # End the creation loop
                    progress_callback.emit("Finished creating accounts.")
        else:
            progress_callback.emit(f"Creation failed. Error code {submit.status_code}")
            progress_callback.emit(submit.text)
    progress_callback.emit(f"\n{timestamp()}Finished creating accounts.")
