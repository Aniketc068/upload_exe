from flask import Flask, send_file, abort, request
import os

app = Flask(__name__)

# Folder containing the .exe file
EXE_FOLDER = os.path.join(os.getcwd(), "exe")
os.makedirs(EXE_FOLDER, exist_ok=True)  # Make sure the folder exists

@app.route('/')
def home():
    return "✅ Server is running."

@app.route('/download')
def download_exe():
    try:
        exe_files = [f for f in os.listdir(EXE_FOLDER) if f.endswith('.exe')]

        if not exe_files:
            return "❌ No .exe file found in 'exe/' folder.", 404

        if len(exe_files) > 1:
            return "⚠️ Multiple .exe files found. Please keep only one.", 400

        exe_file = exe_files[0]
        file_path = os.path.join(EXE_FOLDER, exe_file)

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

        # Save the new file with the same name
        save_path = os.path.join(EXE_FOLDER, file.filename)
        file.save(save_path)

        return "✅ EXE uploaded successfully."

    except Exception as e:
        return f"Error while uploading file: {e}", 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000)
