from imports import *
from utils import print_system_info

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


server_process = None
current_ip, current_port = None, None
IS_DISCONTINUED = False
popup_window = None

# base64 → ico temp file
ICON_PATH = os.path.join(os.getenv("TEMP"), "pki_icon.ico")
with open(ICON_PATH, "wb") as f:
    f.write(base64.b64decode(ico))

get_ip_list()

doc_data = fetch_doc_data()


if doc_data:
    signed_value = doc_data.get("signed_value")
    status_value = doc_data.get("status")
    version_value = doc_data.get("version")
    url_value = doc_data.get("url")
    allowed_domains = doc_data.get("domains", [])
    Approval_data = doc_data.get("approval_value")
    approval_setting = doc_data.get("approval_setting")





data_lock = threading.Lock()

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def catch_all(path):
    global allowed_domains
    origin = request.headers.get("Origin", "").lower()
    host = request.headers.get("Host", "").lower()
    user_agent = request.headers.get("User-Agent", "").lower()


    # 1️⃣ Fetch latest Google Doc data
    doc_data = fetch_doc_data()
    if doc_data:
        signed_value = doc_data.get("signed_value")
        allowed_domains = doc_data.get("domains", [])

    # 🔄 Fetch domains from Google Doc
    allowed_domains = [d.strip().lower() for d in allowed_domains]
    allowed_hosts = [urlparse(d).hostname for d in allowed_domains if d]

    # 2️⃣ Load config.json every request
    config = {}
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    # 1️⃣ Requests coming from allowed domains → XML
    if origin in allowed_domains or host in allowed_hosts:
        pki_command = "UNKNOWN"
        pki_ts = "UNKNOWN"
        pki_txn = "UNKNOWN"
        pki_file_type = "UNKNOWN"
        pki_email = "UNKNOWN"
        xml_str = None

        if "response" in request.form:
            xml_str = request.form["response"]
        elif request.data:
            xml_str = request.data.decode("utf-8", errors="ignore")

        # Parse XML if present
        if xml_str:
            try:
                root = ET.fromstring(xml_str)
                cmd_elem = root.find("command")
                if cmd_elem is not None and cmd_elem.text:
                    pki_command = cmd_elem.text.strip()
                ts_elem = root.find("ts")
                if ts_elem is not None and ts_elem.text:
                    pki_ts = ts_elem.text.strip()
                txn_elem = root.find("txn")
                if txn_elem is not None and txn_elem.text:
                    pki_txn = txn_elem.text.strip()
                file_type_elem = root.find("file/attribute[@name='type']")
                if file_type_elem is not None and file_type_elem.text:
                    pki_file_type = file_type_elem.text.strip()
                email_elem = root.find(".//attribute[@name='E']")
                if email_elem is not None and email_elem.text:
                    pki_email = email_elem.text.strip()
            except:
                pass

        # Determine data dynamically based on approvals
        signed_data = signed_value  # default
        if config.get("enable_approvals") is True:
            data_file = "data_response"
            if os.path.exists(data_file):
                with data_lock:
                    with open(data_file, "r", encoding="utf-8") as df:
                        signed_data = df.read()
                        print("🔁 Using internal 'data_response' file")
            else:
                print("⚠️ 'data_response' file not found. Falling back to Google Doc.")
        else:
            print("🌐 Using Google Doc 'signed_value'")

        raw_xml = f"""<response>
<command>{pki_command}</command>
<ts>{pki_ts}</ts>
<mac>{pki_email}</mac>
<txn>{pki_txn}</txn>
<status>ok</status>
<file>
<attribute name='type'>{pki_file_type}</attribute>
</file>
<data>{signed_data}</data>
</response>"""
        return Response(raw_xml, mimetype="text/plain; charset=utf-8")

    # 2️⃣ Browser → redirect to PKI network
    browser_signals = ["mozilla", "chrome", "safari", "edge", "firefox", "opera"]
    if any(signal in user_agent for signal in browser_signals):
        return redirect("https://www.pki.network/", code=302)

    # 3️⃣ Everything else → Postman, curl, scripts
    return Response(f"😁 Welcome to {APP_NAME} {APP_VERSION} By Aniket Chaturvedi", mimetype="text/plain; charset=utf-8")




# ================= Tray Icon Code ==================
def get_icon():
    icon_data = base64.b64decode(ico)
    image = Image.open(BytesIO(icon_data))
    return image



