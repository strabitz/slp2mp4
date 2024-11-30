import argparse
import pathlib

import video
import pathlib


def run(conf, args):
    path = args.path
    output = f"{path.parent.joinpath(path.stem)}.mp4"
    video.render(conf, path, output)
    return [output]


def register(subparser):
    parser = subparser.add_parser("single", help="render a single .slp file to a video")
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
