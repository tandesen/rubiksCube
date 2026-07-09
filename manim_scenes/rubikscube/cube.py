"""The full Rubik's cube mobject."""

from __future__ import annotations

import numpy as np
from manim import PI, VGroup
from manim.utils.space_ops import rotation_matrix

from .cube_utils import FACE_COLORS, FACE_NORMALS, FACE_ORDER, parse_move
from .cubie import Cubie

# For each face: the numpy index of its slab inside ``self.cubies``.
_FACE_SLICES = {
    "F": (0, slice(None), slice(None)),
    "B": (2, slice(None), slice(None)),
    "R": (slice(None), 0, slice(None)),
    "L": (slice(None), 2, slice(None)),
    "D": (slice(None), slice(None), 0),
    "U": (slice(None), slice(None), 2),
}


def _facelet_indices(face: str, row: int, col: int) -> tuple[int, int, int]:
    """Kociemba facelet grid position -> cubie array index.

    ``row``/``col`` follow the kociemba convention: each face is read row by
    row, left to right, while looking straight at that face (U is viewed with
    B at the top, D is viewed with F at the top).
    """
    r, c = row, col
    if face == "U":
        return (2 - r, 2 - c, 2)
    if face == "R":
        return (c, 0, 2 - r)
    if face == "F":
        return (0, 2 - c, 2 - r)
    if face == "D":
        return (r, 2 - c, 0)
    if face == "L":
        return (2 - c, 2, 2 - r)
    if face == "B":
        return (2, c, 2 - r)
    raise ValueError(f"Unknown face {face!r}")


class RubiksCube(VGroup):
    """3x3x3 Rubik's cube built from 27 :class:`Cubie` mobjects.

    Parameters
    ----------
    colors
        Face colors in kociemba order ``[Up, Right, Front, Down, Left, Back]``.
    cubie_side
        Edge length of a single cubie (whole cube is three times as wide).
    """

    def __init__(self, dim: int = 3, colors: list[str] | None = None, cubie_side: float = 1.0, **kwargs) -> None:
        if dim != 3:
            raise NotImplementedError("Only the classic 3x3x3 cube is supported")
        super().__init__(**kwargs)
        self.dim = dim
        self.cubie_side = cubie_side
        if colors is None:
            self.face_colors = dict(FACE_COLORS)
        else:
            if len(colors) != 6:
                raise ValueError("colors must contain six entries: [U, R, F, D, L, B]")
            self.face_colors = dict(zip(FACE_ORDER, colors))

        self.cubies = np.empty((dim, dim, dim), dtype=object)
        offset = (dim - 1) / 2.0
        for x in range(dim):
            for y in range(dim):
                for z in range(dim):
                    cubie = Cubie((x, y, z), dim=dim, side=cubie_side, colors=self.face_colors)
                    cubie.shift(np.array([x - offset, y - offset, z - offset]) * cubie_side)
                    self.cubies[x, y, z] = cubie
                    self.add(cubie)

        # Solved-state facelet string, updated by set_state().
        self.state = "".join(f * 9 for f in FACE_ORDER)

    # ------------------------------------------------------------------
    # State handling
    # ------------------------------------------------------------------
    def set_state(self, state: str) -> "RubiksCube":
        """Recolor the stickers to show a kociemba facelet string.

        ``state`` is 54 characters, faces in URFDLB order, each face read row
        by row. Cubie *positions* are untouched; only sticker colors change.
        """
        state = state.strip()
        if len(state) != 54 or any(ch not in FACE_ORDER for ch in state):
            raise ValueError("state must be 54 characters using only URFDLB")
        i = 0
        for face in FACE_ORDER:
            for row in range(3):
                for col in range(3):
                    color = self.face_colors[state[i]]
                    cubie = self.cubies[_facelet_indices(face, row, col)]
                    cubie.get_face(face).set_fill(color, opacity=1.0)
                    i += 1
        self.state = state
        return self

    # ------------------------------------------------------------------
    # Layers and moves
    # ------------------------------------------------------------------
    def layer(self, face: str) -> list[Cubie]:
        """The nine cubies currently forming ``face``'s slab."""
        return list(self.cubies[_FACE_SLICES[face.upper()]].flatten())

    # Backwards-compatible alias used by some older scene code.
    get_layer = layer

    def apply_move(self, move: str) -> "RubiksCube":
        """Update the logical cubie array after a face turn.

        The visual rotation is done by :class:`~.cube_animations.CubeMove`;
        this only permutes ``self.cubies`` so that subsequent ``layer()`` /
        move calls keep matching the geometry.
        """
        face, turns = parse_move(move)
        axis = FACE_NORMALS[face]
        rot = rotation_matrix(-turns * PI / 2, axis)
        center = (self.dim - 1) / 2.0

        new_cubies = self.cubies.copy()
        slab = np.argwhere(np.ones((self.dim,) * 3, dtype=bool))
        for idx in slab:
            x, y, z = idx
            if not self._in_layer(face, (x, y, z)):
                continue
            rel = np.array([x, y, z], dtype=float) - center
            new_idx = np.rint(rot @ rel + center).astype(int)
            new_cubies[tuple(new_idx)] = self.cubies[x, y, z]
        self.cubies = new_cubies
        return self

    def _in_layer(self, face: str, indices: tuple[int, int, int]) -> bool:
        sl = _FACE_SLICES[face]
        for axis_index, spec in enumerate(sl):
            if isinstance(spec, int) and indices[axis_index] != spec:
                return False
        return True