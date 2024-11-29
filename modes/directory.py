# Convert a group of replays in a directory into a video
# Outputs the video to the current directory

import pathlib
import tempfile
import multiprocessing
import os

import video
import util
import ffmpeg

# TODO: Make multiprocessing more efficient


def _get_replays_by_directory(directory: pathlib.Path):
    files = sorted(directory.glob("*.slp"), key=util.natsort)
    outputs = {}
    if len(files) > 0:
        outputs.update({directory: files})
    for child in directory.iterdir():
        if child.is_dir():
            outputs = outputs | _get_replays_by_directory(child)
    return outputs


def gather(conf, path: pathlib.Path):
    Ffmpeg = ffmpeg.FfmpegRunner(conf)
    # Creates temp files for rendering
    replays = _get_replays_by_directory(path)
    tmp_files_by_dir = {
        directory: [
            tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") for f in videos
        ]
        for directory, videos in replays.items()
    }
    args = [
        (conf, replay, pathlib.Path(tmp.name))
        for directory in replays
        for (replay, tmp) in zip(replays[directory], tmp_files_by_dir[directory])
    ]
    # Renders videos
    pool = multiprocessing.Pool(conf["runtime"]["parallel"])
    pool.starmap(video.render, args)
    # Concatenates videos
    outputs = []
    for directory, tmp_files in tmp_files_by_dir.items():
        # TODO: Make relative to `path`?
        output = pathlib.Path(f"""./{("_").join(directory.parts)}.mp4""")
        outputs.append(output)
        Ffmpeg.concat_videos([pathlib.Path(t.name) for t in tmp_files], output)
    # Cleans up temp files
    for t1 in tmp_files_by_dir.values():
        for t2 in t1:
            t2.close()
            os.unlink(t2.name)
    return outputs
