"""Arrow indicators anchored to cubies in true 3D.

The old approach projected cubie centers into screen coordinates, built HUD
arrows there, and inverse-projected them back - and the tips never quite
landed on the modules. These helpers instead build the arrows directly in
world space, in a plane that (a) passes through the actual 3D anchor points
and (b) faces the camera as much as possible. The tips therefore sit exactly
on the sticker centers, no manual nudging needed, and the arrows keep
tracking the cube if it moves.

* :func:`swap_arrows` - two cycling curved arrows (or one double arrow)
  between two cubies, for "交换这两个模块".
* :func:`twist_arrow` - a circular arrow around a cubie's own outward axis,
  for "这个角块原地旋转".
* :func:`flip_arrows` - curved arrow(s) hopping over an edge cubie's ridge
  between its two stickers, for "这个棱块自己翻面" (superflip-style).

Occlusion note: the Cairo renderer draws whole mobjects in z_index order, so
an arrow is either entirely in front of the cube (default, ``z_index=20``)
or entirely behind it - partial occlusion of a single arrow is not possible.
"""

from __future__ import annotations

import numpy as np
from manim import OUT, RIGHT, TAU, UP, Arc, ArcBetweenPoints, VGroup

from .cube_utils import normalize

#: Default colors for the two swap arrows (magenta / teal, the lesson pair).
SWAP_COLORS = ("#C23A82", "#36B8A6")
ARROW_SHADOW_COLOR = "#232323"
ARROW_Z_INDEX = 20.0


