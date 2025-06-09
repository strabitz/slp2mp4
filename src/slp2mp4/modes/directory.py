import pathlib

from slp2mp4.modes.mode import Mode
from slp2mp4.output import Output
import slp2mp4.util as util


class Directory(Mode):
    def iterator(self, location, path):
        if (not path.exists()) or (not path.is_dir()):
            raise FileNotFoundError(path.name)
        slps = list(sorted(path.glob("*.slp"), key=util.natsort))
        if len(slps) > 0:
            loc = location if (location != pathlib.Path(".")) else util.get_parent_as_path(path)
            yield slps, loc, pathlib.Path(path.name)
        for child in path.iterdir():
            if child.is_dir():
                yield from self.iterator(location / path.name, path / child)
