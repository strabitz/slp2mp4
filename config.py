# Handles configuration options

import dataclasses
import pathlib
import tomllib
import typing

import util

DEFAULT_CONFIG_FILE = pathlib.Path("defaults.toml")
USER_CONFIG_FILE = pathlib.Path("~/.slp2mp4.toml").expanduser()


def _path(p):
    return pathlib.Path(p).expanduser()


def _parse_resolution(r):
    resolutions = {"480p": "2", "720p": "3", "1080p": "5", "1440p": "6", "2160p": "8"}
    return resolutions[r]


CONSTRUCTORS = {
    "paths": {
        "ffmpeg": _path,
        "slippi_playback": _path,
        "ssbm_ini": _path,
    },
    "video": {
        "resolution": _parse_resolution,
    },
}


def _apply_constructors(conf: dict, constructors: dict):
    for k, constructor in constructors.items():
        if isinstance(constructor, typing.Callable):
            conf[k] = constructor(conf[k])
        elif isinstance(constructor, dict):
            _apply_constructors(conf[k], constructor)


def _load_configs(config_files: [pathlib.Path]) -> dict:
    conf = {}
    for file in config_files:
        with open(file, "rb") as f:
            data = tomllib.load(f)
            util.update_dict(conf, data)
    _apply_constructors(conf, CONSTRUCTORS)
    return conf


def get_config():
    return _load_configs([DEFAULT_CONFIG_FILE, USER_CONFIG_FILE])
