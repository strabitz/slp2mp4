# Logic to orchestrate making a video file from a slippi replay

import pathlib
import tempfile

import ffmpeg
import replay
import dolphin.runner


# Returns True if the render succeeded, False otherwise
# output_path must be a container that requires no reencoding, e.g. mkv
def render(slp_path: pathlib.Path, output_path: pathlib.Path) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = pathlib.Path(tmpdir_str)
        r = replay.ReplayFile(slp_path)
        audio_file, video_file = dolphin.runner.run_dolphin(r, tmpdir)
        success = ffmpeg.merge_audio_and_video(audio_file, video_file, output_path)
        return success
