# Handles configuration options

import dataclasses
import pathlib
import tomllib
import typing

DEFAULT_CONFIG_FILE = pathlib.Path("defaults.toml")
USER_CONFIG_FILE = pathlib.Path("~/.slp2mp4.toml").expanduser()


def _path(p):
    return pathlib.Path(p).expanduser()


CONSTRUCTORS = {
    "paths": {
        "ffmpeg": _path,
        "slippi_playback": _path,
        "ssbm_ini": _path,
    },
}


def _update_dict(d1: dict, d2: dict):
    for k, v in d2.items():
        if isinstance(v, dict):
            if k not in d1:
                d1[k] = {}
            _update_dict(d1[k], d2[k])
        else:
            d1[k] = v


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
            _update_dict(conf, data)
    _apply_constructors(conf, CONSTRUCTORS)
    return conf


def get_config():
    return _load_configs([DEFAULT_CONFIG_FILE, USER_CONFIG_FILE])
