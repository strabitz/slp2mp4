# Logic for dolphin comm configuration
# https://github.com/project-slippi/slippi-wiki/blob/master/COMM_SPEC.md

import uuid
import tempfile
import json
import contextlib
import os

import slp2mp4.replay as replay


@contextlib.contextmanager
def make_temp_file(replay_file: replay.ReplayFile):
    config = {
        "mode": "normal",
        "replay": replay_file.get_slp_filename(),
        "isRealTimeMode": False,
        "commandId": str(uuid.uuid4()),
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
        file.write(json.dumps(config))
        file.close()
        try:
            yield file.name
        finally:
            os.unlink(file.name)
