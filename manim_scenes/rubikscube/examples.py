"""Demo scenes exercising every toolkit feature.

Render from the project root, e.g.::

    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py StyleTour
    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py HighlightTour
    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py PopAndArrowTour
    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py PocketCubeTour

These double as smoke tests: if they render, the public API works.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import DOWN, ORIGIN, PI, RIGHT, Create, FadeOut, Rotate, Text, config

from rubikscube import CubeMove, RubiksCube, RubiksCube2x2, RubiksCubeScene, normalize

config.background_color = "#F6F1E8"


class StyleTour(RubiksCubeScene):
    """All three CubeStyle presets on one screen: cartoon / classic / realistic."""

    def construct(self) -> None:
        # Presets: cartoon (lesson default), classic (BOY, no shadow), realistic (inset + sheen)
        specs = (
            ("cartoon", -4.2),
            ("classic", 0.0),
            ("realistic", 4.2),
        )
        for name, x in specs:
            cube = RubiksCube(style=name, total_size=1.7)
            cube.move_to(self.screen_point(x, 0.35))
            self.add_cube(cube, track=False)
            label = Text(name, font_size=28, color="#232323")
            label.move_to(RIGHT * x + DOWN * 2.4)
            self.add_fixed_in_frame_mobjects(label)
        self.wait(3)


class HighlightTour(RubiksCubeScene):
    """The three highlight modes: focus, blink, mark - then reset."""

    def construct(self) -> None:
        cube = self.add_cube(RubiksCube().scale(0.75).move_to(ORIGIN))
        self.wait(0.3)

        # Mode 1: focus on the edges, dim everything else.
        edges = cube.edge_cubies()
        self.play(cube.focus(edges), run_time=0.7)
        self.wait(0.5)
        self.play(cube.reset_look(), run_time=0.6)

        # Mode 2: bling-bling blink on the top layer.
        self.play(cube.blink(cube.layer("U")), run_time=1.0)
        self.wait(0.3)

        # Mode 3: mark two corners for a swap, with the cycling arrows.
        first = cube.cubie(0, 0, 2)
        second = cube.cubie(0, 2, 2)
        self.play(cube.mark([(first, "#C23A82"), (second, "#36B8A6")]), run_time=0.7)
        arrows = self.swap_arrows(cube, first, second)
        self.play(*[Create(part) for pair in arrows for part in pair], run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(arrows), cube.reset_look(), run_time=0.7)
        self.wait(0.4)


class PopAndArrowTour(RubiksCubeScene):
    """Pop a corner out, twist it, put it back; then flip arrows on an edge."""

    def construct(self) -> None:
        cube = self.add_cube(RubiksCube().scale(0.75).move_to(ORIGIN))
        self.wait(0.3)

        corner = cube.cubie(0, 0, 2)
        self.play(cube.pop_out(corner), run_time=0.7)
        ring = self.twist_arrow(cube, corner, clockwise=True)
        self.play(Create(ring), run_time=0.5)

        # The corner twist itself: rotate the popped cubie around its own
        # outward diagonal (this is deliberately a plain Rotate, not a class
        # method - see README).
        axis = normalize(corner.get_center() - cube.get_cube_center())
        self.play(
            Rotate(corner, angle=-2 * PI / 3, axis=axis, about_point=corner.get_center()),
            run_time=0.9,
        )
        self.play(FadeOut(ring), run_time=0.3)
        self.play(cube.pop_in(corner), run_time=0.7)
        self.wait(0.4)

        # Flip arrows on the front-top edge (superflip-style).
        edge = cube.cubie(0, 1, 2)
        flips = self.flip_arrows(cube, edge)
        self.play(*[Create(part) for pair in flips for part in pair], run_time=0.7)
        self.wait(0.8)
        self.play(FadeOut(flips), run_time=0.4)


class PocketCubeTour(RubiksCubeScene):
    """Everything works the same on the 2x2."""

    def construct(self) -> None:
        cube = self.add_cube(RubiksCube2x2().scale(0.9).move_to(ORIGIN))
        self.wait(0.3)
        self.turn(cube, "R U' F", run_time=0.6)

        first = cube.cubie(0, 0, 1)
        second = cube.cubie(0, 1, 1)
        self.play(cube.mark([(first, "#C23A82"), (second, "#36B8A6")]), run_time=0.6)
        arrows = self.swap_arrows(cube, first, second, style="double", colors=("#C23A82",))
        self.play(Create(arrows), run_time=0.7)
        self.wait(0.6)
        self.play(FadeOut(arrows), cube.reset_look(), run_time=0.6)

        corner = cube.cubie(0, 0, 1)
        self.play(cube.pop_out(corner), run_time=0.6)
        self.play(cube.pop_in(corner), run_time=0.6)
        self.wait(0.4)
