import argparse
import pathlib
import os


def run(conf, args):
    path = args.path
    output_directory = args.output_directory
    output = f"{output_directory.joinpath(path.stem)}.mp4"
    return {output: [path]}


def register(subparser):
    parser = subparser.add_parser("single", help="render a single .slp file to a video")
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
