import os


# Define possible message box return values
messagebox_returns = {
    1: "IDOK (OK button pressed)",
    2: "IDCANCEL (Cancel button pressed)",
    3: "IDABORT (Abort button pressed)",
    4: "IDRETRY (Retry button pressed)",
    5: "IDIGNORE (Ignore button pressed)",
    6: "IDYES (Yes button pressed)",
    7: "IDNO (No button pressed)",
    10: "IDTRYAGAIN (Try Again button pressed)",
    11: "IDCONTINUE (Continue button pressed)"
}

# Define possible icons
icon_map = {
    "ICON_HAND": "error",
    "ICON_QUESTION": "question",
    "ICON_EXCLAMATION": "warning",
    "ICON_ASTERISK": "info",
}

def detect_headless():
    """Detects if running in a headless environment like CI/CD or GitHub Actions."""
    headless_env_vars = ["SSH_CONNECTION", "SSH_CLIENT", "DISPLAY", "WAYLAND_DISPLAY", "GITHUB_ACTIONS", "CI"]
    return any(var in os.environ for var in headless_env_vars) or os.environ.get("TERM") == "dumb"

def get_safest_option(buttons):
    """Returns the safest option in headless mode."""
    safe_defaults = {
        "OK": 1,
        "OK_CANCEL": 2,  # Cancel is safer than OK
        "YES_NO": 7,  # No is safer than Yes
        "YES_NO_CANCEL": 2,  # Cancel is safest
        "RETRY_CANCEL": 2,  # Cancel is safer than Retry
        "ABORT_RETRY_IGNORE": 5,  # Ignore is the least destructive
        "CANCEL_TRY_CONTINUE": 2  # Cancel is safest
    }
    return safe_defaults.get(buttons, 1)  # Default to OK

def show_messagebox(parsed_data):
    """Displays a message box or console prompt based on availability and environment."""
    lpText = parsed_data["arguments"]["lpText"]["value"]
    lpCaption = parsed_data["arguments"]["lpCaption"]["value"]
    uType = parsed_data["arguments"]["uType"]["parsed"]

    buttons = uType["buttons"]
    icon = icon_map.get(uType["icon"], "info")
   
    if buttons in ["ABORT_RETRY_IGNORE", "CANCEL_TRY_CONTINUE"]:
        TK_AVAILABLE = False  # Force console mode for these button types
    
    # Try to import tkinter, fallback to console mode if unavailable
    try:
        import tkinter as tk
        from tkinter import messagebox
        TK_AVAILABLE = True
    except ImportError:
        TK_AVAILABLE = False

    if TK_AVAILABLE and not detect_headless():
        try:
            root = tk.Tk()
            root.withdraw()
            result = None

            if buttons == "OK":
                messagebox.showinfo(lpCaption, lpText, icon=icon)
                result = 1  # IDOK
            elif buttons == "OK_CANCEL":
                result = 1 if messagebox.askokcancel(lpCaption, lpText, icon=icon) else 2  # IDOK or IDCANCEL
            elif buttons == "YES_NO":
                result = 6 if messagebox.askyesno(lpCaption, lpText, icon=icon) else 7  # IDYES or IDNO
            elif buttons == "YES_NO_CANCEL":
                choice = messagebox.askyesnocancel(lpCaption, lpText, icon=icon)
                result = {True: 6, False: 7, None: 2}[choice]  # IDYES, IDNO, or IDCANCEL
            elif buttons == "RETRY_CANCEL":
                result = 4 if messagebox.askretrycancel(lpCaption, lpText, icon=icon) else 2  # IDRETRY or IDCANCEL
            
            root.destroy()
            return result
        except Exception as e:
            print(f"Failed to create message box: {e}")

    # Fallback to console mode
    print(f"\n[{lpCaption}]\n{lpText}\n")

    # If running in a headless environment, return the safest option
    if detect_headless():
        safe_option = get_safest_option(buttons)
        print(f"[Console Mode] Running in headless mode. Defaulting to: {messagebox_returns[safe_option]}")
        return safe_option

    # Map console input buttons
    button_options = {
        "OK": [1],
        "OK_CANCEL": [1, 2],
        "YES_NO": [6, 7],
        "YES_NO_CANCEL": [6, 7, 2],
        "RETRY_CANCEL": [4, 2],
        "ABORT_RETRY_IGNORE": [3, 4, 5],
        "CANCEL_TRY_CONTINUE": [2, 10, 11]
    }

    options = button_options.get(buttons, [1])
    options_str = " ".join(f"{opt}: [{messagebox_returns[opt].split(' ')[0]}]" for opt in options)

    while True:
        try:
            user_input = int(input(f"\nChoose an option: {options_str}\n> "))
            if user_input in options:
                return user_input
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a valid number.")

import tkinter as tk
from tkinter import messagebox

def show_message(title="Message", message="Hello, world!", msg_type="info"):
    """Displays a message box with the specified type."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    if msg_type.lower() == "error":
        messagebox.showerror(title, message)
    elif msg_type.lower() == "warning":
        messagebox.showwarning(title, message)
    else:  # Default to "info"
        messagebox.showinfo(title, message)
    
    root.destroy()  # Destroy the root window after message is shown