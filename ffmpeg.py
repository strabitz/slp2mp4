# Logic for joining audio / video files

import subprocess
import pathlib

# TODO: Configurable
FFMPEG_COMMAND = "ffmpeg"


# Assumes output file can handle no reencoding
# Returns True if ffmpeg ran successfully, False otherwise
def merge_audio_and_video(
    audio_file: pathlib.Path, video_file: pathlib.Path, output_file: pathlib.Path
) -> bool:
    args = (
        (FFMPEG_COMMAND,),
        (
            "-i",
            audio_file,
        ),
        (
            "-i",
            video_file,
        ),
        (
            "-c",
            "copy",
        ),
        ("-xerror",),
        (output_file,),
    )
    ffmpeg_args = [arg for arg_tuple in args for arg in arg_tuple]
    output = subprocess.run(ffmpeg_args)
    return output.returncode == 0
