# Version History

## 3.0.4

- Fixed `~` not being validated properly in config paths
- Use proper dolphin backend names
- Handle invalid TOML files more gracefully
- Fixed `resolution` dropdown in GUI

## 3.0.3

- Fixed a bug where `replay_manager` sometimes wouldn't work properly on
  Windows due to very long path names
- Improved output file name handling
- Changed `volume` to be an ffmpeg setting, since Dolphin framedump ignores
  volume settings apparently
- Only sanitize output filename, not whole directory
- Allow using more than 1 process per CPU

## 3.0.2

- Works on Windows again (how silly of me to assume `os.sched_getaffinity` would
  be multiplatform).

## 3.0.1

- Allow `replay_manager` to accept directories or `.zip` files.

## 3.0.0

- Totally reworked. Run modes:
    - `single`
    - `directory`
    - `replay_manager`
- Added a GUI
- Settings for volume, file output configuration, and more

## Prior

Ancient history.
