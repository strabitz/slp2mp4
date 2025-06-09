import dataclasses
import pathlib

from slp2mp4.output import Output
import slp2mp4.orchestrator as orchestrator
import slp2mp4.config as config

import pathvalidate


class Mode:
    def __init__(self, paths: list[pathlib.Path], output_directory: pathlib.Path):
        self.paths = paths
        self.output_directory = output_directory
        self.conf = None

    def iterator(self, root, path):
        raise NotImplementedError("Child must implement `iterator`")

    def get_name(self, path):
        if self.conf["runtime"]["prepend_directory"]:
            parent_part = ("_").join(path.parent.parts)
            parent_prefix = (
                f"{parent_part}_" if path.parent != pathlib.Path(".") else ""
            )
        else:
            parent_prefix = ""
        name = f"{parent_prefix}{path.stem}.mp4"
        if self.conf["runtime"]["youtubify_names"]:
            name = name.replace("-", "—")
            name = name.replace("(", "⟮")
            name = name.replace(")", "⟯")
        sanitized = pathvalidate.sanitize_filename(self.output_directory / name)
        # Name too long; suffix got dropped
        if not sanitized.suffix:
            # Drop beginning of name since it's more likely to be duplicated
            sanitized = sanitized.parent / (sanitized.name[4:] + ".mp4")
        return sanitized

    def get_outputs(self) -> list[Output]:
        return [
            Output(slps, self.get_name(mp4))
            for path in self.paths
            for slps, mp4 in self.iterator(pathlib.Path("."), path)
        ]

    def run(self, dry_run=False):
        self.conf = config.get_config()
        config.validate_config(self.conf)
        config.translate_config(self.conf)
        products = self.get_outputs()
        if dry_run:
            out = ""
            for output in products:
                out += f"{output.output}\n"
                for i in output.inputs:
                    out += f"\t{i}\n"
            return out
        else:
            self.output_directory.mkdir(parents=True, exist_ok=True)
            orchestrator.run(self.conf, products)


@dataclasses.dataclass
class ModeContainer:
    mode: Mode
    help: str
    description: str
