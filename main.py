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
    parser.add_argument(
        "-o",
        "--output-directory",
        type=pathlib.Path,
        default=".",
        help="output videos to this directory",
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    subparser = parser.add_subparsers(help="run mode", required=True)
    for submodule in submodules_dict.values():
        submodule.register(subparser)
    args = parser.parse_args()

    conf = config.get_config()
    products = args.run(conf, args)
    if args.dry_run:
        for pair in products:
            out_file = pair[0]
            input_files = pair[1]
            print(f"{out_file}:")
            for i in input_files:
                print(f"\t{i}")
