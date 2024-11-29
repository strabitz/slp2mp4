# Convert a group of replays in a directory into a video
# Outputs the video to the current directory

import pathlib
import tempfile
import multiprocessing

import video
import util
import ffmpeg

# TODO: Make multiprocessing more efficient


def _render_directory(conf, directory: pathlib.Path):
    Ffmpeg = ffmpeg.FfmpegRunner(conf)
    files_str = sorted(directory.glob("*.slp"), key=util.natsort)
    files = [pathlib.Path(f) for f in files_str]
    if len(files) == 0:
        return None
    output = pathlib.Path(f"""./{("_").join(directory.parts)}.mp4""")
    with tempfile.TemporaryDirectory() as videodir_str:
        video_files = []
        videodir = pathlib.Path(videodir_str)
        for file in files:
            video_output = pathlib.Path(f"{videodir.joinpath(file.stem)}.mp4")
            video.render(conf, file, video_output)
            video_files.append(video_output)
        Ffmpeg.concat_videos(video_files, output)
    return output


def _get_directories(conf, directory: pathlib.Path):
    outputs = [directory]
    for child in directory.iterdir():
        if child.is_dir():
            outputs.extend(_get_directories(conf, child))
    return outputs


def gather(conf, path: pathlib.Path):
    dirs = _get_directories(conf, path)
    args = [(conf, d) for d in dirs]
    pool = multiprocessing.Pool(conf["runtime"]["parallel"])
    pool.starmap(_render_directory, args)
