from PyInstaller.__main__ import run
import sys
import os
import subprocess
from imports import *

# Files to include (your own modules)
hidden_imports = [
    "requests",
    "re",
    "flask",
    "flask_cors",
    "xml.etree.ElementTree",
    "PIL",
    "pystray",
    "win32event",
    "win32api",
    "win32con",
    "win32com",
    "ctypes",
    "winreg",
    "winotify",
]

# Define additional files to include
additional_files = [
    ("admin_rights.py", "."),      # Include admin_rights.py in the root directory
    ("config_utils.py", "."),      # Include config_utils.py in the root directory
    ("doc_utils.py", "."),         # Include doc_utils.py in the root directory
    ("image_data.py", "."),        # Include image_data.py in the root directory
    ("imports.py", "."),           # Include imports.py in the root directory
    ("port_check.py", "."),        # Include port_check.py in the root directory
    ("utils.py", "."),             # Include utils.py in the root directory
    ("version_info.py", "."),  
]



# Build options
opts = [
    "PKI_Mod.py",               # Main script
    f"--name={APP_NAME} {APP_VERSION}",       # EXE name
    "--onefile",                 # Single EXE
    "--windowed",                # No console
    f"--icon=C:\\Users\\CISPL\\Downloads\\Lo.ico",  # Custom icon
    "--clean",                   # Clean previous builds
]

# Add hidden imports
for hi in hidden_imports:
    opts.append(f"--hidden-import={hi}")

# Add additional data files
for file, dest in additional_files:
    opts.append(f"--add-data={file}{os.pathsep}{dest}")


# Run PyInstaller to generate EXE
print("Building EXE with PyInstaller...")
run(opts)

# Path to EXE directory
exe_directory = os.path.join(os.getcwd(), 'dist')  # Path to the 'dist' directory
exe_file = os.path.join(exe_directory, f'{APP_NAME} {APP_VERSION}.exe')  # Path to the final EXE file

# Debugging output
print(f"Checking if EXE file exists at: {exe_file}")  # Debugging output
if not os.path.exists(exe_file):
    print(f"Error: EXE file not found at the specified path: {exe_file}")

# Now, use UPX to compress the EXE
upx_path = r"C:\Users\CISPL\Downloads\upx-5.0.2-win64\upx-5.0.2-win64\upx.exe"
print(f"Checking if UPX exists at: {upx_path}")  # Debugging output
if os.path.exists(upx_path) and os.path.exists(exe_file):
    print(f"Compressing EXE with UPX: {exe_file}")
    os.system(f'"{upx_path}" "{exe_file}"')
    print(f"EXE file compressed successfully: {exe_file}")
else:
    if not os.path.exists(exe_file):
        print(f"Error: EXE file not found at: {exe_file}")
    if not os.path.exists(upx_path):
        print(f"Error: UPX executable not found: {upx_path}")

# Path to Signtool and certificate for signing
signtool_path = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
certificate_path = r"D:\project\pki\Code_sign_cert\Managex_India_Certificate.pfx"
certificate_password = "Managex@2024"
timestamp_url = "http://timestamp.comodoca.com"

# EXE file to sign
exe_file = rf"D:\project\pki\dist\{APP_NAME} {APP_VERSION}.exe"

# Sign the EXE file
if os.path.exists(signtool_path) and os.path.exists(exe_file):
    print(f"Signing EXE with certificate: {exe_file}")
    # Create the sign command
    sign_command = [
        signtool_path, 'sign', 
        '/f', certificate_path, 
        '/p', certificate_password, 
        '/t', timestamp_url, 
        '/fd', 'sha256', 
        '/v', exe_file
    ]
    
    # Run the command using subprocess.run, which handles spaces properly
    result = subprocess.run(sign_command, capture_output=True, text=True)
    
    # Check if signing was successful
    if result.returncode == 0:
        print(f"EXE file signed successfully: {exe_file}")
    else:
        print(f"Error signing EXE: {result.stderr}")
else:
    if not os.path.exists(exe_file):
        print(f"Error: EXE file not found at: {exe_file}")
    if not os.path.exists(signtool_path):
        print(f"Error: signtool executable not found: {signtool_path}")