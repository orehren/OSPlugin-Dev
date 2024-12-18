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
            names = self.xkb_context.keymap_new_from_names("evdev", None, "us", None, None)
            if names is None:
              log.error(f"Failed to setup xkbcommon: keymap_new_from_names returned NULL")
              self.xkb_context = None
              self.xkb_keymap = None
              self.xkb_state = None
              return
            keymap_str = xkb.Keymap.get_as_string(names, xkb.KEYMAP_FORMAT_TEXT_V1)
            self.xkb_keymap = self.xkb_context.keymap_from_string(keymap_str, xkb.KEYMAP_FORMAT_TEXT_V1, 1)
            self.xkb_state = xkb.State(self.xkb_keymap)
            self.layout = 0
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
            self.xkb_state.update_mask(keycode, 0,0,0,0, self.layout)
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

