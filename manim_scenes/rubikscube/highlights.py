"""Highlight / dim animations for cubies.

Three highlight modes cover what the lesson videos use so far:

* :func:`focus_cubies` - keep some cubies bright, dim everything else
  (opening-scene center highlight, Superflip edge highlight).
* :func:`blink_cubies` / :func:`blink_faces` - a bling-bling Indicate pulse
  (the "上左下右" sticker flashes).
* :func:`mark_cubies` - paint chosen cubies in flat marker colors, darken
  their seams and whiten all other seams (the "交换两个方块" treatment).

All functions *return* animations; play them yourself so you keep control of
``run_time``. :func:`reset_look` undoes any combination of the above because
every face remembers its resting style (``base_fill`` / ``base_stroke``).

The same functions are also available as methods on :class:`RubiksCube`,
e.g. ``self.play(cube.focus(cubies))``.
"""

from __future__ import annotations

from manim import (
    BLACK,
    WHITE,
    YELLOW,
    AnimationGroup,
    Indicate,
    LaggedStart,
    VGroup,
    interpolate_color,
)

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def dim_color(color, amount: float = 0.58):
    """Darken ``color`` toward black; larger ``amount`` means darker."""
    return interpolate_color(color, BLACK, amount)


def _flat_cubies(cube):
    return list(cube.cubies.flatten())


def stickers_of(cubies) -> list:
    """All visible sticker faces of the given cubies."""
    return [face for cubie in cubies for face in cubie.stickers()]


def other_stickers(cube, excluded_cubies) -> list:
    """Visible sticker faces of every cubie *not* in ``excluded_cubies``."""
    excluded_ids = {id(cubie) for cubie in excluded_cubies}
    return [
        face
        for cubie in _flat_cubies(cube)
        if id(cubie) not in excluded_ids
        for face in cubie.stickers()
    ]


# ---------------------------------------------------------------------------
# Mode 1: focus (dim everything else)
# ---------------------------------------------------------------------------


def focus_cubies(
    cube,
    cubies,
    *,
    dim_amount: float = 0.58,
    seam_color=WHITE,
    seam_width: float = 3.2,
) -> AnimationGroup:
    """Dim every sticker except those of ``cubies``.

    The selected cubies optionally get a bright seam so they read as one
    family (pass ``seam_color=None`` to leave their seams untouched).
    Undo with :func:`reset_look`.
    """
    selected = stickers_of(cubies)
    rest = other_stickers(cube, cubies)
    anims = [
        face.animate.set_fill(dim_color(face.get_fill_color(), dim_amount))
        for face in rest
    ]
    if seam_color is not None:
        anims += [
            face.animate.set_stroke(seam_color, width=seam_width, opacity=0.95)
            for face in selected
        ]
    return AnimationGroup(*anims)


# ---------------------------------------------------------------------------
# Mode 2: blink (bling-bling pulse)
# ---------------------------------------------------------------------------


def blink_faces(
    faces,
    *,
    color=YELLOW,
    scale_factor: float = 1.06,
    lag_ratio: float = 0.08,
) -> LaggedStart:
    """An Indicate pulse over arbitrary sticker faces."""
    return LaggedStart(
        *[Indicate(face, color=color, scale_factor=scale_factor) for face in faces],
        lag_ratio=lag_ratio,
    )


def blink_cubies(cube, cubies, **kwargs) -> LaggedStart:
    """An Indicate pulse over all visible stickers of ``cubies``."""
    return blink_faces(stickers_of(cubies), **kwargs)


def face_rings(
    faces,
    *,
    color=WHITE,
    width: float = 2.0,
    scale: float = 1.0,
    fill_color=None,
    fill_opacity: float = 0.0,
    z_index: float = 20.0,
) -> VGroup:
    """Outline copies of sticker faces, for FadeIn/FadeOut blink overlays.

    With the defaults you get thin bright outlines (the opening scene's
    center rings). Pass ``fill_color=YELLOW, fill_opacity=0.74, scale=1.18``
    for the filled "flash" variant.
    """
    rings = VGroup()
    for face in faces:
        ring = face.copy()
        if scale != 1.0:
            ring.scale(scale, about_point=face.get_center())
        ring.set_fill(fill_color if fill_color is not None else face.get_fill_color(), opacity=fill_opacity)
        ring.set_stroke(color, width=width, opacity=0.9)
        rings.add(ring)
    rings.set_z_index(z_index)
    return rings


# ---------------------------------------------------------------------------
# Mode 3: mark (flat marker colors + seam swap)
# ---------------------------------------------------------------------------


def mark_cubies(
    cube,
    marks,
    *,
    marked_seam="#232323",
    marked_seam_width: float = 2.6,
    others_seam=WHITE,
    others_seam_width: float = 3.2,
) -> AnimationGroup:
    """Paint chosen cubies in flat colors; recolor all seams.

    ``marks`` is a list of ``(cubie, color)`` pairs (or a dict). Each marked
    cubie's stickers all take that flat color with a dark seam, while every
    other sticker keeps its color but gets a bright seam - the "交换两个方块"
    look. Undo with :func:`reset_look`.
    """
    if isinstance(marks, dict):
        marks = list(marks.items())
    marked_cubies = [cubie for cubie, _ in marks]
    anims = [
        face.animate.set_fill(color, opacity=1).set_stroke(marked_seam, width=marked_seam_width)
        for cubie, color in marks
        for face in cubie.stickers()
    ]
    if others_seam is not None:
        anims += [
            face.animate.set_stroke(others_seam, width=others_seam_width, opacity=0.95)
            for face in other_stickers(cube, marked_cubies)
        ]
    return AnimationGroup(*anims)


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def reset_look(cube) -> AnimationGroup:
    """Animate every face back to its resting fill and seam."""
    anims = []
    for cubie in _flat_cubies(cube):
        for face in list(cubie.faces.values()) + list(cubie.plates.values()):
            color, width = face.base_stroke
            anims.append(
                face.animate.set_fill(face.base_fill, opacity=1.0).set_stroke(
                    color, width=width, opacity=1.0
                )
            )
    return AnimationGroup(*anims)
