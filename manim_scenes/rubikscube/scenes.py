"""A ThreeDScene base class that takes care of the cube boilerplate.

Inherit from :class:`RubiksCubeScene` instead of ``ThreeDScene`` and you get:

* a default hero camera angle (override the class attributes to change it);
* :meth:`add_cube` - adds a cube and keeps its depth sorting correct every
  frame, so face turns and camera moves never show the cube's insides;
* :meth:`turn` - play a sequence of moves ("R U R' U'") in one call;
* :meth:`fix` - register overlay mobjects as fixed-in-frame without showing
  them yet (so they can still be animated in with FadeIn/Write);
* :meth:`screen_point` - the world point that projects to given frame
  coordinates, for positioning 3D mobjects by screen layout;
* camera-aware wrappers for the arrow builders.

Example::

    class MyScene(RubiksCubeScene):
        def construct(self):
            cube = self.add_cube(RubiksCube().scale(0.8))
            self.turn(cube, "R U R' U'")
            self.play(cube.focus([cube.cubie(0, 0, 2)]))
"""

from __future__ import annotations

import numpy as np
from manim import DEGREES, Mobject, ThreeDScene

from . import arrows as _arrows
from .cube_animations import CubeMove
from .depth import depth_sort_cube


class RubiksCubeScene(ThreeDScene):
    """ThreeDScene with automatic cube depth sorting and small conveniences."""

    #: Default camera orientation; override in subclasses as needed.
    default_phi = 65 * DEGREES
    default_theta = -135 * DEGREES
    default_focal_distance: float | None = None
    default_zoom: float | None = None

    def setup(self) -> None:
        super().setup()
        camera_kwargs = {"phi": self.default_phi, "theta": self.default_theta}
        if self.default_focal_distance is not None:
            camera_kwargs["focal_distance"] = self.default_focal_distance
        if self.default_zoom is not None:
            camera_kwargs["zoom"] = self.default_zoom
        self.set_camera_orientation(**camera_kwargs)
        self._depth_tracked: list = []
        self.add_updater(self._sort_tracked_cubes)

    def _sort_tracked_cubes(self, dt: float = 0.0) -> None:
        for cube in self._depth_tracked:
            depth_sort_cube(cube, self.camera)

    # ------------------------------------------------------------------
    # Cube management
    # ------------------------------------------------------------------
    def add_cube(self, cube, *, track: bool = True):
        """Add ``cube`` to the scene with correct occlusion.

        With ``track=True`` (default) the cube is depth-sorted every frame.
        Use ``track=False`` for static snapshot copies that will never turn
        again, to avoid wasting time re-sorting them.
        """
        depth_sort_cube(cube, self.camera)
        if track:
            self._depth_tracked.append(cube)
        self.add(cube)
        return cube

    def stop_tracking(self, cube) -> None:
        """Stop per-frame depth sorting for ``cube`` (it keeps its z order)."""
        if cube in self._depth_tracked:
            self._depth_tracked.remove(cube)

    def remove_cube(self, cube) -> None:
        self.stop_tracking(cube)
        self.remove(cube)

    def turn(self, cube, moves, *, run_time: float = 0.6, wait: float = 0.0, **kwargs) -> None:
        """Play a sequence of face turns, one ``self.play`` per move.

        ``moves`` is a space-separated string like ``"R U R' U'"`` or an
        iterable of move strings; ``run_time`` applies to each move.
        """
        if isinstance(moves, str):
            moves = moves.split()
        for move in moves:
            self.play(CubeMove(cube, move), run_time=run_time, **kwargs)
            if wait:
                self.wait(wait)

    # ------------------------------------------------------------------
    # Overlay helpers
    # ------------------------------------------------------------------
    def fix(self, *mobjects: Mobject) -> None:
        """Register 2D overlay mobjects as fixed-in-frame without showing
        them yet, so they can still be animated in with FadeIn/Write."""
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.remove(*mobjects)

    def screen_point(self, x: float, y: float) -> np.ndarray:
        """World point that projects to frame coordinates (x, y).

        Uses the camera rotation matrix: rows 0/1 are the world directions of
        screen-right and screen-up. A point in the camera plane through the
        origin has zero depth, so the perspective factor is exactly 1.
        """
        rot = self.camera.get_rotation_matrix()
        return x * rot[0] + y * rot[1]

    # ------------------------------------------------------------------
    # Camera-aware arrow builders
    # ------------------------------------------------------------------
    def swap_arrows(self, cube, cubie_a, cubie_b, **kwargs):
        return _arrows.swap_arrows(cube, cubie_a, cubie_b, camera=self.camera, **kwargs)

    def twist_arrow(self, cube, cubie, **kwargs):
        return _arrows.twist_arrow(cube, cubie, camera=self.camera, **kwargs)

    def flip_arrows(self, cube, edge_cubie, **kwargs):
        return _arrows.flip_arrows(cube, edge_cubie, camera=self.camera, **kwargs)
