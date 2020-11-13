"""Contains all of the content to implement Tribot CLI"""
# Tribot CLI:
# https://help.tribot.org/support/solutions/articles/36000043771-how-to-use-cli-arguments-to-launch-tribot

import glob
import os
import subprocess
import getpass
from src.modules.helper_modules.utility import (get_user_settings, read_proxy, get_tribot_settings)


# def find_tribot():
#     """
#     Finds the user's tribot.jar for CLI use
#     This currently only supports the default Windows path.
#     TODO: Add support for mac and linux paths
#     """
#     user = getpass.getuser()
#     path = f"C:\\Users\\{user}\\AppData\\Roaming\\.tribot\\dependancies"
#
#     print("")
#     print("Changing to our Tribot directory")
#     os.chdir(path)
#     print(os.getcwd())
#
#     client = str(glob.glob('tribot*'))
#     client = client[2:-2]
#     print(f"Our Tribot client is called: {client}")
#
#     return client


def use_tribot(charname, charpass, proxy=None):
    """Gets settings and runs Tribot CLI"""
    # Storing all of our settings while we're in the correct directory
    use_proxies = get_user_settings()[0]
    proxy_auth_type = get_user_settings()[1]
    tribot_username = get_tribot_settings()[1]
    tribot_password = get_tribot_settings()[2]
    tribot_script = get_tribot_settings()[3]
    script_args = get_tribot_settings()[4]

    if use_proxies:
        proxy_auth_type = get_user_settings()[1]
        proxy_username, proxy_password, proxy_ip, proxy_port = read_proxy(proxy, proxy_auth_type)

    original_path = os.getcwd()
    os.chdir("../src/TRiBot/tribot-gradle-launcher/")

    # Create our CLI command according to if we're using proxies or not
    if use_proxies:
        if proxy_auth_type == 1:  # Using proxies with user:pass authentication
            cli_cmd = (f'gradlew.bat runDetached '
                       f'--username "{tribot_username}" --password "{tribot_password}" '
                       f'--charusername "{charname}" --charpassword "{charpass}" '
                       f'--script "{tribot_script}" --scriptargs "{script_args} " '
                       f'--charworld "433" ' 
                       f'--proxyhost "{proxy_ip}" '
                       f'--proxyport "{proxy_port}" '
                       f'--proxyusername "{proxy_username}" '
                       f'--proxypassword "{proxy_password}" ')
        else:  # Using proxies with IP based authentication
            cli_cmd = (f'gradlew.bat runDetached '
                       f'--username "{tribot_username}" --password "{tribot_password}" '
                       f'--charusername "{charname}" --charpassword "{charpass}" '
                       f'--script "{tribot_script}" --scriptargs "{script_args} " '
                       f'--charworld "433" '
                       f'--proxyhost "{proxy_ip}" '
                       f'--proxyport "{proxy_port}" ')
    else:  # Not using proxies
        cli_cmd = (f'gradlew.bat runDetached '
                   f'--username "{tribot_username}" --password "{tribot_password}" '
                   f'--charusername "{charname}" --charpassword "{charpass}" '
                   f'--script "{tribot_script}" --scriptargs "{script_args} " '
                   f'--charworld "433" ')

    # Run the Tribot CLI in a separate, hidden shell to decrease clutter
    create_no_window = 0x08000000
    subprocess.Popen(f"start /B start cmd.exe @cmd /k {cli_cmd}", shell=True,
                     creationflags=create_no_window)

    # Changing back to the account creator directory
    # So we can see the settings.ini file for the next account.
    os.chdir(original_path)

    return cli_cmd
