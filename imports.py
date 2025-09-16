import requests
import re
from flask import Flask, request, Response, redirect
from flask_cors import CORS
import xml.etree.ElementTree as ET
from image_data import ico, ico_1
from io import BytesIO
import io, base64, tempfile
from PIL import Image, ImageTk
import pystray
import threading
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import PhotoImage
import tkinter.font as tkfont
import socket
import time
import multiprocessing
# from plyer import notification
from winotify import Notification, audio
from utils import get_ip_list, kill_app_if_running
import webbrowser
import re
from doc_utils import fetch_doc_data
import win32event, win32api, win32con, sys, winerror, shutil, json, win32com.client, ctypes, winreg
from config_utils import get_config, save_config, add_to_startup, remove_from_startup, is_in_startup, sync_startup_state_with_config
from admin_rights import run_as_admin
from port_check import check_port_and_notify
from version_info import APP_NAME, APP_VERSION
from urllib.parse import urlparse
import subprocess