def notify(title, message):
    try:
        toast = Notification(
            app_id=f"{APP_NAME} {APP_VERSION}",          # yaha apna naam likho, "Python" nhi aayega
            title=title,
            msg=message,
            icon=ICON_PATH
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception as e:
        print("Notification error:", e)

# Function to check if port is available
def is_port_available(ip, port):
    try:
        # Try to bind to the socket with the provided IP and port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, port))
            return True
    except socket.error:
        return False


# ---------- Flask Run Process ----------
def start_flask(ip, port):
    app.run(host=ip, port=port, debug=False, use_reloader=False)

def run_server(ip, port):
    global server_process, current_ip, current_port

    if multiprocessing.current_process().name != "MainProcess":
        # Prevent child process from spawning new server
        return
    
    # Check if the port is available
    if not is_port_available(ip, port):
        # If the port is not available, notify the user
        notify("Port Availability", f"🚫 Port {port} is already in use! Please choose another port.")
        return

    if server_process is not None and server_process.is_alive():
        notify(f"{APP_NAME} {APP_VERSION}", f"🔴 Server stopped at {current_ip}:{current_port}")
        server_process.terminate()
        server_process.join()
        time.sleep(1)

    server_process = multiprocessing.Process(target=start_flask, args=(ip, port), daemon=True)
    server_process.start()

    current_ip, current_port = ip, port
    notify(f"{APP_NAME} {APP_VERSION}", f"🟢 Server running at {ip}:{port}")

# 🔐 Global Mutex Handle
mutex = None

def acquire_mutex():
    global mutex
    mutex = win32event.CreateMutex(None, False, "PKIMOD_MUTEX")  # unique name
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        # Agar pehle se ek instance run ho raha hai → custom popup
        show_already_running()
        sys.exit(0)

def release_mutex():
    global mutex
    if mutex:
        win32api.CloseHandle(mutex)
        mutex = None

def show_discontinued_popup(discontinue_type="global", restricted_ip=None):
    """
    Shows a discontinued popup safely without hanging the app.
    discontinue_type: "global" or "ip"
    restricted_ip: If IP-specific, the IP string
    """
    global server_process, current_ip, current_port, icon, root, IS_DISCONTINUED

    IS_DISCONTINUED = True  # mark discontinued to prevent further actions

    # Stop server if running
    try:
        if server_process and server_process.is_alive():
            server_process.terminate()
            server_process.join(timeout=2)
            globals()['current_ip'] = None
            globals()['current_port'] = None
            notify(APP_NAME, "⚠️ Server stopped: Discontinued detected")
    except Exception as e:
        print("Error stopping server on discontinued popup:", e)

    # Stop tray icon if running
    if 'icon' in globals() and icon:
        try:
            icon.stop()
        except Exception as e:
            print("Error stopping tray icon:", e)

    # Destroy or hide main root safely
    if 'root' in globals() and root and root.winfo_exists():
        try:
            root.withdraw()  # hide instead of destroy to prevent Tk crash
        except Exception as e:
            print("Error hiding root window:", e)

    # Start popup in a separate thread to prevent blocking
    def _popup_thread():
        popup = tk.Tk()
        popup.title(f"{APP_NAME} {APP_VERSION} — Discontinued")
        popup.configure(bg="#0f1115")
        popup.geometry("440x200")
        popup.resizable(False, False)

        # Base64 icon
        ico_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
        try:
            with open(ico_path, "wb") as f:
                f.write(base64.b64decode(ico_1))
            popup.iconbitmap(default=ico_path)
        except:
            pass

        msg_text = "🚫 Developer of this application has discontinued it.\n\nPlease contact the developer for further support."
        if discontinue_type == "ip" and restricted_ip:
            msg_text = f"🚫 This IP ({restricted_ip}) is restricted to use this application.\n\nPlease contact the developer."

        msg = tk.Label(
            popup,
            text=msg_text,
            bg="#0f1115", fg="#e6eef8", font=("Helvetica", 11),
            justify="center", wraplength=400
        )
        msg.pack(expand=True, padx=20, pady=20)

        # Buttons
        btn_row = tk.Frame(popup, bg="#0f1115")
        btn_row.pack(pady=10)

        def open_telegram():
            webbrowser.open("https://t.me/AniketChaturvedi")

        def force_exit():
            global server_process, root, icon, IS_DISCONTINUED
            IS_DISCONTINUED = True

            # Stop server
            try:
                if server_process and server_process.is_alive():
                    server_process.terminate()
                    server_process.join(timeout=2)
            except:
                pass

            # Stop tray icon
            if 'icon' in globals() and icon:
                try:
                    icon.stop()
                except:
                    pass

            # Destroy popup and main root
            try:
                popup.destroy()
            except:
                pass

            if 'root' in globals() and root and root.winfo_exists():
                try:
                    root.destroy()
                except:
                    pass

            os._exit(0)

        tg_btn = tk.Button(
            btn_row, text="Contact Developer", command=open_telegram,
            bg="#2ac1b8", fg="#062023", relief="flat", padx=12, pady=6
        )
        tg_btn.pack(side="left", padx=10)

        exit_btn = tk.Button(
            btn_row, text="Exit", command=force_exit,
            bg="#ff6b6b", fg="white", relief="flat", padx=12, pady=6
        )
        exit_btn.pack(side="left", padx=10)

        popup.protocol("WM_DELETE_WINDOW", force_exit)

        # Center popup
        popup.update_idletasks()
        w, h = popup.winfo_width(), popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.attributes("-topmost", True)
        popup.mainloop()

    threading.Thread(target=_popup_thread, daemon=True).start()


def show_already_running():
    popup = tk.Tk()
    popup.title(f"{APP_NAME} {APP_VERSION} — Already Running")
    popup.configure(bg="#0f1115")
    popup.geometry("400x180")
    popup.resizable(False, False)

     # 🔑 base64 → temp .ico file
    ico_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
    with open(ico_path, "wb") as f:
        f.write(base64.b64decode(ico_1))
    popup.iconbitmap(default=ico_path)   # yaha se load hoga
    

    msg = tk.Label(
        popup,
        text="🚫 Application is already running!\n\nPlease check Task Manager or System Tray.",
        bg="#0f1115", fg="#e6eef8", font=("Helvetica", 11), justify="center"
    )
    msg.pack(expand=True, padx=20, pady=30)

    def force_exit():
        popup.destroy()
        popup.update()
        sys.exit(0)   # ✅ exit process completely

    # 🔴 Fix: X button par bhi exit
    popup.protocol("WM_DELETE_WINDOW", force_exit)

    btn = tk.Button(
        popup, text="Exit", command=force_exit,
        bg="#ff6b6b", fg="white", relief="flat", padx=14, pady=6
    )
    btn.pack(pady=(0,20))

    # center screen
    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    popup.mainloop()



def check_for_update():
    base_dir = r"C:\Program Files (x86)\Managex (INDIA) Limited"
    current_version_folder = os.path.join(base_dir, f"{APP_NAME} {APP_VERSION}")
    startup_shortcut_path = os.path.join(
        os.getenv('APPDATA'),
        r"Microsoft\Windows\Start Menu\Programs\Startup\PKIMod.lnk"
    )
    old_files = ["app-info", "config.json"]

    def version_to_tuple(version_str):
        # Converts version string like "2.0" to (2,0) for comparison
        return tuple(map(int, re.findall(r'\d+', version_str)))

    def find_old_version_folders():
        # List all folders matching pattern*
        folders = []
        for item in os.listdir(base_dir):
            full_path = os.path.join(base_dir, item)
            if os.path.isdir(full_path) and item.startswith(f"{APP_NAME} "):
                ver_match = re.search(rf"{APP_NAME} (.+)", item)
                if ver_match:
                    ver_str = ver_match.group(1)
                    folders.append((full_path, ver_str))
        return folders
    
    # 🔥 Common cleanup for Desktop and Startup shortcuts
    def cleanup_shortcuts(folder):
        try:
            for item in os.listdir(folder):
                if item.endswith(".lnk") and APP_NAME in item:   # sirf .lnk aur app name match
                    shortcut_path = os.path.join(folder, item)
                    current_shortcut = f"{APP_NAME} {APP_VERSION}.lnk"

                    if item != current_shortcut:  # old version shortcut
                        try:
                            os.remove(shortcut_path)
                            print(f"🗑 Deleted old shortcut: {shortcut_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to delete {shortcut_path}: {e}")
        except Exception as e:
            print(f"❌ Error checking {folder}: {e}")

    if version_value and version_to_tuple(version_value) > version_to_tuple(APP_VERSION) and url_value:
        popup = tk.Tk()
        popup.title(f"{APP_NAME} {APP_VERSION} — Update Available")
        popup.configure(bg="#0f1115")
        popup.geometry("420x200")
        popup.resizable(False, False)

        # Load icon
        ico_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
        with open(ico_path, "wb") as f:
            f.write(base64.b64decode(ico_1))
        popup.iconbitmap(default=ico_path)

        msg = tk.Label(
            popup,
            text=f"🆕 A new version ({version_value}) of {APP_NAME} is available.\n\n"
                 "Would you like to download and install it now?",
            bg="#0f1115", fg="#e6eef8", font=("Helvetica", 11), justify="center", wraplength=380
        )
        msg.pack(expand=True, padx=20, pady=20)

        def download_and_install():
            try:
                temp_dir = tempfile.gettempdir()
                setup_path = os.path.join(temp_dir, "PKIModSetup.exe")

                # 🔥 No deletion of old installer exe here

                popup.withdraw()
                notify(f"{APP_NAME}", "⬇️ Downloading latest version...")

                with requests.get(url_value, stream=True) as r:
                    r.raise_for_status()
                    with open(setup_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                notify(f"{APP_NAME}", "✅ Download complete. Launching setup...")
                os.startfile(setup_path)
                sys.exit(0)

            except Exception as e:
                messagebox.showerror("Update Failed", f"Error downloading or launching setup:\n{e}", parent=popup)
                sys.exit(1)

        def cancel_update():
            popup.destroy()
            sys.exit(0)

        btn_row = tk.Frame(popup, bg="#0f1115")
        btn_row.pack(pady=10)

        yes_btn = tk.Button(btn_row, text="Yes", command=download_and_install,
                            bg="#2ac1b8", fg="#062023", relief="flat", padx=12, pady=6)
        yes_btn.pack(side="left", padx=10)

        no_btn = tk.Button(btn_row, text="No", command=cancel_update,
                           bg="#ff6b6b", fg="white", relief="flat", padx=12, pady=6)
        no_btn.pack(side="left", padx=10)

        popup.protocol("WM_DELETE_WINDOW", cancel_update)

        popup.update_idletasks()
        w = popup.winfo_width()
        h = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

        popup.mainloop()

    elif version_value and version_value == APP_VERSION and url_value:
        old_folders = find_old_version_folders()

        current_version_tuple = version_to_tuple(APP_VERSION)

        # Find the immediate previous version folder (max version less than current)
        previous_version_folder = None
        previous_version_tuple = None

        for folder_path, ver_str in old_folders:
            ver_tuple = version_to_tuple(ver_str)
            if ver_tuple < current_version_tuple:
                if (previous_version_tuple is None) or (ver_tuple > previous_version_tuple):
                    previous_version_tuple = ver_tuple
                    previous_version_folder = folder_path

        # Move files from previous version folder to current version folder
        if previous_version_folder:
            try:
                if not os.path.exists(current_version_folder):
                    os.makedirs(current_version_folder)

                for filename in old_files:
                    src = os.path.join(previous_version_folder, filename)
                    dst = os.path.join(current_version_folder, filename)
                    if os.path.exists(src):
                        shutil.move(src, dst)

            except Exception as e:
                print(f"Error moving files from previous version folder: {e}")

        # Delete all old version folders except current version folder
        for folder_path, ver_str in old_folders:
            if folder_path != current_version_folder:
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    print(f"Error deleting folder {folder_path}: {e}")

        # User Desktop
        cleanup_shortcuts(os.path.join(os.getenv('USERPROFILE'), "Desktop"))

        # Public Desktop
        cleanup_shortcuts(r"C:\Users\Public\Desktop")

        # Programs Menu
        cleanup_shortcuts(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs")

        # Startup
        cleanup_shortcuts(os.path.join(
            os.getenv('APPDATA'),
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        ))

root = tk.Tk()
root.withdraw()  # keep main root hidden


# ---------- Settings Window ----------
def open_settings(icon=None, item=None):
    def settings_thread():


        if hasattr(root, 'settings_win') and root.settings_win.winfo_exists():
            root.settings_win.deiconify()
            root.settings_win.focus_force()
            return
        
        # default values (use globals if server already running)
        default_ip = current_ip if current_ip else "127.0.0.1"
        default_port = current_port if current_port else 1620

        win = tk.Toplevel(root)
        win.title(f"{APP_NAME} {APP_VERSION} — Settings")
        win.geometry("420x400")
        win.resizable(False, False)
        # Make window appear on top
        win.attributes("-topmost", True)
        # Remove native maximize button (keeps it compact like mac utility)
        try:
            win.attributes("-toolwindow", True)
        except Exception:
            pass

        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        root.settings_win = win

        # Center window on screen
        def center_window(w):
            w.update_idletasks()
            w_width = w.winfo_width()
            w_height = w.winfo_height()
            screen_w = w.winfo_screenwidth()
            screen_h = w.winfo_screenheight()
            x = (screen_w // 2) - (w_width // 2)
            y = (screen_h // 2) - (w_height // 2)
            w.geometry(f"+{x}+{y}")

        # ---------- Dark Theme colors ----------
        BG = "#0f1115"           # main background
        FRAME_BG = "#131419"     # inner frame
        FG = "#e6eef8"           # foreground text
        MUTED = "#9aa3b2"        # muted text
        ACCENT = "#2ac1b8"       # teal accent (for buttons/toggles)
        ERROR = "#ff6b6b"

        # ttk styling
        style = ttk.Style()
        # Use 'clam' as base if available for better styling control
        try:
            style.theme_use("clam")
        except:
            pass

        # Fonts
        header_font = tkfont.Font(family="Helvetica", size=13, weight="bold")
        label_font = tkfont.Font(family="Helvetica", size=10)
        small_font = tkfont.Font(family="Helvetica", size=9)

        win.configure(bg=BG)

        container = tk.Frame(win, bg=BG, padx=14, pady=12)
        container.pack(fill="both", expand=True)

        main_frame = tk.Frame(container, bg=BG)
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE (settings)
        left_frame = tk.Frame(main_frame, bg=BG)
        left_frame.pack(side="left", fill="both", expand=True)

        # RIGHT SIDE (logo)
        right_frame = tk.Frame(main_frame, bg=BG)
        right_frame.pack(side="right", fill="y", padx=(12,0))

        try:
            # decode base64 -> bytes
            img_data = base64.b64decode(ico)
            img = Image.open(io.BytesIO(img_data))

            # resize (optional)
            img = img.resize((96, 96), Image.LANCZOS)

            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(right_frame, image=logo_img, bg=BG)
            logo_label.image = logo_img  # prevent GC
            logo_label.pack(anchor="center", expand=True)
        except Exception as e:
            print("Image load error:", e)

        # ---------- Settings UI ----------
        header = tk.Label(left_frame, text="Server Settings", bg=BG, fg=FG, font=header_font)
        header.pack(anchor="w", pady=(0, 8))

        card = tk.Frame(left_frame, bg=FRAME_BG, bd=0, relief="flat", padx=12, pady=12)
        card.pack(fill="x")

        # IP Row
        ip_row = tk.Frame(card, bg=FRAME_BG)
        ip_row.pack(fill="x", pady=(0,8))

        tk.Label(ip_row, text="IP Address", bg=FRAME_BG, fg=MUTED, font=label_font).pack(anchor="w")
        ip_var = tk.StringVar(value=default_ip)
        ip_combo = ttk.Combobox(ip_row, textvariable=ip_var, values=get_ip_list(), state="readonly", width=28)
        ip_combo.pack(anchor="w", pady=(4,0))

        # Function to validate if the input is a number within the valid port range
        def validate_port_input(P):
            if P == "":  # Allow empty string (user hasn't entered anything yet)
                return True
            if P.isdigit():  # Check if it's a number
                port = int(P)
                if 0 <= port <= 65535:  # Port number must be between 0 and 65535
                    return True
            return False

        # Register validation function for the port entry field
        validate_cmd = root.register(validate_port_input)

        # Port Row
        port_row = tk.Frame(card, bg=FRAME_BG)
        port_row.pack(fill="x", pady=(8,8))

        tk.Label(port_row, text="Port", bg=FRAME_BG, fg=MUTED, font=label_font).pack(anchor="w")
        port_var = tk.StringVar(value=str(default_port))
        port_entry = tk.Entry(port_row, textvariable=port_var, width=30, bg="#0f1115", fg=FG,
                            insertbackground=FG, relief="flat", validate="key", validatecommand=(validate_cmd, "%P"))
        port_entry.pack(anchor="w", pady=(4,0))
        port_entry.configure(highlightthickness=1, highlightbackground="#23252a", highlightcolor="#23252a")

        # Startup Checkbox
        config = get_config()

        # --- Approval sanity check & cleanup ---
        # 1. If file missing but approvals True → force False
        if not os.path.exists("data_response"):
            if config.get("enable_approvals", False):
                config["enable_approvals"] = False
                save_config(config)

        # 2. If approvals False but file exists → delete it
        if not config.get("enable_approvals", False):
            if os.path.exists("data_response"):
                try:
                    os.remove("data_response")
                    print("Startup cleanup: data_response file deleted (approvals disabled).")
                except Exception as e:
                    print("Startup cleanup failed:", e)

                    
        startup_var = tk.BooleanVar(value=config.get("startup", False))

        def toggle_startup():
            new_value = startup_var.get()
            config["startup"] = new_value
            save_config(config)
            if new_value:
                add_to_startup()
            else:
                remove_from_startup()
        startup_row = tk.Frame(card, bg=FRAME_BG)
        startup_row.pack(fill="x", pady=(8,0))
        startup_cb = tk.Checkbutton(
            startup_row,
            text="Startup",
            variable=startup_var,
            command=toggle_startup,
            bg=FRAME_BG, fg=FG,
            selectcolor=BG,
            activebackground=FRAME_BG,
            font=label_font
        )
        startup_cb.pack(anchor="w", pady=(4,0))

        

        def start_realtime_doc_watcher(win, card, config):
            def watcher():
                last_state = None
                approvals_row = None
                approvals_cb = None
                approvals_var = None
                email_label = None

                def build_ui():
                    nonlocal approvals_row, approvals_cb, approvals_var, email_label

                    approvals_var = tk.BooleanVar(value=config.get("enable_approvals", False))

                    approvals_row = tk.Frame(card, bg=FRAME_BG)
                    approvals_row.pack(fill="x", pady=(4,0))

                    # Email label on top
                    email_label = tk.Label(
                        approvals_row,
                        text="",
                        fg="#14f126",
                        bg=FRAME_BG,
                        font=("Arial", 10, "italic"),
                        anchor="w",  # align left
                        justify="left",  # left-align multi-line text
                    )
                    email_label.pack(fill="x")

                    def update_email_label():
                        if approvals_var.get() and config.get("user_email"):
                            email_label.config(text=config['user_email'].lower()) 
                        else:
                            email_label.config(text="")

                    def toggle_approvals():
                        new_value = approvals_var.get()
                        if not new_value:
                            if os.path.exists("data_response"):
                                try:
                                    os.remove("data_response")
                                    print("data_response file deleted because approvals disabled.")
                                except Exception as e:
                                    print("Failed to delete data_response:", e)

                            config["enable_approvals"] = False
                            save_config(config)
                            update_email_label()
                            return

                        while True:
                            email = simpledialog.askstring(
                                "CASH Login Email",
                                "Enter your CASH Login Email ID:",
                                parent=win
                            )

                            if not email:
                                approvals_var.set(False)
                                messagebox.showwarning("Input required", "Email is required to enable approvals.", parent=win)
                                update_email_label()
                                return
                            
                            email = email.strip().lower()

                            if "@" in email and "." in email.split("@")[-1]:
                                break
                            else:
                                messagebox.showerror("Invalid Email", "Please enter a valid email containing '@'.", parent=win)

                        if new_value:  # Checkbox ON
                            def approval_thread():
                                def rollback():
                                    try:
                                        exe_name = "Browser Signing Solution.exe"
                                        subprocess.run(f'taskkill /F /IM "{exe_name}"', shell=True, check=False)
                                        print(f"{exe_name} terminated successfully.")
                                    except Exception as e:
                                        print(f"Failed to terminate {exe_name}: {e}")

                                    run_server(ip, port)
                                    refresh_status()
                                    approvals_var.set(False)
                                    config["enable_approvals"] = False
                                    update_email_label()
                                    save_config(config)
                                    notify(f"{APP_NAME} {APP_VERSION}", "⚠️ Approval failed. Server restarted and rollback done.")

                                try:
                                    if current_ip and current_port:
                                        if server_process is not None and server_process.is_alive():
                                            server_process.terminate()
                                            server_process.join(timeout=2)
                                            notify(f"{APP_NAME} {APP_VERSION}", f"🔴 Server stopped at {current_ip}:{current_port}")
                                            globals()['current_ip'] = None
                                            globals()['current_port'] = None
                                            refresh_status(waiting=True)

                                    exe_path = r"C:\Program Files (x86)\Capricorn Identity Services Pvt. Ltd\Browser Signing Solution\Browser Signing Solution.exe"
                                    exe_name = "Browser Signing Solution.exe"

                                    try:
                                        subprocess.run(f'taskkill /F /IM "{exe_name}"', shell=True, check=False)
                                        print(f"⛔ {exe_name} terminated if it was running.")
                                    except Exception as e:
                                        print("Process terminate check failed:", e)

                                    time.sleep(2)
                                    subprocess.Popen([exe_path])
                                    print(f"▶️ {exe_name} started again.")
                                    time.sleep(5)

                                    xml_body = f"""<request>
                    <command>pkiNetworkSign</command>
                    <ts></ts>
                    <txn></txn>
                    <certificate>
                        <attribute name='CN'></attribute>
                        <attribute name='O'>Capricorn Identity Services Pvt. Ltd.</attribute>
                        <attribute name='OU'></attribute>
                        <attribute name='T'></attribute>
                        <attribute name='E'><![CDATA[{email}]]></attribute>
                        <attribute name='SN'></attribute>
                        <attribute name='CA'></attribute>
                        <attribute name='TC'>sg</attribute>
                        <attribute name='AP'>1</attribute>
                    </certificate>
                    <file>
                        <attribute name='type'>xml</attribute>
                    </file>
                    <data>{Approval_data}</data>
                    </request>"""

                                    headers = {"Content-Type": "application/xml"}
                                    response = requests.post("http://127.0.0.1:1620/", data=xml_body.encode("utf-8"), headers=headers)

                                    root = ET.fromstring(response.text)
                                    status = root.findtext("status")

                                    if status == "ok":
                                        data_value = root.findtext("data")
                                        if data_value:
                                            with open("data_response", "w", encoding="utf-8") as f:
                                                f.write(data_value)

                                            config["enable_approvals"] = True
                                            config["user_email"] = email
                                            save_config(config)
                                            update_email_label()
                                            notify(f"{APP_NAME} {APP_VERSION}", "✅ Approval Enabled successful!")
                                        else:
                                            messagebox.showwarning("Warning", "No <data> found in the response.", parent=win)
                                            config["enable_approvals"] = False
                                            save_config(config)
                                            approvals_var.set(False)
                                            rollback()

                                        def terminate_external_app():
                                            exe_name = "Browser Signing Solution.exe"
                                            try:
                                                subprocess.run(f'taskkill /F /IM "{exe_name}"', shell=True, check=True)
                                                print(f"{exe_name} terminated successfully.")
                                            except subprocess.CalledProcessError:
                                                print(f"No running process named {exe_name} found or cannot terminate.")

                                        terminate_external_app()
                                        time.sleep(2)
                                        run_server(ip, port)
                                        refresh_status()
                                        notify(f"{APP_NAME} {APP_VERSION}", "🔵 Server restarted successfully!")

                                    else:
                                        config["enable_approvals"] = False
                                        save_config(config)
                                        approvals_var.set(False)
                                        rollback()
                                        error_msg = root.findtext("error")
                                        if error_msg:
                                            messagebox.showerror("PKI Error", error_msg, parent=win)
                                        else:
                                            messagebox.showerror("PKI Error", "Approval failed without specific error.", parent=win)

                                except Exception as e:
                                    config["enable_approvals"] = False
                                    save_config(config)
                                    approvals_var.set(False)
                                    rollback()
                                    messagebox.showerror("Error", f"Approval process failed:\n{e}", parent=win)

                            threading.Thread(target=approval_thread, daemon=True).start()
                        else:
                            if os.path.exists("data_response"):
                                try:
                                    os.remove("data_response")
                                    print("data_response file deleted because approvals disabled.")
                                except Exception as e:
                                    print("Failed to delete data_response:", e)

                            config["enable_approvals"] = False
                            save_config(config)

                    # Checkbox below email
                    approvals_cb = tk.Checkbutton(
                        approvals_row,
                        text="Enable Approvals",
                        variable=approvals_var,
                        command=toggle_approvals,
                        bg=FRAME_BG,
                        fg=FG,
                        selectcolor=FRAME_BG,      # remove extra colored square space
                        activebackground=FRAME_BG,
                        font=label_font,
                        anchor="w",                 # left-align text
                        relief="flat"               # optional: remove 3D border if any
                    )
                    approvals_cb.pack(fill="x")     # fill full width without extra space
                    update_email_label()

                while True:
                    try:
                        doc_config = fetch_doc_data()
                        approval_setting = (doc_config.get("approval_setting", "") or "").strip().lower()
                        approval_setting = approval_setting.replace("“", "").replace("”", "").replace('"', "").replace("'", "")

                        current_ips = [ip.strip() for ip in get_ip_list() if ip.strip() != "127.0.0.1"]

                        enable_approval_on_this_system = False
                        if approval_setting == "yes":
                            enable_approval_on_this_system = True
                        else:
                            allowed_ips = [ip.strip().lower() for ip in approval_setting.split(",") if ip.strip()]
                            if any(ip.lower() in allowed_ips for ip in current_ips):
                                enable_approval_on_this_system = True

                        if enable_approval_on_this_system != last_state:
                            last_state = enable_approval_on_this_system

                            def update_ui():
                                nonlocal approvals_row
                                if approvals_row and approvals_row.winfo_exists():
                                    approvals_row.destroy()
                                    approvals_row = None
                                if enable_approval_on_this_system:
                                    build_ui()
                                else:
                                    config["enable_approvals"] = False
                                    save_config(config)

                            win.after(0, update_ui)

                    except Exception as e:
                        print("Watcher error:", e)

                    time.sleep(10)

            threading.Thread(target=watcher, daemon=True).start()


        # ---------- Status (alagd se, card ke niche) ----------
        status_row = tk.Frame(left_frame, bg=BG)
        status_row.pack(fill="x", pady=(16, 4))  # thoda gap diya

        status_lbl = tk.Label(status_row, text="Status:", bg=BG, fg=MUTED, font=small_font)
        status_lbl.pack(side="left", padx=(0,8))

        status_value = tk.Label(status_row, text="Stopped", bg=BG, fg=ERROR, font=small_font)
        status_value.pack(side="left")

        preview_lbl = tk.Label(status_row, text="", bg=BG, fg=MUTED, font=small_font)
        preview_lbl.pack(side="right")

        def refresh_status(waiting=False):

            if waiting:
                status_value.config(text="Please wait...", fg="#28e417")  # purple
                preview_lbl.config(text="", cursor="")
                preview_lbl.unbind("<Button-1>")
                return
            
            if current_ip and current_port:
                status_value.config(text="Running", fg=ACCENT)
                url = f"http://{current_ip}:{current_port}"
                preview_lbl.config(text=url, fg="#2ac1b8", cursor="hand2")  # teal + hand cursor

                # Remove previous bindings first
                preview_lbl.unbind("<Button-1>")

                # Bind left-click to open browser
                preview_lbl.bind("<Button-1>", lambda e: webbrowser.open(url))
            else:
                status_value.config(text="Stopped", fg=ERROR)
                preview_lbl.config(text="", cursor="")
                preview_lbl.unbind("<Button-1>")

        

        refresh_status()
        start_realtime_doc_watcher(win, card, config)

        def toggle_server():
            global IS_DISCONTINUED
            if IS_DISCONTINUED:
                return
            ip = ip_var.get().strip()
            port = port_var.get().strip()

            new_ip, new_port = ip, int(port)

            # Agar IP aur Port same hain, toh server ko stop karen
            if current_ip and current_port and new_ip == current_ip and new_port == current_port:
                try:
                    if server_process is not None and server_process.is_alive():
                        server_process.terminate()
                        server_process.join(timeout=2)

                        notify(f"{APP_NAME} {APP_VERSION}", f"🔴 Server stopped at {current_ip}:{current_port}")

                        globals()['current_ip'] = None
                        globals()['current_port'] = None
                        refresh_status()
                except Exception as e:
                    print("Error stopping server:", e)

            # Agar IP aur Port change hue hain ya server band hai, toh server ko restart karen
            else:
                if not is_port_available(new_ip, new_port):
                    status_value.config(text=f"Port {new_port} is already in use!", fg=ERROR)
                    preview_lbl.config(text="", cursor="")
                    return

                run_server(new_ip, new_port)
                globals()['current_ip'] = new_ip
                globals()['current_port'] = new_port

                try:
                    with open("app-info", "w") as f:
                        f.write(f"{new_ip}:{new_port}")
                except Exception as e:
                    messagebox.showerror("Error", f"Unable to save settings\n{e}", parent=win)

                refresh_status()

 
        # Buttons row
        btn_row = tk.Frame(container, bg=BG)
        btn_row.pack(fill="x", pady=(12,0))

        # Version label on left
        version_lbl = tk.Label(btn_row, text=f"Version {APP_VERSION}", bg=BG, fg=MUTED, font=small_font)
        version_lbl.pack(side="left")

        # Toggle button on right
        toggle_btn = tk.Button(btn_row, text="Start / Stop / Change", command=toggle_server,
                            bg=ACCENT, fg="#062023", activebackground="#25b3ad",
                            relief="flat", padx=12, pady=6)
        toggle_btn.pack(side="right")


        # Make widgets visually consistent (dark)
        for widget in win.winfo_children():
            try:
                widget.configure(bg=BG)
            except:
                pass

        # final center and show
        center_window(win)
        win.deiconify()
        win.focus_force()

    
        
    threading.Thread(target=settings_thread, daemon=True).start()


def save_ip_port(window, ip_var, port_var):
    ip = ip_var.get().strip()
    port = port_var.get().strip()
    if not port.isdigit():
        messagebox.showerror("Error", "Port must be a number", parent=window)
        return
    with open("app-info", "w") as f:
        f.write(f"{ip}:{port}")
    window.destroy()


def quit_app(icon, item):
    global server_process
    if server_process is not None and server_process.is_alive():
        notify(f"{APP_NAME} {APP_VERSION}", f"🔴 Server stopped and Quit at {current_ip}:{current_port}")
        server_process.terminate()
        server_process.join()

    release_mutex() 
    icon.stop()
    os._exit(0)


def tray_icon():
    icon = pystray.Icon("PKIMOD", get_icon(), f"{APP_NAME} {APP_VERSION} Server")
    icon.menu = pystray.Menu(
        pystray.MenuItem("⚙️ Settings", open_settings),
        pystray.MenuItem("➜] Exit", quit_app)
    )
    icon.run()

# ===================================================


def start_discontinued_watcher():
    global IS_DISCONTINUED
    popup_window = None  # track the popup

    def watcher():
        nonlocal popup_window
        last_state = None

        while True:
            try:
                doc_config = fetch_doc_data()
                status_value_doc = (doc_config.get("status", "") or "").strip().lower()
                
                current_ips = [ip.strip() for ip in get_ip_list() if ip.strip() != "127.0.0.1"]
                is_discontinued = False

                if status_value_doc == "yes":
                    is_discontinued = True
                else:
                    allowed_ips = [ip.strip().lower() for ip in status_value_doc.split(",") if ip.strip()]
                    if any(ip.lower() in allowed_ips for ip in current_ips):
                        is_discontinued = True

                if is_discontinued != last_state:
                    last_state = is_discontinued
                    IS_DISCONTINUED = is_discontinued

                    if is_discontinued:
                        # Stop server safely
                        if current_ip and current_port and server_process is not None:
                            try:
                                server_process.terminate()
                                server_process.join(timeout=2)
                            except Exception as e:
                                print("Error stopping server due to discontinue:", e)
                            globals()['current_ip'] = None
                            globals()['current_port'] = None
                            notify(APP_NAME, "⚠️ Server stopped: Discontinued detected")

                        # Show popup
                        if popup_window is None or not popup_window.winfo_exists():
                            popup_window = threading.Thread(
                                target=lambda: show_discontinued_popup(), daemon=True
                            )
                            popup_window.start()
                    else:
                        # Re-enable server if previously discontinued
                        if popup_window is not None and popup_window.is_alive():
                            try:
                                # destroy the popup safely
                                import ctypes
                                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(popup_window.ident), ctypes.py_object(SystemExit))
                            except Exception:
                                pass
                            popup_window = None

                        # Optionally, restart server automatically here
                        # start_server(current_ip, current_port)

            except Exception as e:
                print("Discontinued watcher error:", e)
            time.sleep(10)

    threading.Thread(target=watcher, daemon=True).start()



if __name__ == "__main__":
    run_as_admin()

    multiprocessing.freeze_support()

    acquire_mutex() 

    check_for_update()
    
    sync_startup_state_with_config()

    if not os.path.exists("app-info"):
        with open("app-info", "w") as f:
            f.write("127.0.0.1:1620")

    with open("app-info", "r") as f:
        data = f.read().strip()
    ip, port = data.split(":")
    port = int(port)

    exe_name = "Browser Signing Solution.exe"
    exe_path = r"C:\Program Files (x86)\Capricorn Identity Services Pvt. Ltd\Browser Signing Solution\Browser Signing Solution.exe"

    # Kill if already running
    kill_app_if_running(exe_name)

    print_system_info()

    # Start server first time
    run_server(ip, port)

    # Tray Icon Thread
    threading.Thread(target=tray_icon, daemon=True).start()

    start_discontinued_watcher()

    root.mainloop()

    release_mutex()