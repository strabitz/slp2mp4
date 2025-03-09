import argparse
import pathlib

import slp2mp4.util as util


def _get_inputs_and_outputs(
    root: pathlib.Path, in_dir: pathlib.Path, out_dir: pathlib.Path
):
    outputs = {}
    slps = list(sorted(in_dir.glob("*.slp"), key=util.natsort))
    root_name = pathlib.Path(root.resolve().name)
    relative_path = root_name.joinpath(in_dir.relative_to(root))
    name = f"""{out_dir.joinpath(("_").join(relative_path.parts))}.mp4"""
    if len(slps) > 0:
        outputs[name] = slps
    for child in in_dir.iterdir():
        if child.is_dir():
            outputs = outputs | _get_inputs_and_outputs(root, child, out_dir)
    return outputs


def run(conf, args):
    return _get_inputs_and_outputs(args.path, args.path, args.output_directory)


def register(subparser):
    parser = subparser.add_parser(
        "directory",
        help="render and combine .slp files in a directory to a video, recursively",
    )
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
