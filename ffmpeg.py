# Logic for joining audio / video files

import subprocess
import pathlib
import tempfile


class FfmpegRunner:
    def __init__(self, config):
        self.ffmpeg_path = config["paths"]["ffmpeg"]

    # Assumes output file can handle no reencoding
    # Returns True if ffmpeg ran successfully, False otherwise
    def merge_audio_and_video(
        self,
        audio_file: pathlib.Path,
        video_file: pathlib.Path,
        output_file: pathlib.Path,
    ) -> bool:
        args = (
            (self.ffmpeg_path,),
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
    def concat_videos(self, videos: [pathlib.Path], output_file: pathlib.Path) -> bool:
        with tempfile.NamedTemporaryFile(mode="w") as concat_file:
            files = ("\n").join(f"file {video.resolve()}" for video in videos)
            concat_file.write(files)
            concat_file.flush()
            args = (
                (self.ffmpeg_path,),
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
