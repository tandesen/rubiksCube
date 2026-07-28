"""A 2x2x2 pocket cube compatible with the local ``CubeMove`` animation."""

from __future__ import annotations

import numpy as np
from manim import PI, VGroup
from manim.utils.space_ops import rotation_matrix

from .cube_utils import FACE_COLORS, FACE_NORMALS, FACE_ORDER, parse_move
from .cubie import Cubie


_FACE_LAYERS = {
    "F": (0, 0),
    "B": (0, 1),
    "R": (1, 0),
    "L": (1, 1),
    "D": (2, 0),
    "U": (2, 1),
}


class RubiksCube2x2(VGroup):
    """A 2x2x2 cube with the layer/apply_move API expected by ``CubeMove``."""

    def __init__(self, colors: list[str] | None = None, cubie_side: float = 1.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.order = 2
        self.cubie_side = cubie_side
        if colors is None:
            self.face_colors = dict(FACE_COLORS)
        else:
            if len(colors) != 6:
                raise ValueError("colors must contain six entries: [U, R, F, D, L, B]")
            self.face_colors = dict(zip(FACE_ORDER, colors))

        self.cubies = np.empty((self.order, self.order, self.order), dtype=object)
        offset = (self.order - 1) / 2.0
        for x in range(self.order):
            for y in range(self.order):
                for z in range(self.order):
                    cubie = Cubie(
                        (x * 2, y * 2, z * 2),
                        dim=3,
                        side=cubie_side,
                        colors=self.face_colors,
                    )
                    cubie.shift(np.array([x - offset, y - offset, z - offset]) * cubie_side)
                    self.cubies[x, y, z] = cubie
                    self.add(cubie)

    def layer(self, face: str) -> list[Cubie]:
        """The four cubies currently forming one face layer."""
        axis, coordinate = _FACE_LAYERS[face.upper()]
        return [
            self.cubies[index]
            for index in np.ndindex(self.cubies.shape)
            if index[axis] == coordinate
        ]

    get_layer = layer

    def apply_move(self, move: str) -> "RubiksCube2x2":
        """Update the logical cubie array after ``CubeMove`` rotates a layer."""
        face, turns = parse_move(move)
        axis = FACE_NORMALS[face]
        rotation = rotation_matrix(-turns * PI / 2, axis)
        center = (self.order - 1) / 2.0

        new_cubies = self.cubies.copy()
        for index in np.ndindex(self.cubies.shape):
            if not self._in_layer(face, index):
                continue
            relative = np.array(index, dtype=float) - center
            new_index = np.rint(rotation @ relative + center).astype(int)
            new_cubies[tuple(new_index)] = self.cubies[index]
        self.cubies = new_cubies
        return self

    def _in_layer(self, face: str, index: tuple[int, int, int]) -> bool:
        axis, coordinate = _FACE_LAYERS[face]
        return index[axis] == coordinate
