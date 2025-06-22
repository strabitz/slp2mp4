# src/slp2mp4/modes/__init__.py
from slp2mp4.modes import mode
from slp2mp4.modes.single import Single
from slp2mp4.modes.directory import Directory
from slp2mp4.modes.zip import Zip

# Import the new clipping mode
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from slp2mp4.clipper import ClippingMode

MODES = {
    "single": mode.ModeContainer(
        Single,
        "convert single replay files to videos",
        "input file(s)",
    ),
    "directory": mode.ModeContainer(
        directory.Directory,
        "recursively convert all replay files in a directory to videos",
        "input directory/directories",
    ),
    "zip": mode.ModeContainer(
        Zip,
        "recursively convert all replay files in a zip to videos",
        "replay manager zip/directory",
    ),
    "clip": mode.ModeContainer(
        ClippingMode,
        "create clips from videos based on D-pad down markers",
        "video file(s) or slp file(s) with corresponding videos",
    ),
}