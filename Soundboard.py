# -- Import -- #
from __future__ import print_function  # Python 2.6+ or 3.0+
import pygame
import argparse
import csv
import tqdm
import os
import sys
import time
# -- End Import -- #


# -- Classes -- #
class sound_clip(object):
    def __init__(self):
        self.path = None
        self.label = None
        self.key = None
        self.type = ''
        self.sound_obj = None

    def play_clip(self):
        if self.type == 'pygame':
            self.sound_obj.play()

    def stop_clip(self):
        pass

    def wait_for_clip(self):
        pass

    def clip_is_playing(self):
        if self.type == 'pygame':
            return pygame.mixer.get_busy()
        pass

class settings(object):
    """ Stores the options to/from a file or from the cli """
    def __init__(self):
        self.gui = False
        self.web = False

    def save_settings(self):
        pass

    def load_settings(self):
        pass
# -- End Classes -- #


# -- Functions -- #
def get_args():
    pass

def import_setting_from_file():
    pass

def init_gui():
    # - Init PyGame
    pygame.init()
    pygame.display.set_mode([300, 200]) # must include a visible display to play audio :-(
    # pygame.display.iconify() # but you can minimize it...
    pygame.mixer.pre_init()
    pygame.mixer.init()
    return

def stop_all_clips():
    pass


# -- End Functions -- #


# -- Main -- #
def main():
    settings = get_args()

    init_gui()

    test = sound_clip()
    test.path = os.path.join(os.getcwd(), "audio", "badumtss1.ogg")
    test.type = 'pygame'
    test.sound_obj = pygame.mixer.Sound(test.path)
    test.play_clip()


    while test.clip_is_playing():
        time.sleep(1)

    # - Get settings from file (if present, else generate dummy and exit)

    # - Check that the files listed exist and warn if missing

    # - If option to keep all files in memory is set, load them

    # - Wait for input
    # - On input, play selected sound until it ends or stop is called
    return
# -- End Main -- #


# -- Run Main -- #
if __name__ == '__main__':
    main()
# -- End Run Main -- #
