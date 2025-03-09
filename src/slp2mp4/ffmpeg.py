# Logic for joining audio / video files

import pathlib
import tempfile
import subprocess

import slp2mp4.util as util


class FfmpegRunner:
    def __init__(self, config):
        self.ffmpeg_path = config["paths"]["ffmpeg"]

    def _run(self, args):
        ffmpeg_args = [self.ffmpeg_path] + util.flatten_arg_tuples(args)
        subprocess.run(ffmpeg_args, check=True)

    def reencode_audio(self, audio_file_path: pathlib.Path):
        reencoded_path = audio_file_path.parent / "fixed.wav"
        args = (
            ("-y",),
            (
                "-i",
                audio_file_path,
            ),
            (
                "-ar",
                "32000",
            ),
            (
                "-c:a",
                "pcm_s16le",
            ),
            (
                "-ac",
                "2",
            ),
            (reencoded_path,),
        )
        self._run(args)
        return reencoded_path

    # Assumes output file can handle no reencoding
    # Returns True if ffmpeg ran successfully, False otherwise
    def merge_audio_and_video(
        self,
        audio_file: pathlib.Path,
        video_file: pathlib.Path,
        output_file: pathlib.Path,
    ):
        args = (
            ("-y",),
            (
                "-i",
                audio_file,
            ),
            (
                "-i",
                video_file,
            ),
            ("-xerror",),
            (output_file,),
        )
        self._run(args)

    # Assumes all videos have the same encoding
    def concat_videos(self, videos: [pathlib.Path], output_file: pathlib.Path):
        # Make a temp directory because windows doesn't like NamedTemporaryFiles :(
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(pathlib.Path(tmpdir) / "concat.txt", "w") as concat_file:
                files = ("\n").join(f"file '{video.resolve()}'" for video in videos)
                concat_file.write(files)
                concat_file.flush()
                args = (
                    ("-y",),
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
                self._run(args)
