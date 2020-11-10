import requests
from urllib.request import urlretrieve

file_version = 1.0  # This will need to be updated along with the github .txt to push an update.
version_url = "https://raw.githubusercontent.com/gavinnn101/Account-Creator/main/version.txt"


def get_update_link():
    api_key = "408afbecad4a60f45fffc17542961094b1fba173a4c7b82b56154132919897d7"
    try:
        session = requests.get(f"https://apiv2.gofile.io/getUploadsList?token={api_key}").json()
    except Exception as e:
        print(e)
        print("Send the above error to Gavin.")
    else:
        download_code = session['data']['0']['code']
        server = session['data']['0']['server']
        link = f"https://{server}.gofile.io/download/{download_code}/Gavin's%20Account%20Creator.exe"
        return link


def get_version():
    session = requests.get(version_url)
    version = session.text.strip()
    return float(version)


def check_update():
    newest_version = get_version()
    if file_version < newest_version:
        print(f"We have version: {file_version} installed. The latest version is: {newest_version}.")
        install_update(newest_version)
        return False
    else:
        print(f"We're using version: {file_version} and it's the most current build.")
        return True


def install_update(new_version):
    new_name = f"Gavin's Account Creator {new_version}.exe"
    print(f"Installing version: {new_version}")
    try:
        urlretrieve(get_update_link(), new_name)
    except Exception as e:
        print("Got an error:\n")
        print(e)
    else:
        print(f"{new_name} has been installed to the local directory. Feel free to delete the previous version.")
