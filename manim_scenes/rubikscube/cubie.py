"""A single cubie: a small cube made of six colored square faces."""

from __future__ import annotations

import numpy as np
from manim import ORIGIN, UL, RoundedRectangle, Square, VGroup, VMobject

from .cube_utils import FACE_NORMALS, get_faces_of_cubie, normalize, plane_basis
from .style import CubeStyle, resolve_style

INNER_COLOR = "#1E1E1E"

# How far (as a fraction of the cubie side) an inset sticker floats above its
# plastic plate. Big enough for a strict depth sort, invisible to the eye.
_STICKER_LIFT = 0.01


class CubieFace(VMobject):
    """One square face of a cubie (a sticker or an inner plastic face).

    The face remembers the fill/stroke it was born with (``base_fill`` /
    ``base_stroke``), so highlight animations can always be undone with
    :meth:`RubiksCube.reset_look` without tracking colors by hand.
    """

    def __init__(
        self,
        normal: np.ndarray,
        center: np.ndarray,
        side: float,
        color: str,
        *,
        corner_radius: float = 0.0,
        seam_color: str = INNER_COLOR,
        seam_width: float = 1.5,
        shade_in_3d: bool = False,
        sheen: float = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if corner_radius > 0:
            template = RoundedRectangle(width=side, height=side, corner_radius=corner_radius * side)
        else:
            template = Square(side_length=side)
        self.set_points(template.points)
        u, v, n = plane_basis(normal)
        self.apply_matrix(np.column_stack([u, v, n]))
        self.shift(np.asarray(center, dtype=float))

        self.set_fill(color, opacity=1.0)
        self.set_stroke(seam_color, width=seam_width)
        if shade_in_3d:
            self.set_shade_in_3d(True)
        if sheen:
            self.set_sheen(sheen, direction=UL)

        self.normal = normalize(normal)
        self.base_fill = color
        self.base_stroke = (seam_color, seam_width)

    def set_base_fill(self, color) -> "CubieFace":
        """Recolor the face and make ``color`` the new resting color."""
        self.set_fill(color, opacity=1.0)
        self.base_fill = color
        return self


class Cubie(VGroup):
    """One small cube of an NxNxN Rubik's cube.

    ``self.faces`` maps the face letter (in the *solved* orientation) to the
    visible colored face, so scenes can do
    ``cube.cubies[0, 1, 1].get_face("F")`` to grab a sticker. With an inset
    (realistic) style, ``self.plates`` additionally holds the plastic plates
    behind each sticker.

    .. note::
       ``Mobject`` already uses ``self.dim`` for the spatial dimension of its
       points (always 3), so the cube order must not be stored there. As in
       the original 2x2 code, ``self.indices`` is therefore kept on the
       0/1/2 kociemba grid (a 2x2 cubie at grid (1, 0, 1) stores indices
       (2, 0, 2)), which keeps ``get_faces_of_cubie(cubie.indices)`` working
       for old scene code. The raw grid position lives in ``self.grid``.
    """

    def __init__(
        self,
        indices: tuple[int, int, int],
        dim: int = 3,
        side: float = 1.0,
        colors: dict[str, str] | None = None,
        style: CubeStyle | str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        style = resolve_style(style)
        if colors is not None:
            style = style.with_colors(colors)
        self.style = style
        self.grid = tuple(indices)
        # Scale indices onto the {0, 1, 2} grid so legacy helpers that assume
        # dim=3 (including Mobject.dim) keep working; see class docstring.
        scale = 2 // (dim - 1) if dim > 1 else 0
        self.indices = tuple(i * scale for i in self.grid)
        self.side = side
        self.faces: dict[str, CubieFace] = {}
        self.plates: dict[str, CubieFace] = {}

        self._sticker_names = get_faces_of_cubie(self.grid, dim)
        outer = set(self._sticker_names)
        for face, normal in FACE_NORMALS.items():
            center = normal * side / 2.0
            common = dict(
                seam_color=style.seam_color,
                seam_width=style.seam_width,
                shade_in_3d=style.shade_in_3d,
            )
            if face not in outer:
                inner = CubieFace(normal, center, side, style.inner_color, **common)
                self.faces[face] = inner
                self.add(inner)
                continue

            color = style.face_colors[face]
            if style.sticker_inset > 0:
                plate = CubieFace(normal, center, side, style.inner_color, **common)
                sticker = CubieFace(
                    normal,
                    center + normal * (side * _STICKER_LIFT),
                    side * (1 - 2 * style.sticker_inset),
                    color,
                    corner_radius=style.corner_radius,
                    seam_color=color,
                    seam_width=0.0,
                    shade_in_3d=style.shade_in_3d,
                    sheen=style.sheen,
                )
                self.plates[face] = plate
                self.faces[face] = sticker
                self.add(plate, sticker)
            else:
                sticker = CubieFace(
                    normal,
                    center,
                    side,
                    color,
                    corner_radius=style.corner_radius,
                    sheen=style.sheen,
                    **common,
                )
                self.faces[face] = sticker
                self.add(sticker)
        self.move_to(ORIGIN)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------
    def get_face(self, face: str) -> CubieFace:
        return self.faces[face.upper()]

    def sticker_names(self) -> list[str]:
        """Face letters (solved orientation) of this cubie's visible stickers."""
        return list(self._sticker_names)

    def stickers(self) -> list[CubieFace]:
        """The visible colored faces, in ``sticker_names()`` order."""
        return [self.faces[name] for name in self.sticker_names()]

    def visible_center(self) -> np.ndarray:
        """Mean of the visible sticker centers, in current world coordinates.

        This is where the eye reads "the module", so arrows should aim here
        rather than at the cubie's core.
        """
        points = [face.get_center() for face in self.stickers()]
        return sum(points) / len(points)
