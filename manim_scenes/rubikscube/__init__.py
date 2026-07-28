"""Rubik's cube toolkit for 德森's Manim lesson videos.

A local, self-contained replacement for the unmaintained
``manim-rubikscube`` plugin, grown into a small toolkit:

* :class:`RubiksCube` / :class:`RubiksCube2x2` - the cube mobjects
  (2x2 and 3x3), with style presets, ground shadow, pop-out cubies, and
  highlight shortcuts.
* :class:`CubeStyle` - appearance settings (palette, seams, rounded/inset
  stickers, shadow) with ``cartoon`` / ``classic`` / ``realistic`` presets.
* :class:`CubeMove` - the face-turn animation (auto-detects the cube's
  world orientation).
* :class:`RubiksCubeScene` - a ThreeDScene base class that keeps depth
  sorting (3D occlusion) correct automatically.
* :mod:`.highlights` - focus / blink / mark animations and reset.
* :mod:`.arrows` - swap / twist / flip arrows anchored in true 3D.

See README.md in this folder for a usage guide (中文).
"""

from .arrows import SWAP_COLORS, flip_arrows, module_center, swap_arrows, twist_arrow
from .cube import RubiksCube, RubiksCube2x2
from .cube_animations import CubeMove
from .cube_utils import (
    FACE_COLORS,
    FACE_NORMALS,
    FACE_ORDER,
    get_axis_from_face,
    get_faces_of_cubie,
    normalize,
    parse_move,
)
from .cubie import Cubie, CubieFace
from .depth import depth_sort_cube
from .highlights import (
    blink_cubies,
    blink_faces,
    dim_color,
    face_rings,
    focus_cubies,
    mark_cubies,
    reset_look,
)
from .scenes import RubiksCubeScene
from .style import (
    CARTOON_PALETTE,
    CLASSIC_PALETTE,
    REALISTIC_PALETTE,
    CubeStyle,
    resolve_style,
)

__all__ = [
    "CARTOON_PALETTE",
    "CLASSIC_PALETTE",
    "REALISTIC_PALETTE",
    "SWAP_COLORS",
    "FACE_COLORS",
    "FACE_NORMALS",
    "FACE_ORDER",
    "CubeMove",
    "CubeStyle",
    "Cubie",
    "CubieFace",
    "RubiksCube",
    "RubiksCube2x2",
    "RubiksCubeScene",
    "blink_cubies",
    "blink_faces",
    "depth_sort_cube",
    "dim_color",
    "face_rings",
    "flip_arrows",
    "focus_cubies",
    "get_axis_from_face",
    "get_faces_of_cubie",
    "mark_cubies",
    "module_center",
    "normalize",
    "parse_move",
    "reset_look",
    "resolve_style",
    "swap_arrows",
    "twist_arrow",
]

__version__ = "0.3.0+cubic.local"