def _camera_axes(camera) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(right, up, toward-camera) unit vectors of the current view."""
    if camera is not None and hasattr(camera, "get_rotation_matrix"):
        rot = camera.get_rotation_matrix()
        return rot[0], rot[1], rot[2]
    return np.array(RIGHT, float), np.array(UP, float), np.array(OUT, float)


def _screen_perpendicular(direction: np.ndarray, camera) -> np.ndarray:
    """Unit vector perpendicular to ``direction`` lying in the camera plane."""
    _, up, out = _camera_axes(camera)
    v = np.cross(out, direction)
    if np.linalg.norm(v) < 1e-6:  # direction points straight at the camera
        v = up - np.dot(up, direction) * direction
    return normalize(v)


def _embed(mobject, u: np.ndarray, v: np.ndarray, origin: np.ndarray):
    """Map a mobject built in the local xy-plane onto the plane (u, v)."""
    matrix = np.column_stack([u, v, np.cross(u, v)])
    mobject.apply_matrix(matrix)
    mobject.shift(origin)
    return mobject


def _with_shadow(front, camera, *, offset: float = 0.05, extra_width: float = 3.0) -> VGroup:
    """Pair ``front`` with a dark offset copy, lesson-style: (shadow, front)."""
    right, up, _ = _camera_axes(camera)
    shadow = front.copy().set_color(ARROW_SHADOW_COLOR)
    shadow.set_stroke(ARROW_SHADOW_COLOR, width=front.get_stroke_width() + extra_width)
    shadow.shift(offset * right - 1.2 * offset * up)
    return VGroup(shadow, front)


def module_center(cubie) -> np.ndarray:
    """Where the eye reads the module: mean of its visible sticker centers."""
    return cubie.visible_center()


def _tip_size(chord: float, tip_length: float | None) -> float:
    """Arrow tip size: proportional to the distance, clamped to sane bounds."""
    if tip_length is not None:
        return tip_length
    return float(np.clip(0.22 * chord, 0.10, 0.32))


def _arc_arrow(
    start: np.ndarray,
    end: np.ndarray,
    *,
    angle: float,
    color: str,
    stroke_width: float,
    tip_length: float | None = None,
    double: bool = False,
) -> ArcBetweenPoints:
    """A curved arrow with a tip size that suits the chord length."""
    arc = ArcBetweenPoints(start, end, angle=angle)
    arc.set_stroke(color, width=stroke_width)
    arc.set_color(color)
    tip = _tip_size(float(np.linalg.norm(end - start)), tip_length)
    arc.add_tip(tip_length=tip, tip_width=tip)
    if double:
        arc.add_tip(tip_length=tip, tip_width=tip, at_start=True)
    return arc


def swap_arrows(
    cube,
    cubie_a,
    cubie_b,
    *,
    camera=None,
    style: str = "pair",
    colors=SWAP_COLORS,
    angle: float = 0.72,
    buff: float = 0.0,
    stroke_width: float = 6.0,
    tip_length: float | None = None,
    shadow: bool = True,
    z_index: float = ARROW_Z_INDEX,
) -> VGroup:
    """Curved arrows between two cubies, anchored to their true 3D centers.

    ``style="pair"`` gives two cycling arrows (the lesson look); each entry
    of the returned VGroup is a ``(shadow, front)`` pair, so scenes can play
    ``Create(arrow[0]), Create(arrow[1])`` per arrow. ``style="double"``
    gives a single double-headed arrow (still wrapped in one pair).

    ``buff`` shortens the arrows from each end (world units) if you do not
    want the tips to touch the sticker centers exactly.
    """
    c1 = module_center(cubie_a)
    c2 = module_center(cubie_b)
    u = normalize(c2 - c1)
    v = _screen_perpendicular(u, camera)
    mid = (c1 + c2) / 2
    half = np.linalg.norm(c2 - c1) / 2 - buff
    a_local = np.array([-half, 0.0, 0.0])
    b_local = np.array([half, 0.0, 0.0])

    common = dict(stroke_width=stroke_width, tip_length=tip_length)
    if style == "double":
        fronts = [
            _arc_arrow(a_local, b_local, angle=-angle, color=colors[0], double=True, **common)
        ]
    elif style == "pair":
        fronts = [
            _arc_arrow(a_local, b_local, angle=-angle, color=colors[0], **common),
            _arc_arrow(b_local, a_local, angle=-angle, color=colors[1], **common),
        ]
    else:
        raise ValueError(f"style must be 'pair' or 'double', got {style!r}")

    arrows = VGroup()
    for front in fronts:
        pair = _with_shadow(front, camera) if shadow else VGroup(front)
        arrows.add(pair)
    _embed(arrows, u, v, mid)
    arrows.set_z_index(z_index)
    return arrows


def twist_arrow(
    cube,
    cubie,
    *,
    camera=None,
    angle: float = 0.68 * TAU,
    clockwise: bool = False,
    radius: float | None = None,
    lift: float | None = None,
    color: str = "#F3D34A",
    stroke_width: float = 5.0,
    tip_length: float = 0.22,
    shadow: bool = True,
    z_index: float = ARROW_Z_INDEX,
) -> VGroup:
    """A circular arrow around a cubie's own outward axis.

    Use it to say "this corner twists in place". The axis is the cubie's
    current radial direction (corner diagonal / edge diagonal / face normal),
    and the ring floats just outside the cubie (``lift`` along the axis).
    ``clockwise`` is judged looking at the cubie from outside the cube.
    """
    axis = normalize(cubie.get_center() - cube.get_cube_center())
    size = cube.current_cubie_size()
    if radius is None:
        radius = 0.72 * size
    if lift is None:
        lift = 0.62 * size

    arc = Arc(radius=radius, start_angle=0.15 * TAU, angle=(-angle if clockwise else angle))
    arc.set_stroke(color, width=stroke_width)
    arc.set_color(color)
    arc.add_tip(tip_length=tip_length, tip_width=tip_length)

    # Basis (u, v, axis): the local xy-plane becomes the plane perpendicular
    # to the cubie's outward axis. Anchor u to the camera so the arc's gap
    # faces a consistent screen direction.
    u = _screen_perpendicular(axis, camera)
    v = np.cross(axis, u)
    ring = _with_shadow(arc, camera, offset=0.04) if shadow else VGroup(arc)
    _embed(ring, u, v, cubie.get_center() + axis * lift)
    ring.set_z_index(z_index)
    return ring


def flip_arrows(
    cube,
    edge_cubie,
    *,
    camera=None,
    style: str = "pair",
    colors=SWAP_COLORS,
    angle: float = 1.05 * np.pi,
    lift: float | None = None,
    stroke_width: float = 5.0,
    tip_length: float | None = None,
    shadow: bool = True,
    z_index: float = ARROW_Z_INDEX,
) -> VGroup:
    """Arrow(s) hopping over an edge cubie's ridge between its two stickers.

    Reads as "this edge flips in place" (the superflip move on one edge).
    Requires a cubie with exactly two stickers. ``style="pair"`` draws one
    arrow per direction; ``style="double"`` draws one double-headed arrow.
    """
    names = edge_cubie.sticker_names()
    if len(names) != 2:
        raise ValueError(
            f"flip_arrows() needs an edge cubie with exactly 2 stickers, got {len(names)}"
        )
    size = cube.current_cubie_size()
    if lift is None:
        lift = 0.10 * size

    center = edge_cubie.get_center()
    anchors = []
    for name in names:
        face = edge_cubie.get_face(name)
        outward = normalize(face.get_center() - center)
        anchors.append(face.get_center() + outward * lift)
    a, b = anchors
    ridge_out = normalize(sum(normalize(p - center) for p in (a, b)))

    u = normalize(b - a)
    v = normalize(ridge_out - np.dot(ridge_out, u) * u)
    mid = (a + b) / 2
    half = np.linalg.norm(b - a) / 2
    a_local = np.array([-half, 0.0, 0.0])
    b_local = np.array([half, 0.0, 0.0])

    # Negative angle bulges toward local +y, i.e. outward over the ridge.
    common = dict(stroke_width=stroke_width, tip_length=tip_length)
    if style == "double":
        fronts = [
            _arc_arrow(a_local, b_local, angle=-angle, color=colors[0], double=True, **common)
        ]
    elif style == "pair":
        fronts = [_arc_arrow(a_local, b_local, angle=-angle, color=colors[0], **common)]
        if len(colors) > 1:
            fronts.append(_arc_arrow(b_local, a_local, angle=angle, color=colors[1], **common))
    else:
        raise ValueError(f"style must be 'pair' or 'double', got {style!r}")

    arrows = VGroup()
    for front in fronts:
        pair = _with_shadow(front, camera, offset=0.035) if shadow else VGroup(front)
        arrows.add(pair)
    _embed(arrows, u, v, mid)
    arrows.set_z_index(z_index)
    return arrows
