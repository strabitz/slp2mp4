# src/slp2mp4/clipper.py
"""
Clipping functionality that detects D-pad down presses and creates clips
"""

import pathlib
import subprocess
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

from slippi import Game
from slippi.event import Buttons

import slp2mp4.ffmpeg as ffmpeg
import slp2mp4.util as util


logger = logging.getLogger(__name__)


@dataclass
class ClipMarker:
    """Represents a clip marker with frame and time information"""
    frame_index: int
    time_seconds: float
    port: int
    
    def get_clip_start(self, duration: float = 10.0) -> float:
        """Get the start time for the clip (default 10 seconds before marker)"""
        return max(0, self.time_seconds - duration)
    
    def get_clip_duration(self, total_duration: float, clip_duration: float = 10.0) -> float:
        """Get the actual duration of the clip, accounting for video boundaries"""
        start = self.get_clip_start(clip_duration)
        # Ensure we don't go past the end of the video
        return min(clip_duration, total_duration - start)


class SlippiClipper:
    """Handles detection of D-pad down presses and clip creation"""
    
    def __init__(self, config):
        self.config = config
        self.ffmpeg_runner = ffmpeg.FfmpegRunner(config)
        self.clip_duration = 10.0  # seconds before the marker
        self.framerate = 60.0  # Melee runs at 60 FPS
        
    def find_dpad_markers(self, slp_path: pathlib.Path) -> List[ClipMarker]:
        """
        Parse SLP file and find all frames where D-pad down was pressed
        
        Returns list of ClipMarker objects
        """
        markers = []
        
        try:
            game = Game(slp_path)
            
            # Track previous frame button states to detect new presses
            prev_buttons = [None] * 4
            
            for frame in game.frames:
                for port_idx, port in enumerate(frame.ports):
                    if port and port.leader and port.leader.pre:
                        current_buttons = port.leader.pre.buttons.physical
                        
                        # Check if D-pad down is newly pressed this frame
                        if current_buttons & Buttons.Physical.DPAD_DOWN:
                            # Check if it wasn't pressed in previous frame (new press)
                            if prev_buttons[port_idx] is None or not (prev_buttons[port_idx] & Buttons.Physical.DPAD_DOWN):
                                # Convert frame index to time
                                # Frame indices start at -123, with 0 being "GO"
                                absolute_frame = frame.index - (-123)
                                time_seconds = absolute_frame / self.framerate
                                
                                marker = ClipMarker(
                                    frame_index=frame.index,
                                    time_seconds=time_seconds,
                                    port=port_idx + 1  # Convert to 1-indexed port number
                                )
                                markers.append(marker)
                                logger.info(f"Found D-pad down marker at frame {frame.index} (port {marker.port})")
                        
                        prev_buttons[port_idx] = current_buttons
                        
        except Exception as e:
            logger.error(f"Error parsing SLP file {slp_path}: {e}")
            raise
            
        return markers
    
    def create_clip(self, video_path: pathlib.Path, marker: ClipMarker, output_path: pathlib.Path) -> bool:
        """
        Create a clip from the video file using ffmpeg
        
        Args:
            video_path: Path to the full video file
            marker: ClipMarker containing timing information
            output_path: Path for the output clip
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get video duration to ensure we don't clip beyond bounds
            duration_cmd = [
                str(self.config["paths"]["ffmpeg"]),
                "-i", str(video_path),
                "-hide_banner",
                "-f", "null",
                "-"
            ]
            
            # This is a quick way to get duration, but you might want a more robust method
            # For now, we'll just use the marker time + some buffer
            total_duration = marker.time_seconds + 60  # Assume video is at least 1 minute longer
            
            start_time = marker.get_clip_start(self.clip_duration)
            duration = marker.get_clip_duration(total_duration, self.clip_duration)
            
            # Build ffmpeg command for clipping
            args = [
                str(self.config["paths"]["ffmpeg"]),
                "-y",  # Overwrite output
                "-ss", str(start_time),  # Seek to start time
                "-i", str(video_path),   # Input file
                "-t", str(duration),     # Duration of clip
                "-c", "copy",            # Copy codecs (no re-encoding for speed)
                "-avoid_negative_ts", "make_zero",
                str(output_path)
            ]
            
            logger.info(f"Creating clip: {start_time:.2f}s for {duration:.2f}s")
            subprocess.run(args, check=True, capture_output=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error creating clip: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error creating clip: {e}")
            return False
    
    def process_replay_clips(self, slp_path: pathlib.Path, video_path: pathlib.Path, 
                           output_dir: pathlib.Path) -> List[pathlib.Path]:
        """
        Process a replay to find markers and create clips
        
        Args:
            slp_path: Path to the .slp replay file
            video_path: Path to the converted .mp4 video
            output_dir: Directory to save clips
            
        Returns:
            List of paths to created clips
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all D-pad down markers
        markers = self.find_dpad_markers(slp_path)
        
        if not markers:
            logger.info(f"No D-pad down markers found in {slp_path}")
            return []
        
        logger.info(f"Found {len(markers)} clip markers")
        
        created_clips = []
        
        for i, marker in enumerate(markers):
            # Generate clip filename
            base_name = video_path.stem
            clip_name = f"{base_name}_clip_{i+1:02d}_p{marker.port}_f{marker.frame_index}.mp4"
            clip_path = output_dir / clip_name
            
            if self.create_clip(video_path, marker, clip_path):
                created_clips.append(clip_path)
                logger.info(f"Created clip: {clip_path}")
            else:
                logger.error(f"Failed to create clip {i+1}")
                
        return created_clips


