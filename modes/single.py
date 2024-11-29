# Convert a single replay into a video
# Outputs the video next to the replay

import video
import pathlib


def gather(conf, path: pathlib.Path):
    output = f"{path.parent.joinpath(path.stem)}.mp4"
    video.render(conf, path, output)
    return [output]
