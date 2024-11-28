# Logic for joining audio / video files

import subprocess
import pathlib
import tempfile

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


# Assumes all videos have the same encoding
def concat_videos(videos: [pathlib.Path], output_file: pathlib.Path) -> bool:
    with tempfile.NamedTemporaryFile(mode="w") as concat_file:
        files = ("\n").join(f"file {video.resolve()}" for video in videos)
        concat_file.write(files)
        concat_file.flush()
        args = (
            (FFMPEG_COMMAND,),
            (
                "-f",
                "concat",
            ),
            (
                "-safe",
                "0",
            ),
            (
                "-i",
                concat_file.name,
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
