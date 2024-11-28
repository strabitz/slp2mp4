# Wrapper for running dolphin

import tempfile
import time
import pathlib
import subprocess

import replay
import dolphin.comm as comm
import dolphin.ini as ini

# TODO: Configurable
DOLPHIN_PATH = pathlib.Path(
    "/home/davis/.config/Slippi Launcher/playback/Slippi_Playback-x86_64.AppImage"
)
MELEE_ISO_PATH = pathlib.Path(
    "/home/davis/files/games/Super Smash Bros. Melee (USA) (En,Ja) (Rev 2).iso"
)
VIDEO_BACKEND = "OGL"


def _get_number_of_frames_rendered(frames_file: pathlib.Path) -> int:
    try:
        with open(frames_file, "r") as f:
            return len(list(f))
    except FileNotFoundError:
        return 0


def render(replay: replay.ReplayFile, dump_dir: pathlib.Path):
    with tempfile.TemporaryDirectory() as userdir_str:
        userdir = pathlib.Path(userdir_str)
        with (
            comm.make_temp_file(replay) as comm_file,
            ini.make_dolphin_file(userdir) as dolphin_file,
            ini.make_gfx_file(userdir) as gfx_file,
        ):
            args = (
                (DOLPHIN_PATH,),
                (
                    "-e",
                    MELEE_ISO_PATH,
                ),
                ("-b",),
                (
                    "-v",
                    VIDEO_BACKEND,
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
    # TODO: Return framedump / dsdump?
