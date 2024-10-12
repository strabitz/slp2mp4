# Logic for dolphin comm configuration
# https://github.com/project-slippi/slippi-wiki/blob/master/COMM_SPEC.md

import uuid
import tempfile
import json
import contextlib

import replay


@contextlib.contextmanager
def make_temp_file(replay_file: replay.ReplayFile):
    config = {
        "mode": "normal",
        "replay": replay_file.get_slp_filename(),
        "isRealTimeMode": False,
        "commandId": str(uuid.uuid4()),
    }
    with tempfile.NamedTemporaryFile(mode="w") as file:
        file.write(json.dumps(config))
        file.flush()
        yield file.name
