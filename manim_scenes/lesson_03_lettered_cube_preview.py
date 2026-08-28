"""Short design preview for the lettered teaching cube.

The cube uses stable cubie identities:

* centers use their standard face letters U, R, F, D, L, B;
* corners use A, C, E, G, H, I, J, K with three face suffixes;
* edges use M, N, O, P, Q, S, T, V, W, X, Y, Z with two suffixes.

Labels are real 3D children of their cubies. They therefore follow layer
turns and keep showing which physical cubie moved where.
"""

from __future__ import annotations

from pathlib import Path

from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    BOLD,
    FadeIn,
    FadeOut,
    ImageMobject,
    MathTex,
    RoundedRectangle,
    Text,
    VGroup,
    WHITE,
    config,
    rate_functions,
)

from rubikscube import CubeStyle
from rubikscube.lettered_cube import LetteredRubiksCube, LetteredRubiksCubeScene


config.frame_width = 16
config.frame_height = 9

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "backgrouds"
FONT = "PingFang SC"
CHARCOAL = "#25231F"
PAPER = "#F8F3E7"
YELLOW = "#F3D34A"
BLUE = "#2C74C9"
MAGENTA = "#C23A82"


def paper_background() -> ImageMobject:
    """Use the same kraft-paper family as the existing course scenes."""
    background = ImageMobject(str(ASSETS_DIR / "kraft_paper_002.png"))
    if background.width / background.height > config.frame_width / config.frame_height:
        background.scale_to_fit_height(config.frame_height)
    else:
        background.scale_to_fit_width(config.frame_width)
    background.move_to(ORIGIN)
    background.set_z_index(-100)
    return background


def legend_panel() -> VGroup:
    """Screen-space legend explaining the proposed production notation."""
    title = Text("编号规则", font=FONT, weight=BOLD, font_size=36, color=CHARCOAL)

    corner = MathTex(r"\mathbf{A}_0\quad\mathbf{A}_1\quad\mathbf{A}_2", font_size=38, color=BLUE)
    corner_note = Text("同一个角块 A 的三个贴面", font=FONT, font_size=25, color=CHARCOAL)
    corner_row = VGroup(corner, corner_note).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

    edge = MathTex(r"\mathbf{M}_0\quad\mathbf{M}_1", font_size=38, color=MAGENTA)
    edge_note = Text("同一个棱块 M 的两个贴面", font=FONT, font_size=25, color=CHARCOAL)
    edge_row = VGroup(edge, edge_note).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

    center = MathTex(r"\mathbf{U\ R\ F\ D\ L\ B}", font_size=38, color=YELLOW)
    center_note = Text("六个中心直接标记对应面名", font=FONT, font_size=25, color=CHARCOAL)
    center_row = VGroup(center, center_note).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

    content = VGroup(title, corner_row, edge_row, center_row).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.34,
    )
    panel = RoundedRectangle(
        width=5.4,
        height=4.5,
        corner_radius=0.12,
        fill_color=PAPER,
        fill_opacity=0.88,
        stroke_color=CHARCOAL,
        stroke_width=1.2,
    )
    content.move_to(panel).shift(LEFT * 0.05)
    return VGroup(panel, content)


class LetteredCubePreviewScene(LetteredRubiksCubeScene):
    """Eight-second visual check of the proposed lettered teaching cube."""

    default_zoom = 1.08

    def construct(self) -> None:
        background = paper_background()
        self.add_fixed_in_frame_mobjects(background)

        heading = Text("给每个 cubie 一个名字", font=FONT, weight=BOLD, font_size=46, color=CHARCOAL)
        heading.to_edge(UP, buff=0.48)
        panel = legend_panel().move_to(RIGHT * 4.75 + DOWN * 0.12)
        self.fix(heading, panel)

        style = CubeStyle.cartoon().with_(
            seam_width=1.6,
            shadow_opacity=0.13,
        )
        cube = LetteredRubiksCube(total_size=3.45, style=style)
        cube.move_to(self.screen_point(-2.65, -0.18))
        self.add_cube(cube)
        self.remove(cube)

        self.play(FadeIn(heading, shift=DOWN * 0.08), FadeIn(cube), run_time=0.8)
        self.play(FadeIn(panel, shift=LEFT * 0.16), run_time=0.65)
        self.wait(0.55)

        # Isolate A=URF long enough to inspect A_0/A_1/A_2 on one cubie.
        corner_a = cube.cubie(0, 0, 2)
        self.play(cube.pop_out(corner_a, distance=0.62), run_time=0.65)
        self.wait(0.85)
        self.play(cube.pop_in(corner_a), run_time=0.55)

        # The labels are attached to cubies, so these face turns verify that
        # they rotate with the physical pieces instead of staying on screen.
        self.turn(
            cube,
            "R U",
            run_time=0.52,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.35)

        cycle = MathTex(
            r"(A\ C\ E\ G\ H\ I\ J)",
            font_size=52,
            color=BLUE,
        )
        cycle_note = VGroup(
            Text("下一步：用 cycle notation", font=FONT, font_size=27, color=CHARCOAL),
            Text("描述 cubie 的置换", font=FONT, font_size=27, color=CHARCOAL),
        ).arrange(DOWN, buff=0.06)
        cycle_group = VGroup(cycle, cycle_note).arrange(DOWN, buff=0.16)
        cycle_group.move_to(RIGHT * 4.75 + DOWN * 2.35)
        self.fix(cycle_group)
        self.play(FadeOut(panel, shift=UP * 0.08), FadeIn(cycle_group, shift=UP * 0.12), run_time=0.65)
        self.wait(1.1)
