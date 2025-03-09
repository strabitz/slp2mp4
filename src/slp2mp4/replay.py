# Logic for interacting with a single slippi replay file

import dataclasses
import pathlib

import slippi

_READY_GO_FRAMES = 124
_END_SCREEN_FRAMES = 114


@dataclasses.dataclass
class ReplayFile:
    slp_path: pathlib.Path
    slp_data: slippi.Game = dataclasses.field(init=False)

    def __post_init__(self):
        self.slp_data = slippi.Game(str(self.slp_path), skip_frames=True)

    def get_slp_filename(self):
        return str(self.slp_path.absolute())

    def get_expected_number_of_frames(self):
        # gameplay_frames = _READY_GO_FRAMES + self.slp_data.metadata["lastFrame"] # TODO: peppi
        gameplay_frames = self.slp_data.metadata.duration
        end_frames = (
            _END_SCREEN_FRAMES if (self.slp_data.end.lras_initiator is None) else 0
        )
        return gameplay_frames + end_frames
