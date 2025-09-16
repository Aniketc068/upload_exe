from imports import *


def notify(title, message):
    """Function to send notification"""
    # This function can be customized based on your notification system
    print(f"[{title}] {message}")  # For now, simply print the notification

def is_port_available(port):
    """Check if the specified port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Try to bind to the port
        sock.bind(("0.0.0.0", port))
    except socket.error:
        # If an error occurs, the port is already in use
        return False
    else:
        # Port is available
        return True
    finally:
        sock.close()

def check_port_and_notify(port):
    """Check if the port is available and notify the user if it's not."""
    if not is_port_available(port):
        notify("PKI Mod", f"🔴 Port {port} is already in use by another application.")
        return False
    return True