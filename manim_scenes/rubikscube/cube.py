"""The full Rubik's cube mobject (2x2x2 and 3x3x3)."""

from __future__ import annotations

import numpy as np
from manim import DOWN, IN, PI, Circle, Ellipse, VGroup
from manim.utils.space_ops import rotation_matrix

from . import highlights
from .cube_utils import FACE_NORMALS, FACE_ORDER, normalize, parse_move
from .cubie import Cubie, CubieFace
from .style import CubeStyle, resolve_style

# Axis index and layer coordinate of each face, for an NxNxN cube.
_FACE_AXIS = {"F": 0, "B": 0, "R": 1, "L": 1, "D": 2, "U": 2}
_FACE_AT_MAX = {"B", "L", "U"}


def _face_layer(face: str, dim: int) -> tuple[int, int]:
    face = face.upper()
    return _FACE_AXIS[face], (dim - 1 if face in _FACE_AT_MAX else 0)


def _facelet_indices(face: str, row: int, col: int) -> tuple[int, int, int]:
    """Kociemba facelet grid position -> cubie array index (3x3 only).

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
    """An NxNxN Rubik's cube built from :class:`Cubie` mobjects.

    Only ``dim=2`` and ``dim=3`` are exercised, but the geometry is generic.

    Parameters
    ----------
    dim
        2 for a pocket cube, 3 for the classic cube.
    colors
        Optional face colors in kociemba order ``[U, R, F, D, L, B]``;
        overrides the palette of ``style``.
    cubie_side
        Edge length of a single cubie (the whole cube is ``dim`` times as
        wide). Alternatively pass ``total_size`` for the full edge length.
    style
        A :class:`CubeStyle`, a preset name (``"cartoon"``, ``"classic"``,
        ``"realistic"``), or None for the default cartoon look.
    orientation
        Optional 3x3 rotation matrix baked into the cubies, for use with the
        plain 2D camera. Leave None (recommended) when rendering through a
        ``ThreeDScene`` camera.
    shadow
        Override the style's shadow flag. The shadow is a child of the cube
        group, so it follows the cube through ``move_to`` / ``scale``.

    The cube is a normal Manim mobject: position and size it with the usual
    chained calls, e.g. ``RubiksCube().scale(0.8).move_to(LEFT * 3)``.

    .. note::
       The cube order (2 or 3) is stored as ``self.order``, *not*
       ``self.dim``: Manim's ``Mobject`` already uses ``dim`` internally for
       the spatial dimension of its points.
    """

    def __init__(
        self,
        dim: int = 3,
        colors: list[str] | None = None,
        cubie_side: float = 1.0,
        style: CubeStyle | str | None = None,
        *,
        total_size: float | None = None,
        orientation: np.ndarray | None = None,
        shadow: bool | None = None,
        **kwargs,
    ) -> None:
        if dim not in (2, 3):
            raise NotImplementedError("Only 2x2x2 and 3x3x3 cubes are supported")
        super().__init__(**kwargs)
        style = resolve_style(style)
        if colors is not None:
            style = style.with_colors(colors)
        self.style = style
        self.face_colors = dict(style.face_colors)
        if total_size is not None:
            cubie_side = total_size / dim
        self.order = dim
        self.cubie_side = cubie_side

        self.body = VGroup()
        self.cubies = np.empty((dim, dim, dim), dtype=object)
        offset = (dim - 1) / 2.0
        for x in range(dim):
            for y in range(dim):
                for z in range(dim):
                    cubie = Cubie((x, y, z), dim=dim, side=cubie_side, style=style)
                    cubie.shift(np.array([x - offset, y - offset, z - offset]) * cubie_side)
                    self.cubies[x, y, z] = cubie
                    self.body.add(cubie)

        self.orientation = None
        if orientation is not None:
            self.orientation = np.array(orientation, dtype=float)
            self.body.apply_matrix(self.orientation)

        self.shadow = None
        want_shadow = style.shadow if shadow is None else shadow
        if want_shadow:
            self.shadow = self._make_shadow()
            self.add(self.shadow)
        self.add(self.body)

        # Solved-state facelet string (3x3 only), updated by set_state().
        self.state = "".join(f * 9 for f in FACE_ORDER) if dim == 3 else None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def _make_shadow(self):
        size = self.order * self.cubie_side
        opacity = self.style.shadow_opacity
        color = self.style.shadow_color
        if self.orientation is None:
            # True-3D usage: a disc on the floor plane below the cube; the
            # camera's viewing angle foreshortens it into an ellipse.
            shadow = Circle(radius=0.83 * size, fill_color=color, fill_opacity=opacity, stroke_width=0)
            shadow.move_to(IN * (0.5 * size + 0.17 * size))
        else:
            # Baked-orientation (2D camera) usage: a screen-space ellipse.
            shadow = Ellipse(width=1.15 * size, height=0.16 * size, fill_color=color, fill_opacity=opacity, stroke_width=0)
            shadow.move_to(self.body.get_bottom() + DOWN * 0.07 * size)
        shadow.set_z_index(1)
        return shadow

    # ------------------------------------------------------------------
    # Geometry lookups
    # ------------------------------------------------------------------
    def get_cube_center(self) -> np.ndarray:
        """Center of the cube body (ignores the shadow)."""
        return self.body.get_center()

    def current_cubie_size(self) -> float:
        """World-space distance between adjacent cubie centers right now."""
        a = self.cubies[0, 0, 0].get_center()
        b = self.cubies[1, 0, 0].get_center()
        return float(np.linalg.norm(b - a))

    def face_axis(self, face: str) -> np.ndarray:
        """Outward world-space normal of ``face``, wherever the cube is now.

        Computed from the actual cubie geometry, so it stays correct after a
        baked orientation, ``rotate()`` calls, or camera-independent moves.
        """
        layer_center = np.mean([c.get_center() for c in self.layer(face)], axis=0)
        return normalize(layer_center - self.get_cube_center())

    # ------------------------------------------------------------------
    # Cubie selectors
    # ------------------------------------------------------------------
    def cubie(self, x: int, y: int, z: int) -> Cubie:
        """The cubie currently at logical array position (x, y, z)."""
        return self.cubies[x, y, z]

    def _extreme_count(self, index: tuple[int, int, int]) -> int:
        return sum(c in (0, self.order - 1) for c in index)

    def corner_cubies(self) -> list[Cubie]:
        return [
            self.cubies[i]
            for i in np.ndindex(self.cubies.shape)
            if self._extreme_count(i) == 3
        ]

    def edge_cubies(self) -> list[Cubie]:
        """The twelve edge cubies (empty list for a 2x2)."""
        return [
            self.cubies[i]
            for i in np.ndindex(self.cubies.shape)
            if self._extreme_count(i) == 2 and self.order >= 3
        ]

    def center_cubies(self) -> list[Cubie]:
        """The six face-center cubies (empty list for a 2x2)."""
        return [
            self.cubies[i]
            for i in np.ndindex(self.cubies.shape)
            if self._extreme_count(i) == 1 and self.order >= 3
        ]

    def center_sticker(self, face: str) -> CubieFace:
        """The center sticker of ``face`` (3x3 only)."""
        if self.order != 3:
            raise ValueError("center_sticker() only makes sense on a 3x3 cube")
        axis, coord = _face_layer(face, self.order)
        index = [1, 1, 1]
        index[axis] = coord
        return self.cubies[tuple(index)].get_face(face)

    def visible_center_stickers(self, faces=("F", "U", "R")) -> VGroup:
        """Center stickers of the given faces (defaults: the hero-view trio)."""
        return VGroup(*[self.center_sticker(face) for face in faces])

    # ------------------------------------------------------------------
    # State handling
    # ------------------------------------------------------------------
    def set_state(self, state: str) -> "RubiksCube":
        """Recolor the stickers to show a kociemba facelet string (3x3 only).

        ``state`` is 54 characters, faces in URFDLB order, each face read row
        by row. Cubie *positions* are untouched; only sticker colors change,
        and they become the new resting colors for ``reset_look()``.
        """
        if self.order != 3:
            raise NotImplementedError("set_state() currently supports only 3x3 cubes")
        state = state.strip()
        if len(state) != 54 or any(ch not in FACE_ORDER for ch in state):
            raise ValueError("state must be 54 characters using only URFDLB")
        i = 0
        for face in FACE_ORDER:
            for row in range(3):
                for col in range(3):
                    color = self.face_colors[state[i]]
                    cubie = self.cubies[_facelet_indices(face, row, col)]
                    cubie.get_face(face).set_base_fill(color)
                    i += 1
        self.state = state
        return self

    # ------------------------------------------------------------------
    # Layers and moves
    # ------------------------------------------------------------------
    def layer(self, face: str) -> list[Cubie]:
        """The cubies currently forming ``face``'s slab."""
        axis, coord = _face_layer(face, self.order)
        return [
            self.cubies[index]
            for index in np.ndindex(self.cubies.shape)
            if index[axis] == coord
        ]

    # Backwards-compatible alias used by some older scene code.
    get_layer = layer

    def apply_move(self, move: str) -> "RubiksCube":
        """Update the logical cubie array after a face turn.

        The visual rotation is done by :class:`~.cube_animations.CubeMove`
        (or :meth:`do_moves`); this only permutes ``self.cubies`` so that
        subsequent ``layer()`` / move calls keep matching the geometry.
        """
        face, turns = parse_move(move)
        axis = FACE_NORMALS[face]
        rot = rotation_matrix(-turns * PI / 2, axis)
        center = (self.order - 1) / 2.0

        new_cubies = self.cubies.copy()
        for index in np.ndindex(self.cubies.shape):
            if not self._in_layer(face, index):
                continue
            rel = np.array(index, dtype=float) - center
            new_index = np.rint(rot @ rel + center).astype(int)
            new_cubies[tuple(new_index)] = self.cubies[index]
        self.cubies = new_cubies
        return self

    def _in_layer(self, face: str, index: tuple[int, int, int]) -> bool:
        axis, coord = _face_layer(face, self.order)
        return index[axis] == coord

    def do_moves(self, moves) -> "RubiksCube":
        """Apply moves instantly (no animation), e.g. to set up a scramble.

        ``moves`` is a space-separated string like ``"R U R' U'"`` or an
        iterable of move strings.
        """
        if isinstance(moves, str):
            moves = moves.split()
        for move in moves:
            face, turns = parse_move(move)
            axis = self.face_axis(face)
            VGroup(*self.layer(face)).rotate(
                -turns * PI / 2, axis=axis, about_point=self.get_cube_center()
            )
            self.apply_move(move)
        return self

    # ------------------------------------------------------------------
    # Pop a cubie out of / back into the cube
    # ------------------------------------------------------------------
    def pop_out(self, cubie: Cubie, distance: float | None = None):
        """Animation sliding ``cubie`` straight out of the cube.

        The direction is the cubie's outward radial direction in current
        world coordinates (face normal for centers, edge diagonal for edges,
        corner diagonal for corners), so it works for any cube orientation.
        Play the returned animation, then later play :meth:`pop_in`.

        Avoid turning a layer while one of its cubies is popped out.
        """
        direction = normalize(cubie.get_center() - self.get_cube_center())
        if distance is None:
            distance = 0.85 * self.current_cubie_size()
        shift = direction * distance
        cubie._pop_shift = getattr(cubie, "_pop_shift", None)
        cubie._pop_shift = shift if cubie._pop_shift is None else cubie._pop_shift + shift
        return cubie.animate.shift(shift)

    def pop_in(self, cubie: Cubie):
        """Animation sliding a popped-out cubie back into its slot."""
        shift = getattr(cubie, "_pop_shift", None)
        if shift is None:
            raise ValueError("pop_in() called on a cubie that is not popped out")
        cubie._pop_shift = None
        return cubie.animate.shift(-shift)

    # ------------------------------------------------------------------
    # Highlight shortcuts (see highlights.py for details)
    # ------------------------------------------------------------------
    def focus(self, cubies, **kwargs):
        """Dim every sticker except those of ``cubies``."""
        return highlights.focus_cubies(self, cubies, **kwargs)

    def blink(self, cubies, **kwargs):
        """Bling-bling Indicate pulse over the cubies' stickers."""
        return highlights.blink_cubies(self, cubies, **kwargs)

    def mark(self, marks, **kwargs):
        """Flat marker colors on chosen cubies + seam recoloring."""
        return highlights.mark_cubies(self, marks, **kwargs)

    def reset_look(self):
        """Animate every face back to its resting fill and seam."""
        return highlights.reset_look(self)


class RubiksCube2x2(RubiksCube):
    """A 2x2x2 pocket cube; same API as :class:`RubiksCube` with ``dim=2``."""

    def __init__(self, colors: list[str] | None = None, cubie_side: float = 1.0, **kwargs) -> None:
        super().__init__(dim=2, colors=colors, cubie_side=cubie_side, **kwargs)
