import subprocess
import inspect
import pathlib
import argparse

import config
import modes

submodules_tuple = inspect.getmembers(modes, inspect.ismodule)
submodules_dict = {mod[0]: mod[1] for mod in submodules_tuple}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=sorted(list(submodules_dict)))
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args()

    conf = config.get_config()
    submodules_dict[args.mode].gather(conf, args.path)
