# Logic for dolphin INIs
# https://github.com/dolphin-emu/fifoci/

# TODO: Disable "waiting for game" screen
# TODO: Graphics enhancements
# TODO: More config options

import configparser
import contextlib
import pathlib


@contextlib.contextmanager
def make_ini_file(filename: pathlib.Path, contents: dict):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as ini_file:
        ini_parser = configparser.ConfigParser(
            allow_no_value=True, delimiters=("=",), strict=False
        )
        for section, options in contents.items():
            ini_parser.add_section(section)
            for opt_name, opt_val in options.items():
                ini_parser.set(section, opt_name, opt_val)
        ini_parser.write(ini_file)
        ini_file.flush()
        yield filename, ini_file


@contextlib.contextmanager
def make_dolphin_file(userdir: pathlib.Path):
    settings = {
        # Disables rumble, since it's annoying when rendering replays
        "Core": {
            "AdapterRumble0": "False",
            "AdapterRumble1": "False",
            "AdapterRumble2": "False",
            "AdapterRumble3": "False",
        },
        # Enables dumping frames
        "Movie": {
            "DumpFrames": "True",
            "DumpFramesSlient": "True",
        },
        # Enables dumping audio
        "DSP": {
            "DumpAudio": "True",
            "DumpAudioSilent": "True",
            "Backend": "ALSA",
        },
    }
    filename = userdir.joinpath("Config", "Dolphin.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name


@contextlib.contextmanager
def make_gfx_file(userdir: pathlib.Path):
    # Could use Settings.DumpFramesAsImages, then detect all-black images
    settings = {
        "Settings": {
            "LogRenderTimeToFile": "True",  # Used to monitor render progress
        },
    }
    filename = userdir.joinpath("Config", "GFX.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name
