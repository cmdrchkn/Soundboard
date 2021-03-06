# -- Import -- #
from __future__ import print_function  # Python 2.6+ or 3.0+

import configparser
import csv
import os
import sys
import time
import itertools
import pygame
import simpleaudio
import tqdm

# Deal with py Version skew
if sys.version[0] == "3":
    raw_input = input


# -- End Import -- #


# -- Classes -- #
class SoundLibrary(object):
    """
    Holds a group of sound objects
    """

    def __init__(self):
        self.sounds = {}
        self.playing = []
        self.type = 'simpleaudio'
        self.gui = False
        self.web = False
        self.keep_in_mem = False
        self.root = os.path.split(sys.argv[0])[0]
        if not os.path.isabs(self.root):
            self.root = os.path.join(os.getcwd(), self.root)

        self.import_settings_from_file()
        self.import_library_from_file()

    def display_choices(self):
        items_per_row = 3

        # Determine what to display
        prompt_text = []
        for key in sorted(self.sounds.keys()):
            clip = self.sounds[key]
            prompt_text.append(key + ': ' + clip.label)

        # Clear the screen
        cls()

        # Print Now Playing info
        stale = []
        for clip in self.playing:
            if clip.clip_is_playing():
                print('Playing:', clip.label)
            else:
                stale.append(clip)

        # Purge the old notices from the list
        for stale_clip in stale:
            self.playing.remove(stale_clip)

        # Figure out how to fit stuff on the screen
        screen_text_lines = get_rows_by_slice(prompt_text, items_per_row)
        # !TODO: Paginate?

        # Do the actual displaying
        for _ in range(0, 119):
            print('-', end='')
        print()
        for row in screen_text_lines:
            format_string = '|{:<38}'
            for _ in row[1:]:
                format_string += '|{:<38}'

            print(format_string.format(*row))

        return

    def process_choice(self, choice, wait=False):
        # Play clips back to back
        if ',' in choice:
            for _ in choice.split(','):
                self.process_choice(_, wait=True)
            return True

        # Play multiple clips (almost) simultaneously
        if '+' in choice:
            for _ in choice.split('+'):
                self.process_choice(_)
            return True

        if choice.lower() in ['q', 'exit']:
            print('Quiting...')
            return False

        if choice.lower() in ['!', 'stop', 'shut the fuck up', 'shut up']:
            print('Stopping all sounds...')
            self.stop_all_sounds()

        elif choice in self.sounds:
            # print('Playing:', self.sounds[choice].label)

            # Play the selection
            self.sounds[choice].play_clip()

            # Note that we're playing it in case we need to stop it explicitly
            self.playing.append(self.sounds[choice])

            # Block until the clip is done playing
            if wait:
                self.sounds[choice].wait_for_clip()

        else:
            print('Unknown Command')

        #time.sleep(0.5)
        return True

    def stop_all_sounds(self):
        if self.type == 'pygame':
            pygame.mixer.stop()
        elif self.type == 'simpleaudio':
            simpleaudio.stop_all()
        return

    def save_library_to_file(self):
        library_file_path = os.path.join(self.root, 'soundboard_library.csv')
        with open(library_file_path, 'w', newline='') as library_file:
            library_csv = csv.writer(library_file, quoting=csv.QUOTE_ALL)
            library_csv.writerow([
                "clip_label",
                "clip_key",
                "clip_path",
            ])

            for clip_key in tqdm.tqdm(self.sounds.keys()):
                library_csv.writerow([
                    self.sounds[clip_key].label,
                    self.sounds[clip_key].key,
                    self.sounds[clip_key].path,
                ])
        return

    def import_library_from_file(self):
        library_file_path = os.path.join(self.root, 'soundboard_library.csv')

        if not os.path.exists(library_file_path):
            self.write_dummy_library_to_file()
            return

        library_file = csv.reader(open(library_file_path, 'r'))

        for _i, row in enumerate(library_file):
            # print('DEBUG', row)
            this_clip = SoundClip(self.type)

            if len(row) == 0 or row[0] == '':
                continue

            try:
                this_clip.label = row[0]
                this_clip.key = row[1]
                this_clip.path = row[2]
                if not os.path.isabs(this_clip.path):
                    this_clip.path = os.path.join(self.root, this_clip.path)
            except:  # !TODO: actual exception handling might be nice...
                print('Failed to read a row in the library: line #', _i, ' was [', row, ']', sep='')

            if this_clip.label == 'clip_label':
                continue

            if this_clip.key not in self.sounds:
                this_clip.import_from_file()
                self.sounds[this_clip.key] = this_clip
            else:
                print('SoundClips cannot share keys. Key ' + this_clip.key + ' will stay assigned to ' +
                      self.sounds[this_clip.key].label + ' and ' + this_clip.label + ' will be ignored.')
        return

    def write_dummy_library_to_file(self):
        self.save_library_to_file()
        return

    def save_settings_to_file(self):
        config_file_path = os.path.join(self.root, 'soundboard_settings.cfg')
        config = configparser.ConfigParser()
        config['Settings'] = {
            'gui':         str(self.gui),
            'web':         str(self.web),
            'type':        str(self.type),
            'keep_in_mem': str(self.keep_in_mem),
        }

        with open(config_file_path, 'w') as config_file:
            config.write(config_file)
        return

    def import_settings_from_file(self):
        settings_file_path = os.path.join(self.root, 'soundboard_settings.cfg')

        if not os.path.exists(settings_file_path):
            self.write_dummy_settings_to_file()
            return

        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            'gui':         "False",
            'web':         "False",
            'type':        "simpleaudio",
            'keep_in_mem': "False",
        }
        config.read(settings_file_path)
        for key in config["Settings"]:
            if config["Settings"][key] == "True":
                setattr(self, key, True)
            elif config["Settings"][key] == "False":
                setattr(self, key, False)
            else:
                setattr(self, key, config["Settings"][key])
        return

    def write_dummy_settings_to_file(self):
        self.save_settings_to_file()
        return


