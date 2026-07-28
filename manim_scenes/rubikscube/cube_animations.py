"""Manim animation for turning one face of the cube."""

from __future__ import annotations

import numpy as np
from manim import PI, Animation, VGroup

from .cube_utils import get_axis_from_face, normalize, parse_move


class CubeMove(Animation):
    """Rotate one layer of a :class:`~.cube.RubiksCube` by a quarter turn(s).

    The turn axis is derived from the cube's *current world geometry* when
    the animation begins, so the same ``CubeMove(cube, "R")`` works whether
    the cube is axis-aligned under a ThreeDCamera, carries a baked-in 2D
    orientation matrix, or has been rotated by hand.

    The rotation is applied incrementally each frame, so subclasses may still
    override ``self.axis`` after ``__init__`` (legacy ``OrientedCubeMove``
    scene code keeps working). On finish the cube's logical state is updated
    via ``apply_move`` so that subsequent moves keep matching the geometry.
    """

    def __init__(self, cube, move: str, **kwargs) -> None:
        self.cube = cube
        self.move = move
        self.face, self.turns = parse_move(move)
        # Canonical-frame outward normal; replaced by the geometric axis in
        # begin() unless a subclass already rotated it.
        self.axis = get_axis_from_face(self.face)
        self.angle = -self.turns * PI / 2
        self.layer_group = VGroup(*cube.layer(self.face))
        self._last_angle = 0.0
        self._state_applied = False
        self._about_point = None
        super().__init__(cube, **kwargs)

    def _geometric_axis(self) -> np.ndarray | None:
        face_axis = getattr(self.cube, "face_axis", None)
        if face_axis is None:
            return None
        axis = face_axis(self.face)
        return axis if np.linalg.norm(axis) > 1e-9 else None

    def begin(self) -> None:
        self._last_angle = 0.0
        # Adopt the cube's world-space face normal, unless a subclass already
        # customised the axis (in which case we leave it alone).
        if np.allclose(self.axis, get_axis_from_face(self.face)):
            axis = self._geometric_axis()
            if axis is not None:
                self.axis = axis
        else:
            self.axis = normalize(self.axis)
        # Lock the pivot once: the cube's bounding-box center moves while a
        # layer's corners swing outward, so re-reading the center every frame
        # would make the layer drift off its rotation axis.
        center_of = getattr(self.cube, "get_cube_center", self.cube.get_center)
        self._about_point = np.array(center_of(), dtype=float)
        super().begin()

    def interpolate_mobject(self, alpha: float) -> None:
        # ``alpha`` arrives raw; apply the rate function ourselves because we
        # rotate incrementally instead of interpolating from a start copy.
        current_angle = self.angle * self.rate_func(alpha)
        delta = current_angle - self._last_angle
        if abs(delta) > 1e-9:
            self.layer_group.rotate(delta, axis=self.axis, about_point=self._about_point)
            self._last_angle = current_angle

    def finish(self) -> None:
        super().finish()
        if not self._state_applied:
            self.cube.apply_move(self.move)
            self._state_applied = True
