# Commonizes the batching / concatenating of slippi files
# There are to threads here:
#   1. The "render" thread, which runs dolphin / does frame dumps
#   2. The "concat" thread, which contatenates frame-dumps into a single mp4

import multiprocessing
import os
import pathlib
import queue
import tempfile

import slp2mp4.ffmpeg as ffmpeg
import slp2mp4.video as video


def _render(conf, slp_queue, video_queue):
    while True:
        data = slp_queue.get()
        if data is None:
            break
        output_name, slp_path = data
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        video.render(conf, slp_path, pathlib.Path(tmp.name))
        tmp.close()
        video_queue.put((output_name, slp_path, tmp.name))


def _concat(conf, video_queue, inputs_and_outputs):
    Ffmpeg = ffmpeg.FfmpegRunner(conf)
    outputs = {}
    while True:
        data = video_queue.get()
        if data is None:
            break
        output_name, slp_path, mp4_path = data
        if output_name not in outputs:
            outputs[output_name] = {}
        outputs[output_name][slp_path] = mp4_path
        if len(outputs[output_name]) < len(inputs_and_outputs[output_name]):
            continue
        tmpfiles = [
            pathlib.Path(outputs[output_name][slp])
            for slp in inputs_and_outputs[output_name]
        ]
        Ffmpeg.concat_videos(tmpfiles, output_name)
        for tmp in tmpfiles:
            os.unlink(tmp)


def run(conf, inputs_and_outputs):
    num_procs = conf["runtime"]["parallel"]
    slp_queue = multiprocessing.Queue()
    video_queue = multiprocessing.Queue()
    slp_pool = multiprocessing.Pool(
        num_procs,
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

    for output_name, input_names in inputs_and_outputs.items():
        for slp in input_names:
            slp_queue.put(
                (
                    output_name,
                    slp,
                )
            )

    for i in range(num_procs):
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
