"""Reusable 26-letter teaching cube for Manim course scenes.

Usage::

    from rubikscube.lettered_cube import LetteredRubiksCube, LetteredRubiksCubeScene

    class Demo(LetteredRubiksCubeScene):
        def construct(self):
            cube = self.add_cube(LetteredRubiksCube(total_size=3.2))
            self.turn(cube, "R U R' U'")

The six center cubies use the move letters U/R/F/D/L/B. The remaining
twenty letters identify the eight corners and twelve edges. A suffix labels
the permanent sticker of a multi-face cubie, for example A_0/A_1/A_2.
"""

from __future__ import annotations

import numpy as np
from manim import MathTex, ORIGIN, VGroup

from .cube import RubiksCube
from .scenes import RubiksCubeScene


PAPER = "#F8F3E7"
CHARCOAL = "#25231F"

# Cubie IDs follow the conventional corner/edge position order. Face names
# map to the permanent suffix printed on that physical sticker.
PIECE_LABELS = {
    "A": ((0, 0, 2), {"U": 0, "R": 1, "F": 2}),  # URF
    "C": ((0, 2, 2), {"U": 0, "F": 1, "L": 2}),  # UFL
    "E": ((2, 2, 2), {"U": 0, "L": 1, "B": 2}),  # ULB
    "G": ((2, 0, 2), {"U": 0, "B": 1, "R": 2}),  # UBR
    "H": ((0, 0, 0), {"D": 0, "F": 1, "R": 2}),  # DFR
    "I": ((0, 2, 0), {"D": 0, "L": 1, "F": 2}),  # DLF
    "J": ((2, 2, 0), {"D": 0, "B": 1, "L": 2}),  # DBL
    "K": ((2, 0, 0), {"D": 0, "R": 1, "B": 2}),  # DRB
    "M": ((1, 0, 2), {"U": 0, "R": 1}),  # UR
    "N": ((0, 1, 2), {"U": 0, "F": 1}),  # UF
    "O": ((1, 2, 2), {"U": 0, "L": 1}),  # UL
    "P": ((2, 1, 2), {"U": 0, "B": 1}),  # UB
    "Q": ((1, 0, 0), {"D": 0, "R": 1}),  # DR
    "S": ((0, 1, 0), {"D": 0, "F": 1}),  # DF
    "T": ((1, 2, 0), {"D": 0, "L": 1}),  # DL
    "V": ((2, 1, 0), {"D": 0, "B": 1}),  # DB
    # Middle-slice edges use R/L=0 and F/B=1. This deliberately breaks full
    # visual symmetry so a flipped edge still has an unambiguous orientation.
    "W": ((0, 0, 1), {"F": 1, "R": 0}),  # FR
    "X": ((0, 2, 1), {"F": 1, "L": 0}),  # FL
    "Y": ((2, 2, 1), {"B": 1, "L": 0}),  # BL
    "Z": ((2, 0, 1), {"B": 1, "R": 0}),  # BR
}

CENTER_INDICES = {
    "U": (1, 1, 2),
    "R": (1, 0, 1),
    "F": (0, 1, 1),
    "D": (1, 1, 0),
    "L": (1, 2, 1),
    "B": (2, 1, 1),
}

# Face-local axes keep every label upright when looking straight at its face.
FACE_BASIS = {
    "U": (np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0])),
    "R": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
    "F": (np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0])),
    "D": (np.array([0.0, -1.0, 0.0]), np.array([-1.0, 0.0, 0.0])),
    "L": (np.array([-1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
    "B": (np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])),
}


def _fit_to_box(mobject, width: float, height: float):
    mobject.scale(min(width / mobject.width, height / mobject.height))
    return mobject


def _place_on_face(label, face, face_name: str, cubie_side: float):
    u, v = FACE_BASIS[face_name]
    normal = np.cross(u, v)
    label.move_to(ORIGIN)
    label.apply_matrix(np.column_stack([u, v, normal]))
    label.move_to(face.get_center() + normal * (0.018 * cubie_side))
    label.identity_face = face
    return label


def _text_color(face_name: str) -> str:
    return PAPER if face_name in {"U", "R", "D"} else CHARCOAL


def _facelet_label(piece: str, suffix: int, face_name: str, face, side: float):
    label = MathTex(
        rf"\mathbf{{{piece}}}_{{\!{suffix}}}",
        font_size=42,
        color=_text_color(face_name),
    )
    _fit_to_box(label, 0.54 * side, 0.38 * side)
    return _place_on_face(label, face, face_name, side)


def _center_label(face_name: str, face, side: float):
    label = MathTex(
        rf"\mathbf{{{face_name}}}",
        font_size=46,
        color=_text_color(face_name),
    )
    _fit_to_box(label, 0.38 * side, 0.42 * side)
    return _place_on_face(label, face, face_name, side)


def add_identity_labels(cube: RubiksCube) -> dict[str, VGroup]:
    """Attach all 54 permanent facelet labels to a 3x3 cube.

    The function is idempotent: if the cube is already labelled, its current
    ``identity_labels`` mapping is returned without adding a second copy.
    """
    if cube.order != 3:
        raise ValueError("The 26-letter notation is defined only for a 3x3 cube")
    existing = getattr(cube, "identity_labels", None)
    if existing is not None:
        return existing

    labels: dict[str, VGroup] = {}
    side = cube.cubie_side

    for piece, (index, suffixes) in PIECE_LABELS.items():
        cubie = cube.cubie(*index)
        piece_group = VGroup()
        for face_name, suffix in suffixes.items():
            label = _facelet_label(piece, suffix, face_name, cubie.get_face(face_name), side)
            label.is_identity_label = True
            label.identity_piece = piece
            label.identity_suffix = suffix
            cubie.add(label)
            piece_group.add(label)
        labels[piece] = piece_group

    centers = VGroup()
    for face_name, index in CENTER_INDICES.items():
        cubie = cube.cubie(*index)
        label = _center_label(face_name, cubie.get_face(face_name), side)
        label.is_identity_label = True
        label.identity_piece = face_name
        label.identity_suffix = None
        cubie.add(label)
        centers.add(label)
    labels["centers"] = centers
    cube.identity_labels = labels
    return labels


def refresh_identity_label_depth(cube: RubiksCube) -> None:
    """Draw each label just after its sticker during Cairo face turns."""
    for cubie in cube.cubies.flatten():
        for child in cubie.submobjects:
            if not getattr(child, "is_identity_label", False):
                continue
            face = getattr(child, "identity_face", None)
            z_index = face.z_index + 5e-4 if face is not None else child.z_index
            child.set_z_index(z_index, family=True)


class LetteredRubiksCube(RubiksCube):
    """A standard 3x3 :class:`RubiksCube` with the 26-letter notation."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        add_identity_labels(self)


class LetteredRubiksCubeScene(RubiksCubeScene):
    """RubiksCubeScene with the extra depth pass required by 3D labels."""

    def _sort_tracked_cubes(self, dt: float = 0.0) -> None:
        super()._sort_tracked_cubes(dt)
        for cube in self._depth_tracked:
            refresh_identity_label_depth(cube)


__all__ = [
    "CENTER_INDICES",
    "FACE_BASIS",
    "PIECE_LABELS",
    "LetteredRubiksCube",
    "LetteredRubiksCubeScene",
    "add_identity_labels",
    "refresh_identity_label_depth",
]
