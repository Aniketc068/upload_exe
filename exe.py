from flask import Flask, send_file, request
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONITOR_USER_ID = os.getenv("MONITOR_USER_ID")

app = Flask(__name__)

# Folder paths
EXE_FOLDER = os.path.join(os.getcwd(), "exe")
LOG_FOLDER = os.path.join(os.getcwd(), "logs")
DOWNLOADS_FILE = os.path.join(LOG_FOLDER, "downloads.json")

# Ensure folders exist
os.makedirs(EXE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "✅ Server is running."

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip

def notify_telegram(ip, count):
    try:
        message = f"📥 EXE downloaded from IP: `{ip}`\nTotal Downloads from this IP: {count}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": MONITOR_USER_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Telegram notification failed: {e}")

def update_download_count(ip):
    # Load existing download counts or initialize empty dict
    if os.path.exists(DOWNLOADS_FILE):
        with open(DOWNLOADS_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # Increment count for this IP
    data[ip] = data.get(ip, 0) + 1

    # Save updated counts
    with open(DOWNLOADS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return data[ip]

@app.route('/download')
def download_exe():
    try:
        client_ip = get_client_ip()
        print(f"🔍 Download requested from IP: {client_ip}")

        exe_files = [f for f in os.listdir(EXE_FOLDER) if f.endswith('.exe')]

        if not exe_files:
            return "❌ No .exe file found in 'exe/' folder.", 404

        if len(exe_files) > 1:
            return "⚠️ Multiple .exe files found. Please keep only one.", 400

        exe_file = exe_files[0]
        file_path = os.path.join(EXE_FOLDER, exe_file)

        # Update IP download count
        count = update_download_count(client_ip)

        # Notify on Telegram
        notify_telegram(client_ip, count)

        return send_file(file_path, as_attachment=True, download_name=exe_file)

    except Exception as e:
        return f"Error: {e}", 500

@app.route('/upload', methods=['POST'])
def upload_exe():
    # Case-insensitive file key lookup
    file = next((f for key, f in request.files.items() if key.lower() == 'file'), None)

    if file is None:
        return "❌ No file part in the request (expecting key='file').", 400

    if file.filename == '':
        return "❌ No selected file.", 400

    if not file.filename.endswith('.exe'):
        return "❌ Only .exe files are allowed.", 400

    try:
        # Remove all existing .exe files
        for f in os.listdir(EXE_FOLDER):
            if f.endswith('.exe'):
                os.remove(os.path.join(EXE_FOLDER, f))

        # Save the new file
        save_path = os.path.join(EXE_FOLDER, file.filename)
        file.save(save_path)

        return "✅ EXE uploaded successfully."

    except Exception as e:
        return f"Error while uploading file: {e}", 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000)
