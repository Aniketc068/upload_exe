from imports import *
import psutil
import platform
from version_info import APP_NAME, APP_VERSION

# Telegram config
TELEGRAM_BOT_TOKEN = ''
MONITOR_USER_ID = ''

def get_ip_list():
    ip_list = ["127.0.0.1"]  # always include localhost

    try:
        # detect main LAN IP (IPv4 only)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("8.8.8.8", 80))   # dummy connect (Google DNS)
        local_ip = s.getsockname()[0]
        s.close()

        if local_ip not in ip_list:
            ip_list.append(local_ip)
    except:
        pass

    return ip_list

def kill_app_if_running(exe_name: str):
    """
    Kill all running instances of a given executable.
    Waits a bit to ensure port/resources are freed.
    """
    killed_any = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                proc.kill()
                killed_any = True
                print(f"⛔ {exe_name} was running → killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if killed_any:
        time.sleep(2)  # ensure resources/port are freed

def gather_system_info():
    """Return system info as string"""
    hostname = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    user_name = os.getlogin()
    ips = [ip for ip in get_ip_list() if ip != "127.0.0.1"]
    ip_str = ', '.join(ips) if ips else 'No external IP found'

    info = (
        f"===== System Information =====\n"
        f"Desktop Name: {hostname}\n"
        f"Operating System: {os_info}\n"
        f"Logged-in User: {user_name}\n"
        f"IP Addresses: {ip_str}\n"
        f"{APP_NAME} {APP_VERSION} is running on this system ✅\n"
        f"=============================="
    )
    return info

def print_system_info():
    info = gather_system_info()
    print(info)
    send_telegram_message(info)

def send_telegram_message(message: str):
    """Send message to Telegram user via bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": MONITOR_USER_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ System info sent to Telegram successfully.")
        else:
            print(f"⚠️ Telegram API returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")


