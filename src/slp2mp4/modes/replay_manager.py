import atexit
import pathlib
import shutil
import tempfile
import zipfile

import pathlib

from slp2mp4.modes.mode import Mode
from slp2mp4.output import Output
from slp2mp4.modes.mode import Mode
import slp2mp4.util as util


# TODO: Use context.json to get names?
def _make_tmpdir():
    tmpdir = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tmpdir)
    return pathlib.Path(tmpdir)


class ReplayManager(Mode):
    def __init__(self, paths: list[pathlib.Path], output_directory: pathlib.Path):
        self.lookups = {}
        self.paths = self._extract_helper(paths)
        self.output_directory = output_directory

    def iterator(self, _root, path):
        yield self.lookups[path]

    def _extract_helper(self, paths):
        for path in paths:
            root = pathlib.Path(path.absolute().name) if path.is_dir() else util.get_parent_as_path(path) / path.stem
            self._recursive_extract(root, path)
        return self.lookups.keys()

    def _recursive_extract(self, location, path, fromzip=False):
        if zipfile.is_zipfile(path):
            tmpdir = _make_tmpdir()
            with zipfile.ZipFile(path, "r") as zfile:
                zfile.extractall(path=tmpdir)
            self._recursive_extract(location, tmpdir, True)
        else:
            slps = list(sorted(path.glob("*.slp"), key=util.natsort))
            if len(slps) > 0 and fromzip:
                self.lookups[location] = (slps, location.parent, pathlib.Path(location.name))
            for child in path.iterdir():
                if child.is_dir() or zipfile.is_zipfile(child):
                    self._recursive_extract(location / child.stem, child, fromzip)
