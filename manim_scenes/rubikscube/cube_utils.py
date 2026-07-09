"""Geometry / notation helpers shared by the Rubik's cube mobjects.

Coordinate convention (the cube's *canonical*, unrotated frame):

* array index ``(x, y, z)`` of ``RubiksCube.cubies`` maps to world position
  ``((x - 1) * side, (y - 1) * side, (z - 1) * side)`` for a 3x3x3 cube;
* ``x``: 0 = Front slab, 2 = Back slab   (F normal = -X, B normal = +X)
* ``y``: 0 = Right slab, 2 = Left slab   (R normal = -Y, L normal = +Y)
* ``z``: 0 = Down slab,  2 = Up slab     (U normal = +Z, D normal = -Z)

With this convention the scenes' ``cube_orientation()`` matrix
(Rx(-90) then Ry(60) then Rx(20)) shows the F, U and R faces to the default
2D camera, in the classic 3/4 "hero" view.
"""

from __future__ import annotations

import numpy as np

# Kociemba facelet-string face order; also the order of the ``colors``
# argument of RubiksCube: [Up, Right, Front, Down, Left, Back].
FACE_ORDER = "URFDLB"

# Standard (western / BOY) color scheme, used when no colors are supplied.
FACE_COLORS = {
    "U": "#FFFFFF",  # white
    "R": "#C41E3A",  # red
    "F": "#009E60",  # green
    "D": "#FFD500",  # yellow
    "L": "#FF5800",  # orange
    "B": "#0051BA",  # blue
}

# Outward unit normal of each face in the cube's canonical frame.
FACE_NORMALS = {
    "F": np.array([-1.0, 0.0, 0.0]),
    "B": np.array([1.0, 0.0, 0.0]),
    "R": np.array([0.0, -1.0, 0.0]),
    "L": np.array([0.0, 1.0, 0.0]),
    "U": np.array([0.0, 0.0, 1.0]),
    "D": np.array([0.0, 0.0, -1.0]),
}


def get_axis_from_face(face: str) -> np.ndarray:
    """Outward rotation axis (unit vector) for a face turn, canonical frame."""
    return FACE_NORMALS[face.upper()].copy()


def parse_move(move: str) -> tuple[str, int]:
    """Parse singmaster notation ("U", "U'", "U2", "U2'") -> (face, turns).

    ``turns`` is signed: positive = clockwise (seen from outside the face).
    """
    move = move.strip()
    if not move:
        raise ValueError("Empty move string")
    face = move[0].upper()
    if face not in FACE_NORMALS:
        raise ValueError(f"Unknown face {face!r} in move {move!r}")
    suffix = move[1:]
    turns = 1
    if suffix.replace("'", "").isdigit():
        turns = int(suffix.replace("'", ""))
    elif suffix not in ("", "'"):
        raise ValueError(f"Cannot parse move {move!r}")
    if "'" in suffix:
        turns = -turns
    return face, turns


def get_faces_of_cubie(indices: tuple[int, int, int], dim: int = 3) -> list[str]:
    """Which stickers (face letters) a cubie at array ``indices`` shows."""
    x, y, z = indices
    faces = []
    if x == 0:
        faces.append("F")
    if x == dim - 1:
        faces.append("B")
    if y == 0:
        faces.append("R")
    if y == dim - 1:
        faces.append("L")
    if z == dim - 1:
        faces.append("U")
    if z == 0:
        faces.append("D")
    return faces