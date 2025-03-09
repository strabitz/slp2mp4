TODO

### TODO

* Rest of README.md
* Tests
* Github actions?
* Config / input validation
* Mode for using files output by replay manager (zips)
* Config path validation (during dry run)


### Notes

* If you get weird looking video (where half the width is cropped), try
  changing the video backend. [Here][dolphin-video-backends] is a list of the
  different video backends; you can find the names used
  [here][dolphin-video-backends-src] for what name to use in the config.

* Does not play nicely with WSL. Slippi playback expects all paths to be
  relative to Windows. Because `slp2mp4` parses the replay file to determine
  match length, both the WSL-relative and Windows-relative paths for each
  replay file would have to be determined. I could try to determine if the user
  is running under WSL and convert the path if possible.

    * Note to future self: `paths.ssbm_ini` must be the Windows file path (use
      `/` instead of `\`)

* Currently using [`py-slippi`][py-slippi] instead of [`peppi-py`][peppi-py]
  because of numerous issues related to `pyarrow` and `maturin` on Windows /
  Mac.

    * When the switch is made, the API is largely the same, but peppi's frame
      count starts *once players are actionable* (after ready/go), while
      py-slippi's frame count includes these frames.


[dolphin-video-backends-src]: https://github.com/dolphin-emu/dolphin/tree/master/Source/Core/VideoBackends
[dolphin-video-backends]: https://wiki.dolphin-emu.org/index.php?title=Configuration_Guide#Video_Backend
[peppi-py]: https://github.com/hohav/peppi-py
[py-slippi]: https://github.com/hohav/py-slippi
