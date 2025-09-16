import subprocess
from version_info import APP_NAME, APP_VERSION

def sign_exe():
    # Paths and credentials
    signtool_path = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
    pfx_file = r"D:\project\pki\Code_sign_cert\Managex_India_Certificate.pfx"
    pfx_password = "Managex@2024"
    target_exe = rf"D:\project\pki\output\{APP_NAME} Setup {APP_VERSION}.exe"
    timestamp_url = "http://timestamp.comodoca.com"

    # Command to run
    command = [
        signtool_path,
        "sign",
        "/f", pfx_file,
        "/p", pfx_password,
        "/t", timestamp_url,
        "/fd", "sha256",
        "/v", target_exe
    ]

    try:
        print("🔐 Signing EXE file...")
        result = subprocess.run(command, capture_output=True, text=True)
        print("✅ Command executed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except Exception as e:
        print(f"❌ Error while signing: {e}")

if __name__ == "__main__":
    sign_exe()
