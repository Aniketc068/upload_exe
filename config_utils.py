from imports import *
from pathlib import Path
from version_info import APP_NAME, APP_VERSION

CONFIG_FILE = "config.json"
EXE_NAME = f"{APP_NAME} {APP_VERSION}.exe"

def sync_startup_state_with_config():
    """Sync startup shortcut with config.json setting."""
    config = get_config()
    should_be_in_startup = config.get("startup", False)

    if should_be_in_startup and not is_in_startup():
        add_to_startup()
    elif not should_be_in_startup and is_in_startup():
        remove_from_startup()

def is_in_startup():
    """Check if shortcut exists in the Startup folder."""
    shortcut_path = os.path.join(get_startup_folder(), f"{Path(EXE_NAME).stem}.lnk")
    return os.path.exists(shortcut_path)

def get_config():
    """Load or create config.json with defaults."""
    if not os.path.exists(CONFIG_FILE):
        save_config({"startup": False})
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data: dict):
    """Save dict to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_startup_folder():
    """Return Windows startup folder path."""
    return os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")

def add_to_startup():
    """Create a shortcut to the original exe in the Startup folder."""
    startup_folder = get_startup_folder()
    target = os.path.abspath(EXE_NAME)  # original exe path
    shortcut_path = os.path.join(startup_folder, f"{Path(EXE_NAME).stem}.lnk")

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()
        print("Shortcut created successfully.")
    except Exception as e:
        print("Error creating startup shortcut:", e)

def remove_from_startup():
    """Remove the shortcut from Startup folder."""
    shortcut_path = os.path.join(get_startup_folder(), f"{Path(EXE_NAME).stem}.lnk")
    try:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("Shortcut removed.")
    except Exception as e:
        print("Error removing shortcut:", e)