import argparse
import pathlib
import os

import slp2mp4.video as video


def run(conf, args):
    path = args.path
    output_directory = args.output_directory
    output = f"{output_directory.joinpath(path.stem)}.mp4"
    if not args.dry_run:
        os.makedirs(output_directory, exist_ok=True)
        video.render(conf, path, output)
    return [(output, [path])]


def register(subparser):
    parser = subparser.add_parser("single", help="render a single .slp file to a video")
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
