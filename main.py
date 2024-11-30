import subprocess
import inspect
import pathlib
import argparse

import config
import modes

submodules_tuple = inspect.getmembers(modes, inspect.ismodule)
submodules_dict = {mod[0]: mod[1] for mod in submodules_tuple}

# TODO: dryrun?

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output-directory",
        type=pathlib.Path,
        default=".",
        help="output videos to this directory",
    )
    subparser = parser.add_subparsers(help="run mode", required=True)
    for submodule in submodules_dict.values():
        submodule.register(subparser)
    args = parser.parse_args()

    conf = config.get_config()
    args.run(conf, args)
