"""A single cubie: a small cube made of six colored square faces."""

from __future__ import annotations

import numpy as np
from manim import ORIGIN, VGroup, VMobject

from .cube_utils import FACE_COLORS, FACE_NORMALS, get_faces_of_cubie

INNER_COLOR = "#1E1E1E"


def _square_points(normal: np.ndarray, center: np.ndarray, side: float) -> np.ndarray:
    """Corner points of a filled square lying in the plane ``normal``."""
    n = np.asarray(normal, dtype=float)
    # Build two unit vectors spanning the face plane.
    helper = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(n, helper)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    h = side / 2.0
    return np.array([
        center + h * u + h * v,
        center - h * u + h * v,
        center - h * u - h * v,
        center + h * u - h * v,
    ])


class CubieFace(VMobject):
    """One square face of a cubie (a sticker or an inner plastic face)."""

    def __init__(self, normal: np.ndarray, center: np.ndarray, side: float, color: str, **kwargs) -> None:
        super().__init__(**kwargs)
        corners = _square_points(normal, center, side)
        self.set_points_as_corners([*corners, corners[0]])
        self.set_fill(color, opacity=1.0)
        self.set_stroke(INNER_COLOR, width=1.5)


class Cubie(VGroup):
    """One of the 27 small cubes.

    ``self.faces`` maps the face letter (in the *solved* orientation) to the
    corresponding :class:`CubieFace`, so scenes can do
    ``cube.cubies[0, 1, 1].get_face("F")`` to grab a sticker.
    """

    def __init__(
        self,
        indices: tuple[int, int, int],
        dim: int = 3,
        side: float = 1.0,
        colors: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.indices = tuple(indices)
        self.dim = dim
        self.side = side
        self.faces: dict[str, CubieFace] = {}

        colors = colors or FACE_COLORS
        outer = set(get_faces_of_cubie(self.indices, dim))
        for face, normal in FACE_NORMALS.items():
            color = colors[face] if face in outer else INNER_COLOR
            sticker = CubieFace(normal, normal * side / 2.0, side, color)
            self.faces[face] = sticker
            self.add(sticker)
        self.move_to(ORIGIN)

    def get_face(self, face: str) -> CubieFace:
        return self.faces[face.upper()]