# Convert a group of replays in a directory into a video
# Outputs the video to the current directory

import argparse
import pathlib
import tempfile
import multiprocessing
import queue
import os

import video
import util
import ffmpeg


def _get_inputs_and_outputs(directory: pathlib.Path):
    outputs = {}
    slps = list(sorted(directory.glob("*.slp"), key=util.natsort))
    # TODO: Make relative to "root" path
    name = f"""./{("_").join(directory.parts)}.mp4"""
    if len(slps) > 0:
        outputs[name] = slps
    for child in directory.iterdir():
        if child.is_dir():
            outputs = outputs | _get_inputs_and_outputs(child)
    return outputs


def _render(conf, slp_queue, video_queue):
    while True:
        data = slp_queue.get()
        if data is None:
            break
        key, path = data
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        video.render(conf, path, pathlib.Path(tmp.name))
        tmp.close()
        video_queue.put((key, {path: tmp.name}))


def _concat(conf, video_queue, inputs_and_outputs):
    Ffmpeg = ffmpeg.FfmpegRunner(conf)
    outputs = {}
    while True:
        data = video_queue.get()
        if data is None:
            break
        key, tmpfile = data
        if key not in outputs:
            outputs[key] = {}
        outputs[key] = outputs[key] | tmpfile
        if len(outputs[key]) < len(inputs_and_outputs[key]):
            continue
        tmpfiles = [outputs[key][path] for path in inputs_and_outputs[key]]
        output_file = key
        Ffmpeg.concat_videos([pathlib.Path(t) for t in tmpfiles], output_file)
        for tmp in tmpfiles:
            os.unlink(tmp)


def run(conf, args):
    path = args.path
    inputs_and_outputs = _get_inputs_and_outputs(path)

    slp_queue = multiprocessing.Queue()
    video_queue = multiprocessing.Queue()

    slp_pool = multiprocessing.Pool(
        conf["runtime"]["parallel"],
        _render,
        (
            conf,
            slp_queue,
            video_queue,
        ),
    )
    video_pool = multiprocessing.Pool(
        1,
        _concat,
        (
            conf,
            video_queue,
            inputs_and_outputs,
        ),
    )

    for key, slps in inputs_and_outputs.items():
        for slp in slps:
            slp_queue.put(
                (
                    key,
                    slp,
                )
            )

    for i in range(conf["runtime"]["parallel"]):
        slp_queue.put(None)

    slp_queue.close()
    slp_queue.join_thread()

    slp_pool.close()
    slp_pool.join()

    video_queue.put(None)

    video_queue.close()
    video_queue.join_thread()

    video_pool.close()
    video_pool.join()


def register(subparser):
    parser = subparser.add_parser(
        "directory",
        help="render and combine .slp files in a directory to a video, recursively",
    )
    parser.add_argument("path", type=pathlib.Path)
    parser.set_defaults(run=run)
