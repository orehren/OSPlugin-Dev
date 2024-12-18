from .mappings import KeyMapper

from evdev import InputDevice, UInput, list_devices
from evdev import ecodes as e

from loguru import logger as log
import time

def check_caps_lock() -> bool:
    """Returns True if Caps Lock is on, False if it is off, and False if it cannot be determined."""
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if device.capabilities().get(e.EV_LED):
            return e.LED_CAPSL in device.leds()
    return False

def keyboard_write(ui: UInput, text: str, delay: float = 0.01):
    key_mapper = KeyMapper()
    caps_lock_is_on = check_caps_lock()
    for char in text:
        is_unicode = False
        unicode_bytes = char.encode("unicode_escape")
        # '\u' or '\U' for unicode, or '\x' for UTF-8
        if unicode_bytes[0] == 92 and unicode_bytes[1] in [85, 117, 120]:
            is_unicode = True

        keycodes = key_mapper.map_char(char)

        if not keycodes:
            log.warning(f"Unsupported character: {char}")
            continue
        
        for keycode in keycodes:
            need_shift = False
            
            if char.isalpha() and caps_lock_is_on:
                
                
                if char.isupper():
                    need_shift = False
                else:
                    need_shift = True
                    
            if need_shift:
                ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)

            ui.write(e.EV_KEY, keycode, 1)
            ui.write(e.EV_KEY, keycode, 0)

            if need_shift:
                ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
        
        # send keys
        ui.syn()
        time.sleep(delay)

def parse_key_combination(key_combination: str) -> list[int]:
    key_mapper = KeyMapper()
    keys = key_combination.lower().split('+')
    parsed_keys = []
    for key in keys:
        keycodes = key_mapper.map_char(key)
        if keycodes:
            parsed_keys.extend(keycodes)
        
        else:
            log.error(f"Unsupported key: {key}")
            # raise ValueError(f"Unsupported key: {key}")
    return parsed_keys

# Function to press and release keys
def press_key_combination(ui: UInput, key_combination: str, delay: float = 0.01):
    keycodes = parse_key_combination(key_combination)
    
    # Press each key in the combination
    for keycode in keycodes:
        ui.write(e.EV_KEY, keycode, 1)  # Key down
    ui.syn()
    
    # Short delay between press and release
    time.sleep(delay)
    
    # Release each key in the combination
    for keycode in keycodes:
        ui.write(e.EV_KEY, keycode, 0)  # Key up
    ui.syn()
