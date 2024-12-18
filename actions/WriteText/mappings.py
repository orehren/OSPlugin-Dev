import evdev

from evdev import ecodes

from loguru import logger as log
import os

import xkbcommon.xkb as xkb  # Corrected import

from typing import List


class KeyMapper:
    def __init__(self):
        self.xkb_context = None
        self.xkb_keymap = None
        self.xkb_state = None
        self._setup_xkb()

    def _setup_xkb(self):
        try:
            self.xkb_context = xkb.Context()
            self.xkb_keymap = self.xkb_context.keymap_new_from_names()
            self.xkb_state = self.xkb_keymap.state_new()
            log.debug("xkbcommon setup successful")
        except Exception as e:
            log.error(f"Failed to setup xkbcommon: {e}")
            self.xkb_context = None
            self.xkb_keymap = None
            self.xkb_state = None
            
    def map_char(self, char: str) -> List[int]:
        if not self.xkb_state or not self.xkb_keymap:
             log.error("xkbcommon is not set up correctly.")
             return []

        keycodes = []
        utf32_char = ord(char)
            
        found_keycodes = []
        for keycode in self.xkb_keymap:
            self.xkb_state.update_mask(keycode, 0,0,0,0)
            symbols = self.xkb_state.key_get_syms(keycode)
            if not symbols:
                 continue
                
            for symbol in symbols:
                if xkb.keysym_to_utf32(symbol) == utf32_char:
                  found_keycodes.append(keycode)
                  break
            
        if not found_keycodes:
            log.warning(f"No keycode found for character: {char} (UTF-32: {utf32_char})")
        
        keycodes.extend(found_keycodes)

        return keycodes
        
        keycodes.extend(found_keycodes)
        return keycodes
