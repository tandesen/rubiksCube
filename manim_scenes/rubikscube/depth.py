"""Painter's-algorithm depth sorting for the cube.

Manim's Cairo renderer projects 3D points onto the screen but draws mobjects
in ``z_index`` order, ignoring actual depth. Without help, the black inside
of the cube can be drawn on top of the outside stickers while a layer turns.

:func:`depth_sort_cube` maps each face's distance from the camera onto a
fractional ``z_index``. Re-run it every frame while anything moves - either
via :class:`~.scenes.RubiksCubeScene` (which does it for you), or with your
own scene updater::

    self.add_updater(lambda dt: depth_sort_cube(cube, self.camera))
"""

from __future__ import annotations

import numpy as np

#: Default z_index floor for cube faces. Backgrounds should stay below this,
#: overlays (arrows, badges) above ``base + 2``.
BASE_Z = 3.0


def depth_sort_cube(cube, camera=None, base: float = BASE_Z) -> None:
    """Assign fractional z_index values so nearer faces draw last.

    ``cube`` is a :class:`~.cube.RubiksCube` (or anything with a ``cubies``
    array of :class:`~.cubie.Cubie`). With a ``ThreeDCamera`` pass ``camera``
    so depth follows the camera's viewing axis; with the plain 2D camera
    (baked-orientation cubes) leave it None and world z is used.
    """
    faces = [face for cubie in cube.cubies.flatten() for face in cubie.submobjects]
    if camera is not None and hasattr(camera, "get_rotation_matrix"):
        view = camera.get_rotation_matrix()[2]
        faces.sort(key=lambda face: np.dot(view, face.get_center()))
    else:
        faces.sort(key=lambda face: face.get_center()[2])
    for i, face in enumerate(faces):
        face.z_index = base + i * 1e-3
    shadow = getattr(cube, "shadow", None)
    if shadow is not None:
        shadow.z_index = base - 2