# Integration with existing modes
class ClippingMode:
    """Mode that processes existing videos to create clips"""
    
    def __init__(self, paths: List[pathlib.Path], output_directory: pathlib.Path):
        self.paths = paths
        self.output_directory = output_directory
        self.conf = None
        
    def run(self, dry_run=False):
        import slp2mp4.config as config
        self.conf = config.get_config()
        config.translate_and_validate_config(self.conf)
        
        clipper = SlippiClipper(self.conf)
        
        all_clips = []
        
        for path in self.paths:
            if path.suffix.lower() == '.mp4':
                # Look for corresponding .slp file
                slp_path = path.with_suffix('.slp')
                if not slp_path.exists():
                    # Try looking in common locations
                    logger.warning(f"Could not find .slp file for {path}")
                    continue
                    
                if dry_run:
                    markers = clipper.find_dpad_markers(slp_path)
                    print(f"\nWould create {len(markers)} clips from {path}:")
                    for i, marker in enumerate(markers):
                        print(f"  Clip {i+1}: Port {marker.port}, Frame {marker.frame_index}, "
                              f"Time {marker.time_seconds:.2f}s")
                else:
                    clips = clipper.process_replay_clips(slp_path, path, self.output_directory)
                    all_clips.extend(clips)
                    
            elif path.suffix.lower() == '.slp':
                # Look for corresponding .mp4 file
                mp4_path = path.with_suffix('.mp4')
                if not mp4_path.exists():
                    logger.warning(f"Could not find .mp4 file for {path}")
                    continue
                    
                if dry_run:
                    markers = clipper.find_dpad_markers(path)
                    print(f"\nWould create {len(markers)} clips from {mp4_path}:")
                    for i, marker in enumerate(markers):
                        print(f"  Clip {i+1}: Port {marker.port}, Frame {marker.frame_index}, "
                              f"Time {marker.time_seconds:.2f}s")
                else:
                    clips = clipper.process_replay_clips(path, mp4_path, self.output_directory)
                    all_clips.extend(clips)
                    
        if not dry_run:
            print(f"\nCreated {len(all_clips)} total clips")
            for clip in all_clips:
                print(f"  {clip}")
                
        return None  # Matches expected return type from other modes