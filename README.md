# `slp2mp4`

Convert Slippi replay files (`.slp`) to video files (`.mp4`) with ease.

## Features

- Multiple conversion modes:
    - Single file conversion
    - Directory batch conversion (recursive)
    - Replay Manager zip file support
- Parallel processing for faster batch conversions
- GUI for easy configuration and operation
- Customizable output resolution and bitrate
- Cross-platform support for Windows, Linux
    - Dolphin on Mac does not support framedumping

## Requirements

- Python 3.11 or higher
- [FFmpeg](https://ffmpeg.org/) installed and accessible
- [Slippi Dolphin](https://slippi.gg/downloads) installed
- Super Smash Bros. Melee ISO file

## Installation

### From a Build

Currently, go to the "Actions" tab, select the latest workflow, and select the
artifact for your platform.

Eventually, we will make releases which will have artifacts attached.

### From Source

```bash
pip install "slp2mp4[gui] @ git+https://github.com/davisdude/slp2mp4.git@cleanup"
```

or

```bash
git clone https://github.com/davisdude/slp2mp4.git
git checkout cleanup
pip install .[gui]
```

Both methods require having `git` and `pip` installed

## Usage

### Command Line Interface

```text
usage: slp2mp4 [-h] [-o OUTPUT_DIRECTORY] [-n] [-v] {single,directory,replay_manager} ...

options:
  -h, --help            show this help message and exit
  -o, --output-directory OUTPUT_DIRECTORY
                        set path to output videos
  -n, --dry-run         show inputs and outputs and exit
  -v, --version         show program's version number and exit

mode:
  {single,directory,replay_manager}
    single              convert single replay files to videos
    directory           recursively convert all replay files in a directory to videos
    replay_manager      recursively convert all replay files in a zip to videos
```

### Graphical User Interface

The GUI has all the features that the CLI has. Change your settings in the
menu, select your conversion type, set your directories, then click start.

To launch the GUI, run `slp2mp4_gui`.

## Configuration

`slp2mp4` uses hierarchical settings that come from [TOML][toml] files.
Settings not found in the user configuration (`~/.slp2mp4.toml`) fall back to
the [default settings](#default-settings).

### Default Settings

The default settings can be found [here][default-settings].

### Configuration Options

#### Paths

- `ffmpeg`: Path to FFmpeg executable
- `slippi_playback`: Path to playback Slippi Dolphin executable
- `ssbm_iso`: Path to your Melee ISO file

#### Dolphin Settings

- `backend`: Video backend (`OGL`, `D3D`, `D3D12`, `Vulkan`, `Software`)
- `resolution`: Output resolution (`480p`, `720p`, `1080p`, `1440p`, `2160p`)
- `bitrate`: Video bitrate in kbps
- `volume`: Volume of dolphin (0-100)

#### FFmpeg Settings

- `audio_args`: FFmpeg audio processing settings

#### Runtime Settings

- `parallel`: Number of parallel processes (0 = auto-detect CPU cores)
- `prepend_directory`: Prepend the parent directory info
- `youtubify_names`: Replace some characters in file names for YouTube uploads

### Example Configuration

```toml
[paths]
ffmpeg = "ffmpeg"
slippi_playback = "~/AppData/Roaming/Slippi Launcher/playback/Slippi Dolphin.exe"
ssbm_iso = "~/Games/Melee.iso"

[dolphin]
backend = "OGL"
resolution = "1080p"
bitrate = 16000
volume = 25

[runtime]
parallel = 0
```

or on Windows:

```toml
[paths]
ffmpeg = "C:/Users/user/Downloads/ffmpeg-2025-01-27-git-959b799c8d-essentials_build/bin/ffmpeg.exe"
slippi_playback = "C:/Users/user/AppData/Roaming/Slippi Launcher/playback/Slippi Dolphin.exe"
ssbm_iso = "C:/Users/user/Documents/iso/ssbm.iso"

[dolphin]
backend = "D3D"
resolution = "1080p"
volume = 25
bitrate = 16000

[runtime]
parallel = 0
```

## Notes

* If you get weird looking video (where half the width is cropped), try
  changing the video backend. [Here][dolphin-video-backends] is a list of the
  different video backends; you can find the names used
  [here][dolphin-video-backends-src] for what name to use in the config.

* Does not play nicely with WSL, since dolphin expects all paths to be relative
  to Windows.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


[default-settings]: ./src/slp2mp4/defaults.toml
[dolphin-video-backends-src]: https://github.com/dolphin-emu/dolphin/tree/master/Source/Core/VideoBackends
[dolphin-video-backends]: https://wiki.dolphin-emu.org/index.php?title=Configuration_Guide#Video_Backend
[toml]: https://toml.io/en/
