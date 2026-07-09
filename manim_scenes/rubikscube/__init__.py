"""Small Rubik's cube helpers for this Manim project.

This is a local, self-contained replacement for the unmaintained
``manim-rubikscube`` plugin, keeping only the API used by this project:
``RubiksCube``, ``CubeMove``, ``Cubie`` and a few face/axis utilities.
"""

from .cube import RubiksCube
from .cube_animations import CubeMove
from .cube_utils import (
    FACE_COLORS,
    FACE_NORMALS,
    get_axis_from_face,
    get_faces_of_cubie,
    parse_move,
)
from .cubie import Cubie, CubieFace

__all__ = [
    "Cubie",
    "CubieFace",
    "CubeMove",
    "FACE_COLORS",
    "FACE_NORMALS",
    "RubiksCube",
    "get_axis_from_face",
    "get_faces_of_cubie",
    "parse_move",
]

__version__ = "0.2.0+cubic.local"