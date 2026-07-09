"""Smoke test for the manim-rubikscube plugin.
Renders a short clip: fade in a 3D Rubik's cube, do F / U2 / R' moves.
Run with:
    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/plugin_smoke_test.py PluginSmokeTest
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *
from rubikscube import CubeMove, RubiksCube

class PluginSmokeTest(ThreeDScene):
    def construct(self) -> None:
        cube = RubiksCube().scale(0.6)
        self.set_camera_orientation(phi=50 * DEGREES, theta=160 * DEGREES)
        self.renderer.camera.frame_center = cube.get_center()
        self.play(FadeIn(cube))
        self.play(CubeMove(cube, "F"), run_time=1)
        self.play(CubeMove(cube, "U2"), run_time=1)
        self.play(CubeMove(cube, "R'"), run_time=1)
        self.wait(0.5)