class SoundClip(object):
    """
    Holds the info and objects needed to turn a file into sound.
    Provides a unified interface to use both pygame and simpleaudio

    Note: SoundClip.key must be unique
    """

    def __init__(self, library_type):
        self.label = None
        self.key = None
        self.path = None
        self.type = library_type
        self.sound_obj = None
        self.play_obj = None  # Only needed for simpleaudio
        self.is_loaded = False

    def play_clip(self):
        if not self.is_loaded:
            self.import_from_file()

        if self.type == 'pygame':
            self.sound_obj.play()
            return
        elif self.type == 'simpleaudio':
            self.play_obj = self.sound_obj.play()
            return
        else:
            return None

    def stop_clip(self):
        if self.type == 'pygame':
            return self.sound_obj.stop()
        elif self.type == 'simpleaudio':
            return self.play_obj.stop()
        else:
            return None

    def import_from_file(self):
        if self.type == 'pygame':
            self.sound_obj = pygame.mixer.Sound(self.path)
            self.is_loaded = True
        elif self.type == 'simpleaudio':
            self.sound_obj = simpleaudio.WaveObject.from_wave_file(self.path)
            self.is_loaded = True
        else:
            return None

    def wait_for_clip(self):
        while self.clip_is_playing():
            time.sleep(0.1)

    def clip_is_playing(self):
        if self.type == 'pygame':
            return pygame.mixer.get_busy()
        elif self.type == 'simpleaudio':
            return self.play_obj.is_playing()
        else:
            return None


# -- End Classes -- #


# -- Functions -- #
def get_args():
    # !TODO: Implement literally any argument handling at all
    return SoundLibrary()


def init_gui():
    # - Init PyGame
    pygame.init()
    pygame.display.set_mode([300, 200])  # must include a visible display to play audio :-(
    # pygame.display.iconify()  # but you can minimize it...
    pygame.mixer.pre_init()
    pygame.mixer.init()
    return


def cls():
    """
    Ugly but function method for clearing the screen on both Linux and Windows
    http://stackoverflow.com/a/684344
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    return


def get_rows_by_slice(seq, row_length):
    # http://stackoverflow.com/a/3744524
    for start in range(0, len(seq), row_length):
        yield seq[start:start+row_length]


# -- End Functions -- #


# -- Main -- #
def main():
    # - Get settings from file (if present, else generate dummy and exit)
    library = get_args()
    library.type = 'simpleaudio'  # !TODO: get this from settings_file

    # - If option to use gui is set, init pygame
    if library.gui:
        init_gui()

    # - If option to keep all files in memory is set, load them
    if library.keep_in_mem:
        # !TODO: Not sure this is needed unless we end up with a crap-ton of clips
        pass

    # - Check that the files listed exist and warn if missing

    # - Wait for input
    keep_running = True
    while keep_running:
        library.display_choices()
        # !TODO: Process KeyInput directly
        keep_running = library.process_choice(raw_input("\tSoundboard> "))

    return


# -- End Main -- #


# -- Run Main -- #
if __name__ == '__main__':
    main()
# -- End Run Main -- #
