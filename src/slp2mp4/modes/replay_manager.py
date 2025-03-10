import argparse
import atexit
import os
import pathlib
import shutil
import tempfile
import zipfile

from .directory import get_inputs_and_outputs

# TODO: Use context.json to get names?


def _recursively_unzip(zip_file, to_dir):
    with zipfile.ZipFile(zip_file, "r") as zfile:
        zfile.extractall(path=to_dir)
    for root, dirs, files in to_dir.walk():
        for file in files:
            if zipfile.is_zipfile(file):
                _recursively_unzip(file, root)


def run(conf, args):
    if not args.path.exists():
        raise FileNotFoundError(args.path.name)
    if not args.path.is_dir() and zipfile.is_zipfile(args.path):
        files = [args.path]
    else:
        files = []
        for root, _, walk_files in args.path.walk():
            for file in walk_files:
                path = root / file
                if zipfile.is_zipfile(path):
                    files.append(path)
    # Needs to persist until all conversions are done
    with tempfile.TemporaryDirectory(delete=False) as tmpdir_str:
        tmpdir = pathlib.Path(tmpdir_str)
        atexit.register(shutil.rmtree, tmpdir)
        for file in files:
            _recursively_unzip(file, tmpdir / file.stem)
        return get_inputs_and_outputs(tmpdir, tmpdir, args.output_directory)


def register(subparser):
    parser = subparser.add_parser(
        "replay_manager",
        help="render and combine replay manager zips",
    )
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
