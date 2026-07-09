"""Manim animation for turning one face of the cube."""

from __future__ import annotations

from manim import PI, Animation, VGroup

from .cube_utils import get_axis_from_face, parse_move


class CubeMove(Animation):
    """Rotate one layer of a :class:`~.cube.RubiksCube` by a quarter turn(s).

    The rotation is applied incrementally each frame, so subclasses may
    transform ``self.axis`` after ``__init__`` (this is what the scenes'
    ``OrientedCubeMove`` does for a cube with a baked-in world orientation).
    On finish the cube's logical state is updated via ``apply_move`` so that
    subsequent moves keep matching the geometry.
    """

    def __init__(self, cube, move: str, **kwargs) -> None:
        self.cube = cube
        self.move = move
        self.face, self.turns = parse_move(move)
        # Canonical-frame outward normal; subclasses may rotate this into the
        # cube's current world orientation.
        self.axis = get_axis_from_face(self.face)
        self.angle = -self.turns * PI / 2
        self.layer_group = VGroup(*cube.layer(self.face))
        self._last_angle = 0.0
        self._state_applied = False
        self._about_point = None
        super().__init__(cube, **kwargs)

    def begin(self) -> None:
        self._last_angle = 0.0
        # Lock the pivot once: the cube's bounding-box center moves while a
        # layer's corners swing outward, so re-reading get_center() every
        # frame would make the layer drift off its rotation axis.
        self._about_point = self.cube.get_center().copy()
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