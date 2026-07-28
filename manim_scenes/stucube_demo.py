"""Minimal dark-style Rubik's Cube demo for STUCUBE.

Render a quick preview from the project root with:

    .venv/bin/manim -ql --media_dir media manim_scenes/stucube_demo.py STUCubeDemoScene

The constants near the top are the main visual controls.  The scene uses a
real ``ThreeDScene`` camera rather than baking a 3D angle into a 2D object.
"""

from __future__ import annotations

import numpy as np
from manim import *

from rubikscube import CubeMove, RubiksCube
from rubikscube.cube_utils import get_faces_of_cubie


# ---------------------------------------------------------------------------
# Easy-to-adjust visual controls
# ---------------------------------------------------------------------------

config.frame_width = 16
config.frame_height = 9

# Scene background.  Raising these RGB values makes the background softer;
# lowering them moves it closer to pure black.
CHARCOAL = "#17191C"
config.background_color = CHARCOAL

# Dark plastic and seams make the separate cubies read more like a physical
# speedcube.  OUTLINE_WIDTH controls the apparent size of those seams.
PLASTIC = "#090B0D"
OUTLINE = "#050607"
OUTLINE_WIDTH = 2.8

# Slightly muted sticker colors suit STUCUBE's darker visual language better
# than the bright, illustrative palette used by lesson_01_opening.py.
# RubiksCube expects this order: Up, Right, Front, Down, Left, Back.
STICKER_COLORS = [
    "#E8E9E4",  # U: off-white
    "#B92F3D",  # R: red
    "#168A57",  # F: green
    "#E7C43A",  # D: yellow
    "#DE702B",  # L: orange
    "#315FA9",  # B: blue
]

CUBE_SCALE = 0.78
TURN_TIME = 0.72
MOVES = ("R", "U'", "F2")


def depth_sort_cube(body: RubiksCube, camera, base: float = 3.0) -> None:
    """Draw rear faces first and front faces last for correct occlusion.

    Manim's Cairo renderer projects 3D points onto the screen but still uses
    ``z_index`` to decide draw order.  Sorting every frame prevents the rear
    stickers from appearing on top while a layer is turning.
    """
    camera_depth_axis = camera.get_rotation_matrix()[2]
    faces = [
        face
        for cubie in body.cubies.flatten()
        for face in cubie.submobjects
    ]
    faces.sort(key=lambda face: np.dot(camera_depth_axis, face.get_center()))
    for index, face in enumerate(faces):
        face.z_index = base + index * 1e-3


def make_realistic_cube(scale: float = CUBE_SCALE) -> RubiksCube:
    """Create a darker cube with stronger seams, shading, and soft sheen."""
    body = RubiksCube(colors=list(STICKER_COLORS), shadow=False)

    for cubie in body.cubies.flatten():
        sticker_faces = set(get_faces_of_cubie(cubie.indices))
        for face_name, face in cubie.faces.items():
            # Faces inside the cube are plastic rather than stickers.  This is
            # especially visible for a few frames while a layer is turning.
            if face_name not in sticker_faces:
                face.set_fill(PLASTIC, opacity=1.0)

            # Wider, nearly-black outlines create the physical gaps between
            # cubies.  Reduce OUTLINE_WIDTH for a cleaner graphic appearance.
            face.set_stroke(OUTLINE, width=OUTLINE_WIDTH, opacity=1.0)

            # These two settings let the ThreeDCamera light different planes
            # differently and add a restrained highlight across each face.
            face.set_shade_in_3d(True)
            face.set_sheen(0.10, direction=UL)

    body.scale(scale).move_to(ORIGIN)
    return body


def make_ground_shadow(cube: RubiksCube) -> VGroup:
    """Build a soft fake floor shadow from several translucent circles."""
    # ``get_bottom()`` means screen/world -Y in Manim, not the lowest Z point.
    # Read the geometry directly so the shadow really sits beneath the cube.
    bottom_z = np.min(cube.get_all_points()[:, 2])
    shadow = VGroup()

    # Concentric discs approximate blur without requiring an image asset.
    # Increase opacity for a heavier, more dramatic studio-lighting look.
    for radius, opacity in ((1.38, 0.10), (1.18, 0.13), (0.98, 0.16)):
        disc = Circle(
            radius=radius,
            fill_color=BLACK,
            fill_opacity=opacity,
            stroke_width=0,
        )
        disc.move_to([0, 0, bottom_z - 0.08])
        disc.set_z_index(0)
        shadow.add(disc)

    return shadow


class STUCubeDemoScene(ThreeDScene):
    """A cube is present immediately, then performs three simple turns."""

    def construct(self) -> None:
        # phi controls how much of the top is visible; theta rotates the view
        # around the cube.  A shorter focal distance increases perspective.
        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-135 * DEGREES,
            focal_distance=12,
            zoom=1.32,
        )

        # Moving the light above and toward the camera gives the top face a
        # soft highlight while leaving side faces slightly darker.
        self.camera.light_source.move_to([-5, -5, 8])

        cube = make_realistic_cube()
        shadow = make_ground_shadow(cube)
        depth_sort_cube(cube, self.camera)

        # Keep occlusion correct throughout every layer turn.
        self.add_updater(lambda dt: depth_sort_cube(cube, self.camera))

        # Add directly: there is intentionally no FadeIn or introductory text.
        self.add(shadow, cube)
        self.wait(0.5)

        for move in MOVES:
            self.play(CubeMove(cube, move), run_time=TURN_TIME)
            self.wait(0.12)

        self.wait(0.6)
