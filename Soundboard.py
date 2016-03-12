# -- Import -- #
import argparse
import csv
import pygame
import tqdm
import os
import sys
import time
# -- End Import -- #


# -- Classes -- #
class sound_byte(object):
    def __init__(self):
        self.path = None
        self.label = None
        self.key = None

    def play_clip(self):
        pass
# -- End Classes -- #


# -- Functions -- #
def get_args():
    pass

def import_setting_from_file():
    pass

def save_settings_to_file(settings):
    if not settings:
        pass
    pass

def stop_all_clips():
    pass
# -- End Functions -- #


# -- Main -- #
def main():

    # - Init PyGame
    pygame.init()
    pygame.display.set_mode([300, 200])
    # pygame.display.iconify()
    pygame.mixer.pre_init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    test = pygame.mixer.Sound(os.path.join(os.getcwd(), "audio", "badumtss1.ogg"))
    test.play()
    clock.tick(10)

    while pygame.mixer.get_busy():
        pygame.event.poll()
        clock.tick(10)

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
