# Wrapper for running dolphin

import tempfile
import time
import pathlib
import subprocess

import replay
import dolphin.comm as comm
import dolphin.ini as ini


def _get_number_of_frames_rendered(frames_file: pathlib.Path) -> int:
    try:
        with open(frames_file, "r") as f:
            return len(list(f))
    except FileNotFoundError:
        return 0


class DolphinRunner:
    def __init__(self, config):
        self.slippi_playback = config["paths"]["slippi_playback"]
        self.ssbm_ini = config["paths"]["ssbm_ini"]
        self.video_backend = config["video"]["backend"]
        self.user_gfx = {
            "Settings": {"EFBScale": config["video"]["resolution"]},
        }

    def run_dolphin(self, replay: replay.ReplayFile, dump_dir: pathlib.Path):
        with tempfile.TemporaryDirectory() as userdir_str:
            userdir = pathlib.Path(userdir_str)
            with (
                comm.make_temp_file(replay) as comm_file,
                ini.make_dolphin_file(userdir) as dolphin_file,
                ini.make_gfx_file(userdir, self.user_gfx) as gfx_file,
            ):
                args = (
                    (self.slippi_playback,),
                    (
                        "-e",
                        self.ssbm_ini,
                    ),
                    ("-b",),
                    (
                        "-v",
                        self.video_backend,
                    ),
                    (
                        "-i",
                        comm_file,
                    ),
                    ("--hide-seekbar",),
                    (
                        "--output-directory",
                        dump_dir,
                    ),
                    (
                        "--user",
                        userdir,
                    ),
                )
                dolphin_args = [arg for arg_tuple in args for arg in arg_tuple]
                proc = subprocess.Popen(args=dolphin_args)
                frames_file = userdir.joinpath("Logs", "render_time.txt")
                expected_frames = replay.get_expected_number_of_frames()
                while _get_number_of_frames_rendered(frames_file) < expected_frames:
                    if proc.poll() is not None:
                        print("Dolphin terminated early")
                        break
                    time.sleep(1)

                # Kills dolphin (if need be) when finished dumping
                print("Terminating dolphin")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired as t:
                    print("Timed out waiting for Dolphin to terminate")
                    proc.kill()
        # TODO: Detect other paths; when do other paths happen?
        audio_file = dump_dir.joinpath("dspdump.wav")
        video_file = dump_dir.joinpath("framedump0.avi")
        return audio_file, video_file
