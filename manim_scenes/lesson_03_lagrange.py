"""Lesson 03: subgroups, cosets, Lagrange's theorem, and order 13.

This file follows the visual language established in lesson 02: textured
paper backgrounds, compact mathematical badges, restrained formulas, and
short Rubik's Cube demonstrations.  The scenes intentionally show only the
key mathematical steps; the full verbal explanation remains in the lesson
voice-over script.

Suggested render order::

    Lesson03OpeningScene
    SubgroupScene
    CosetScene
    CosetPartitionProofScene
    LagrangeTheoremScene
    ThistlethwaiteScene
    CyclicOrderCorollaryScene
    SevenCycleBridgeScene
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    ImageMobject,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    Transform,
    VGroup,
    Write,
    config,
    rate_functions,
)

from rubikscube import (
    BADGE_PRESETS,
    CubeMove,
    CubeStyle,
    RubiksCube,
    RubiksCubeScene,
    course_badge,
    def_heading,
    proof_heading,
    proposition_heading,
    theorem_heading,
)
from rubikscube.lettered_cube import LetteredRubiksCube, LetteredRubiksCubeScene


config.frame_width = 16
config.frame_height = 9
config.background_color = "#7D8C73"

FONT = "PingFang SC"
CHARCOAL = "#232323"
PAPER = "#F8F6EF"
YELLOW = "#F3D34A"
GREEN = "#31B56A"
ORANGE = "#F08A33"
MAGENTA = "#C23A82"
BLUE = "#2C74C9"
CYAN = "#36B8A6"
MUTED = "#716D63"

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "backgrouds"


# ---------------------------------------------------------------------------
# Shared visual helpers
# ---------------------------------------------------------------------------


def paper_background(filename: str) -> ImageMobject:
    """Cover the 16:9 frame with one of the course paper textures."""
    background = ImageMobject(str(ASSETS_DIR / filename))
    if background.width / background.height > config.frame_width / config.frame_height:
        background.scale_to_fit_height(config.frame_height)
    else:
        background.scale_to_fit_width(config.frame_width)
    background.move_to(ORIGIN)
    background.set_z_index(-100)
    return background


def ctext(text: str, font_size: int, color: str = CHARCOAL, *, bold: bool = False) -> Text:
    value = Text(
        text,
        font=FONT,
        font_size=font_size,
        color=color,
        weight="BOLD" if bold else "NORMAL",
    )
    value.set_stroke(PAPER, width=0.7, opacity=0.25, background=True)
    return value


def formula(*tex: str, font_size: int = 54, color: str = CHARCOAL) -> MathTex:
    value = MathTex(*tex, font_size=font_size, color=color)
    value.set_stroke(PAPER, width=0.7, opacity=0.22, background=True)
    return value


def lesson02_ctext(text: str, font_size: int, color: str = PAPER) -> Text:
    """Lesson 02 text styling, used only by the opening recap."""
    value = Text(text, font=FONT, font_size=font_size, color=color)
    value.set_stroke(CHARCOAL, width=1.8, opacity=0.75, background=True)
    return value


def lesson02_formula(*tex: str, font_size: int = 58, color: str = PAPER) -> MathTex:
    """Lesson 02 MathTex styling, including its dark readability stroke."""
    value = MathTex(*tex, font_size=font_size, color=color)
    value.set_stroke(CHARCOAL, width=2.2, opacity=0.8, background=True)
    return value


def move_badge(moves: str, *, font_size: int = 38) -> VGroup:
    move_tex = formula(moves, font_size=font_size, color=PAPER)
    return course_badge(move_tex, preset="move", v_padding=0.18)


def moves_to_latex(moves: str) -> str:
    """Convert executable cube notation into spaced MathTex notation."""
    parts: list[str] = []
    for token in moves.split():
        if len(token) == 2 and token[1] == "2":
            parts.append(f"{token[0]}^2")
        elif len(token) == 2 and token[1] == "'":
            parts.append(f"{token[0]}'")
        else:
            parts.append(token)
    return r"\ ".join(parts)


def move_sequence_badge(moves: str, *, font_size: int = 36) -> VGroup:
    """Match the framed move-sequence badges used in lesson 02."""
    style = BADGE_PRESETS["move"].merged(font_size=font_size)
    label = lesson02_formula(
        moves_to_latex(moves),
        font_size=style.font_size,
        color=style.text_color,
    )
    box = RoundedRectangle(
        width=max(2.4, label.width + 2 * style.h_padding),
        height=style.height,
        corner_radius=style.corner_radius,
        fill_color=style.fill_color,
        fill_opacity=style.fill_opacity,
        stroke_color=style.stroke_color,
        stroke_width=style.stroke_width,
    )
    label.move_to(box)
    return VGroup(box, label)


def math_chip(
    tex: str,
    *,
    radius: float = 0.43,
    fill_color: str = PAPER,
    text_color: str = CHARCOAL,
    stroke_color: str = CHARCOAL,
) -> VGroup:
    disk = Circle(
        radius=radius,
        fill_color=fill_color,
        fill_opacity=0.96,
        stroke_color=stroke_color,
        stroke_width=1.8,
    )
    label = formula(tex, font_size=int(34 * radius / 0.43), color=text_color)
    label.move_to(disk)
    return VGroup(disk, label)


def strike_through(mobject, *, color: str = MAGENTA, width: float = 6.0) -> Line:
    return Line(
        mobject.get_corner(LEFT + DOWN),
        mobject.get_corner(RIGHT + UP),
        color=color,
        stroke_width=width,
    )


def coset_card(label: str, members: tuple[str, ...], color: str) -> VGroup:
    """Equal-size coset tile used by the partition and Lagrange scenes."""
    box = RoundedRectangle(
        width=2.6,
        height=3.1,
        corner_radius=0.16,
        fill_color=color,
        fill_opacity=0.82,
        stroke_color=PAPER,
        stroke_width=2.0,
    )
    title = formula(label, font_size=34, color=PAPER)
    title.next_to(box.get_top(), DOWN, buff=0.27)
    dots = VGroup(
        *[
            math_chip(
                member,
                radius=0.29,
                fill_color=PAPER,
                text_color=CHARCOAL,
                stroke_color=CHARCOAL,
            )
            for member in members
        ]
    ).arrange_in_grid(rows=2, cols=2, buff=0.28)
    dots.move_to(box).shift(DOWN * 0.3)
    return VGroup(box, title, dots)


def phase_card(title: str, moves: str, goal: str, index: str, color: str) -> VGroup:
    box = RoundedRectangle(
        width=13.8,
        height=1.12,
        corner_radius=0.12,
        fill_color=PAPER,
        fill_opacity=0.87,
        stroke_color=color,
        stroke_width=2.4,
    )
    phase = ctext(title, 26, color=color, bold=True)
    generators = formula(moves, font_size=29, color=CHARCOAL)
    target = ctext(goal, 24, color=CHARCOAL)
    factor = formula(index, font_size=31, color=color)
    phase.move_to(box.get_left() + RIGHT * 1.0)
    generators.move_to(box.get_left() + RIGHT * 4.05)
    target.move_to(box.get_left() + RIGHT * 8.45)
    factor.move_to(box.get_right() + LEFT * 1.05)
    return VGroup(box, phase, generators, target, factor)


# ---------------------------------------------------------------------------
# 0. Opening hook
# ---------------------------------------------------------------------------


class Lesson03OpeningScene(RubiksCubeScene):
    """Start with the concrete claim: order 13 is impossible."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_002.png")
        background.scale(1.04)
        self.add_fixed_in_frame_mobjects(background)

        # Recap 1: reproduce the cube-group definition from lesson 02.
        cube_group_heading = def_heading("三阶魔方群", y=2.05, font_size=34, height=0.88)
        group_notation = lesson02_formula(r"(G,", r"\ast", r")", font_size=48)
        heading_content = VGroup(cube_group_heading[1], group_notation).arrange(RIGHT, buff=0.28)
        cube_group_heading[0].stretch_to_fit_width(heading_content.width + 0.86)
        heading_content.move_to(cube_group_heading[0])
        cube_group_heading = VGroup(cube_group_heading[0], heading_content)

        group_symbol = lesson02_formula(r"G:", font_size=48, color=CHARCOAL)
        set_part = VGroup(
            group_symbol,
            lesson02_formula(r"\{", font_size=48, color=CHARCOAL),
            lesson02_ctext("等价的", 34, color=CHARCOAL),
            course_badge("动作序列", preset="definition", font_size=34, height=0.82),
            lesson02_formula(r"\}", font_size=48, color=CHARCOAL),
        ).arrange(RIGHT, buff=0.22)
        operation_part = VGroup(
            lesson02_formula(r"\ast", r":", font_size=48, color=CHARCOAL),
            lesson02_ctext("自然结合两个动作序列", 34, color=CHARCOAL),
        ).arrange(RIGHT, buff=0.18)
        group_definition = VGroup(set_part, operation_part).arrange(RIGHT, buff=0.55)
        group_definition.move_to(UP * 0.55)
        composition_example = lesson02_formula(
            r"UF", r"\ast", r"LB", r"=", r"UFLB", font_size=50, color=CHARCOAL
        ).move_to(DOWN * 1.2)
        group_recap = VGroup(cube_group_heading, group_definition, composition_example)
        self.fix(group_recap)

        self.play(FadeIn(group_recap), run_time=0.55)
        self.wait(0.75)

        # Recap 2: reproduce the four order examples from lesson 02.
        row_specs = (
            ("R U R' U'", 6, 2.5),
            ("R U", 105, 1.25),
            ("U L D R", 315, 0.0),
            ("R U2 D' B D'", 1260, -1.25),
        )
        order_rows: list[tuple[RubiksCube, VGroup, MathTex]] = []
        for moves, count, y in row_specs:
            row_cube = RubiksCube(total_size=0.68)
            row_cube.do_moves(moves)
            row_cube.move_to(self.screen_point(-4.88, y))
            self.add_cube(row_cube, track=False)
            self.remove(row_cube)

            badge = move_sequence_badge(moves, font_size=36)
            badge.move_to(RIGHT * 0.05 + UP * y)
            order_label = lesson02_formula(
                rf"\operatorname{{ord}}\!\left({moves_to_latex(moves)}\right)",
                "=",
                str(count),
                font_size=34,
                color=CHARCOAL,
            )
            order_label[2].set_color(BLUE)
            order_label.move_to(RIGHT * 4.95 + UP * y)
            self.fix(badge, order_label)
            order_rows.append((row_cube, badge, order_label))

        self.play(
            FadeOut(group_recap),
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(row_cube, scale=0.92),
                        FadeIn(badge, shift=LEFT * 0.08),
                        FadeIn(order_label, shift=RIGHT * 0.08),
                    )
                    for row_cube, badge, order_label in order_rows
                ],
                lag_ratio=0.1,
            ),
            run_time=0.85,
        )
        self.wait(0.8)

        cube = RubiksCube(total_size=2.8, style=CubeStyle.cartoon())
        cube.move_to(self.screen_point(-3.8, -0.4))
        self.add_cube(cube)
        self.remove(cube)

        title = ctext("重复 13 次，第一次复原？", 56, bold=True)
        subtitle = ctext("三阶魔方里，这样的动作不存在。", 32, color=MUTED)
        heading = VGroup(title, subtitle).arrange(DOWN, buff=0.18)
        heading.to_edge(UP, buff=0.62)
        self.fix(heading)

        order_question = formula(r"\operatorname{ord}(g)", "=", "13", font_size=64)
        order_question[2].set_color(MAGENTA)
        order_box = SurroundingRectangle(
            order_question,
            color=MAGENTA,
            buff=0.35,
            corner_radius=0.14,
            stroke_width=3.0,
        )
        order_panel = VGroup(order_box, order_question).move_to(RIGHT * 3.7 + UP * 0.25)
        self.fix(order_panel)

        self.play(
            *[
                FadeOut(mobject)
                for row_cube, badge, order_label in order_rows
                for mobject in (row_cube, badge, order_label)
            ],
            FadeIn(cube),
            FadeIn(heading, shift=DOWN * 0.12),
            run_time=0.75,
        )
        self.play(FadeIn(order_panel, scale=0.92), run_time=0.65)
        self.play(CubeMove(cube, "R"), run_time=0.55)
        self.play(CubeMove(cube, "U"), run_time=0.55)
        self.wait(0.35)

        slash = strike_through(order_panel, width=7.0)
        self.fix(slash)
        self.play(Create(slash), run_time=0.5)

        route = VGroup(
            course_badge("Subgroup", preset="definition", prefix=None),
            ctext("→", 34, color=MUTED),
            course_badge("Coset", preset="definition", prefix=None),
            ctext("→", 34, color=MUTED),
            course_badge("Lagrange", preset="theorem", prefix=None),
        ).arrange(RIGHT, buff=0.28)
        route.move_to(DOWN * 2.72)
        self.fix(route)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in route], lag_ratio=0.12), run_time=1.1)
        self.wait(0.8)


# ---------------------------------------------------------------------------
# 1. Subgroup
# ---------------------------------------------------------------------------


class SubgroupScene(RubiksCubeScene):
    """Define a subgroup, then show 2Z and <R>."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_green_003.png")
        self.add_fixed_in_frame_mobjects(background)

        heading = def_heading("Subgroup  子群", label="3.1", y=3.25)
        definition = VGroup(
            ctext("设 (G, *) 是群，H 是 G 的子集。", 34),
            ctext("若 H 在同一个运算 * 下也构成群，则", 34),
            formula(r"H\leq G", font_size=58, color=BLUE),
        ).arrange(DOWN, buff=0.23)
        definition.move_to(UP * 1.55)
        self.fix(heading, definition)

        self.play(FadeIn(heading, shift=DOWN * 0.1), run_time=0.6)
        self.play(LaggedStart(*[Write(line) for line in definition], lag_ratio=0.25), run_time=1.5)
        self.wait(0.5)

        integers = tuple(str(number) for number in range(-6, 7))
        integer_chips = VGroup(
            *[
                math_chip(
                    value,
                    radius=0.33,
                    fill_color=BLUE if int(value) % 2 == 0 else PAPER,
                    text_color=PAPER if int(value) % 2 == 0 else MUTED,
                    stroke_color=BLUE if int(value) % 2 == 0 else MUTED,
                )
                for value in integers
            ]
        ).arrange(RIGHT, buff=0.16)
        integer_chips.move_to(DOWN * 0.35)
        even_label = formula(r"2\mathbb Z\leq(\mathbb Z,+)", font_size=46, color=BLUE)
        odd_label = ctext("奇数集合：0 不在其中，而且不封闭", 28, color=CHARCOAL)
        labels = VGroup(even_label, odd_label).arrange(DOWN, buff=0.2).move_to(DOWN * 1.72)
        odd_cross = strike_through(odd_label, color=MAGENTA, width=4.5)
        self.fix(integer_chips, labels, odd_cross)

        self.play(FadeIn(integer_chips, shift=UP * 0.08), run_time=0.8)
        self.play(FadeIn(even_label), run_time=0.45)
        self.play(FadeIn(odd_label), Create(odd_cross), run_time=0.55)
        self.wait(0.65)

        self.play(FadeOut(definition), FadeOut(integer_chips), FadeOut(labels), FadeOut(odd_cross), run_time=0.55)

        cube = RubiksCube(total_size=2.45)
        cube.move_to(self.screen_point(-3.9, -0.25))
        self.add_cube(cube)
        self.remove(cube)

        orbit_circle = Circle(radius=1.75, color=BLUE, stroke_width=3.0)
        orbit_circle.move_to(RIGHT * 3.6 + DOWN * 0.2)
        orbit_labels = VGroup(
            math_chip("e", fill_color=BLUE, text_color=PAPER, stroke_color=BLUE),
            math_chip("R", fill_color=PAPER, stroke_color=BLUE),
            math_chip("R^2", fill_color=PAPER, stroke_color=BLUE),
            math_chip("R^3", fill_color=PAPER, stroke_color=BLUE),
        )
        for label, angle in zip(orbit_labels, (90, 0, -90, 180), strict=True):
            radians = np.deg2rad(angle)
            label.move_to(orbit_circle.get_center() + 1.75 * np.array([np.cos(radians), np.sin(radians), 0]))
        orbit_name = formula(r"\langle R\rangle=\{e,R,R^2,R^3\}", font_size=42, color=CHARCOAL)
        orbit_name.next_to(orbit_circle, DOWN, buff=0.38)
        orbit_group = VGroup(orbit_circle, orbit_labels, orbit_name)
        self.fix(orbit_group)

        self.play(FadeIn(cube), Create(orbit_circle), FadeIn(orbit_labels[0]), run_time=0.7)
        for index in range(1, 4):
            self.play(CubeMove(cube, "R"), FadeIn(orbit_labels[index]), run_time=0.55)
        self.play(CubeMove(cube, "R"), Indicate(orbit_labels[0], color=YELLOW), run_time=0.55)
        self.play(Write(orbit_name), run_time=0.7)
        self.wait(0.8)


# ---------------------------------------------------------------------------
# 2. Cosets
# ---------------------------------------------------------------------------


class CosetScene(RubiksCubeScene):
    """Define left/right cosets and visualize residues modulo 3."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_blue_003.png")
        self.add_fixed_in_frame_mobjects(background)

        heading = def_heading("Coset  陪集", label="3.2", y=3.25)
        left_coset = formula(r"aH=\{a*h:h\in H\}", font_size=48)
        right_coset = formula(r"Ha=\{h*a:h\in H\}", font_size=48)
        definitions = VGroup(left_coset, right_coset).arrange(RIGHT, buff=1.2).move_to(UP * 1.65)
        self.fix(heading, definitions)

        self.play(FadeIn(heading, shift=DOWN * 0.1), run_time=0.6)
        self.play(Write(left_coset), run_time=0.8)
        self.play(Write(right_coset), run_time=0.8)
        self.wait(0.4)

        row_specs = (
            (r"3\mathbb Z", ("-6", "-3", "0", "3", "6"), BLUE),
            (r"1+3\mathbb Z", ("-5", "-2", "1", "4", "7"), ORANGE),
            (r"2+3\mathbb Z", ("-4", "-1", "2", "5", "8"), MAGENTA),
        )
        rows = VGroup()
        for label_tex, members, color in row_specs:
            row_label = formula(label_tex, font_size=38, color=color)
            member_group = VGroup(
                *[
                    math_chip(
                        member,
                        radius=0.31,
                        fill_color=color,
                        text_color=PAPER,
                        stroke_color=PAPER,
                    )
                    for member in members
                ]
            ).arrange(RIGHT, buff=0.22)
            row = VGroup(row_label, member_group).arrange(RIGHT, buff=0.55)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.36).move_to(DOWN * 0.38)
        partition_note = ctext("三个陪集：等大、互不重叠、覆盖所有整数", 30, color=CHARCOAL)
        partition_note.next_to(rows, DOWN, buff=0.35)
        self.fix(rows, partition_note)

        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in rows], lag_ratio=0.22), run_time=1.4)
        self.play(FadeIn(partition_note, shift=UP * 0.08), run_time=0.55)
        self.wait(0.65)

        abelian = formula(r"a+b=b+a\quad\Longrightarrow\quad a+H=H+a", font_size=42, color=BLUE)
        cube_warning = VGroup(
            formula(r"RU\neq UR", font_size=39, color=MAGENTA),
            ctext("所以一般来说", 27, color=CHARCOAL),
            formula(r"aH\neq Ha", font_size=39, color=MAGENTA),
        ).arrange(RIGHT, buff=0.28)
        comparison = VGroup(abelian, cube_warning).arrange(DOWN, buff=0.38).move_to(DOWN * 0.15)
        self.fix(comparison)
        self.play(FadeOut(rows), FadeOut(partition_note), FadeOut(definitions), FadeIn(comparison), run_time=0.65)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# 3. Why cosets partition the group
# ---------------------------------------------------------------------------


class CosetPartitionProofScene(RubiksCubeScene):
    """Keep the proof visual: intersection, equality, coverage, bijection."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_white_002.png")
        self.add_fixed_in_frame_mobjects(background)

        heading = proposition_heading("两个左陪集要么相等，要么不相交", label="3.3", y=3.25)
        proof = proof_heading(None, y=2.35)
        self.fix(heading, proof)
        self.play(FadeIn(heading, shift=DOWN * 0.1), FadeIn(proof), run_time=0.65)

        left_set = Ellipse(
            width=4.4,
            height=2.7,
            fill_color=BLUE,
            fill_opacity=0.22,
            stroke_color=BLUE,
            stroke_width=4,
        ).move_to(LEFT * 1.25 + UP * 0.25)
        right_set = Ellipse(
            width=4.4,
            height=2.7,
            fill_color=MAGENTA,
            fill_opacity=0.22,
            stroke_color=MAGENTA,
            stroke_width=4,
        ).move_to(RIGHT * 1.25 + UP * 0.25)
        left_label = formula(r"aH", font_size=42, color=BLUE).next_to(left_set, LEFT, buff=0.2)
        right_label = formula(r"bH", font_size=42, color=MAGENTA).next_to(right_set, RIGHT, buff=0.2)
        common = math_chip("x", radius=0.35, fill_color=YELLOW, stroke_color=CHARCOAL)
        common.move_to(UP * 0.25)
        diagram = VGroup(left_set, right_set, left_label, right_label, common)
        self.fix(diagram)
        self.play(Create(left_set), Create(right_set), FadeIn(left_label), FadeIn(right_label), FadeIn(common), run_time=0.9)

        steps = VGroup(
            formula(r"x=ah_1=bh_2", font_size=42),
            formula(r"a=bh_2h_1^{-1}", font_size=42),
            formula(r"ah_3=b(h_2h_1^{-1}h_3)\in bH", font_size=42),
            VGroup(
                formula(r"aH\subseteq bH", font_size=42),
                ctext("且", 28),
                formula(r"bH\subseteq aH", font_size=42),
            ).arrange(RIGHT, buff=0.25),
            formula(r"aH=bH", font_size=50, color=MAGENTA),
        ).arrange(DOWN, buff=0.23, aligned_edge=LEFT)
        steps.move_to(DOWN * 1.82)
        self.fix(steps)

        for step in steps:
            self.play(Write(step), run_time=0.55)
        self.wait(0.35)

        equal_set = left_set.copy().set_fill(MAGENTA, opacity=0.22).set_stroke(MAGENTA)
        equal_set.move_to(left_set)
        equal_label = formula(r"aH=bH", font_size=42, color=MAGENTA).move_to(left_label)
        self.fix(equal_set, equal_label)
        self.play(
            Transform(right_set, equal_set),
            FadeOut(common),
            FadeOut(right_label),
            Transform(left_label, equal_label),
            run_time=0.75,
        )
        self.wait(0.45)

        self.play(FadeOut(diagram), FadeOut(steps), run_time=0.55)

        coverage = formula(r"a=ae\in aH\qquad(\forall a\in G)", font_size=47)
        map_line = formula(r"f:H\longrightarrow aH,\qquad h\longmapsto ah", font_size=47)
        injective = formula(r"ah_1=ah_2\Longrightarrow h_1=h_2", font_size=43)
        cardinality = formula(r"|aH|=|H|", font_size=58, color=BLUE)
        conclusion = VGroup(coverage, map_line, injective, cardinality).arrange(DOWN, buff=0.37)
        conclusion.move_to(DOWN * 0.25)
        self.fix(conclusion)
        self.play(Write(coverage), run_time=0.7)
        self.play(Write(map_line), run_time=0.75)
        self.play(Write(injective), run_time=0.65)
        self.play(FadeIn(cardinality, scale=0.92), run_time=0.6)
        self.play(Indicate(cardinality, color=YELLOW, scale_factor=1.05), run_time=0.75)
        self.wait(0.7)


# ---------------------------------------------------------------------------
# 4. Lagrange's theorem
# ---------------------------------------------------------------------------


class LagrangeTheoremScene(RubiksCubeScene):
    """Assemble equal coset tiles into |G| = [G:H]|H|."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_002.png")
        self.add_fixed_in_frame_mobjects(background)

        theorem = theorem_heading("Lagrange's theorem  拉格朗日定理", label="3.4", y=3.25)
        statement = VGroup(
            ctext("设 G 是有限群，且", 32),
            formula(r"H\leq G", font_size=48),
            formula(r"\Longrightarrow", font_size=48),
            formula(r"|H|\mid |G|", font_size=52, color=MAGENTA),
        ).arrange(RIGHT, buff=0.28)
        statement.move_to(UP * 2.15)
        self.fix(theorem, statement)
        self.play(FadeIn(theorem, shift=DOWN * 0.1), run_time=0.6)
        self.play(Write(statement), run_time=0.9)

        colors = (BLUE, ORANGE, MAGENTA, GREEN, "#6957A5")
        labels = ("H", "a_2H", "a_3H", "a_4H", "a_5H")
        cards = VGroup(
            *[
                coset_card(label, ("h_1", "h_2", "h_3", "h_4"), color)
                for label, color in zip(labels, colors, strict=True)
            ]
        ).arrange(RIGHT, buff=0.12)
        cards.scale(0.83).move_to(DOWN * 0.1)
        self.fix(cards)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.12) for card in cards], lag_ratio=0.16), run_time=1.4)

        count = formula(r"|G|", "=", r"[G:H]", r"\cdot", r"|H|", font_size=58)
        count[2].set_color(MAGENTA)
        count[4].set_color(BLUE)
        count.move_to(DOWN * 2.32)
        index_note = ctext("[G:H]：H 在 G 中的 index（陪集数量）", 27, color=CHARCOAL)
        index_note.next_to(count, DOWN, buff=0.22)
        self.fix(count, index_note)
        self.play(Write(count), run_time=0.9)
        self.play(FadeIn(index_note, shift=UP * 0.06), run_time=0.5)
        self.play(Indicate(count[4], color=YELLOW), Indicate(count[0], color=YELLOW), run_time=0.75)
        self.wait(0.8)


# ---------------------------------------------------------------------------
# 5. Cyclic subgroups and the order corollary
# ---------------------------------------------------------------------------


class CyclicOrderCorollaryScene(RubiksCubeScene):
    """Connect element order to a cyclic subgroup, then rule out 13."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_green_003.png")
        self.add_fixed_in_frame_mobjects(background)

        heading = def_heading("由 x 生成的 cyclic subgroup", label="3.5", y=3.25)
        generated = formula(
            r"\langle x\rangle=\{x^k:k\in\mathbb Z\}",
            r"=\{\ldots,x^{-1},e,x,x^2,\ldots\}",
            font_size=43,
        )
        generated.arrange(DOWN, buff=0.22).move_to(UP * 1.75)
        self.fix(heading, generated)
        self.play(FadeIn(heading, shift=DOWN * 0.1), run_time=0.6)
        self.play(Write(generated[0]), run_time=0.8)
        self.play(Write(generated[1]), run_time=0.8)

        orbit = VGroup(
            *[
                math_chip(tex, fill_color=BLUE if tex == "e" else PAPER, text_color=PAPER if tex == "e" else CHARCOAL, stroke_color=BLUE)
                for tex in ("e", "x", "x^2", r"\cdots", "x^{n-1}")
            ]
        ).arrange(RIGHT, buff=0.36)
        orbit.move_to(UP * 0.22)
        self.fix(orbit)
        self.play(LaggedStart(*[FadeIn(chip, shift=RIGHT * 0.08) for chip in orbit], lag_ratio=0.18), run_time=1.2)

        equality = formula(r"\operatorname{ord}(x)=|\langle x\rangle|", font_size=54, color=BLUE)
        lagrange = formula(r"|\langle x\rangle|\mid |G|", font_size=54, color=MAGENTA)
        corollary = formula(r"\therefore\quad\operatorname{ord}(x)\mid |G|", font_size=58, color=CHARCOAL)
        conclusion = VGroup(equality, lagrange, corollary).arrange(DOWN, buff=0.25).move_to(DOWN * 1.65)
        self.fix(conclusion)
        self.play(Write(equality), run_time=0.7)
        self.play(Write(lagrange), run_time=0.7)
        self.play(FadeIn(corollary, scale=0.94), run_time=0.65)
        self.wait(0.65)

        group_order = formula(
            r"|G_{\mathrm{cube}}|=2^{27}3^{14}5^3 7^2 11",
            font_size=49,
            color=CHARCOAL,
        )
        no_thirteen = formula(r"13\nmid |G_{\mathrm{cube}}|", font_size=55, color=MAGENTA)
        yes_seven = formula(r"7\mid |G_{\mathrm{cube}}|", font_size=55, color=BLUE)
        divisibility = VGroup(group_order, no_thirteen, yes_seven).arrange(DOWN, buff=0.38).move_to(DOWN * 0.2)
        self.fix(divisibility)
        self.play(FadeOut(generated), FadeOut(orbit), FadeOut(conclusion), run_time=0.55)
        self.play(Write(group_order), run_time=0.75)
        self.play(FadeIn(no_thirteen, shift=UP * 0.08), run_time=0.55)
        self.play(FadeIn(yes_seven, shift=UP * 0.08), run_time=0.55)
        necessary = ctext("整除是必要条件，不是充分条件", 31, color=MAGENTA, bold=True)
        necessary.next_to(divisibility, DOWN, buff=0.42)
        self.fix(necessary)
        self.play(FadeIn(necessary), run_time=0.5)
        self.wait(0.9)


# ---------------------------------------------------------------------------
# 6. Thistlethwaite: a practical use for subgroups and cosets
# ---------------------------------------------------------------------------


class ThistlethwaiteScene(RubiksCubeScene):
    """Show the subgroup chain without turning the lesson into a solver tutorial."""

    def construct(self) -> None:
        background = paper_background("kraft_paper_blue_003.png")
        self.add_fixed_in_frame_mobjects(background)

        title = ctext("Thistlethwaite：把一个巨大问题拆成四个陪集搜索", 46, bold=True)
        subtitle = ctext("计算机求解思路，不是给人背诵的速拧公式", 27, color=MUTED)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.14).to_edge(UP, buff=0.42)
        self.fix(header)
        self.play(FadeIn(header, shift=DOWN * 0.1), run_time=0.7)

        chain = formula(
            r"G_0\supset G_1\supset G_2\supset G_3\supset G_4=\{e\}",
            font_size=47,
            color=CHARCOAL,
        )
        chain.move_to(UP * 2.1)
        self.fix(chain)
        self.play(Write(chain), run_time=0.85)

        phase_specs = (
            ("阶段 1", r"\langle L,R,F,B,U,D\rangle", "固定棱块朝向", r"[G_0:G_1]=2{,}048", BLUE),
            ("阶段 2", r"\langle L,R,F,B,U^2,D^2\rangle", "固定角块朝向与中层棱", r"[G_1:G_2]=1{,}082{,}565", ORANGE),
            ("阶段 3", r"\langle L,R,F^2,B^2,U^2,D^2\rangle", "进入 tetrads / slices", r"[G_2:G_3]=29{,}400", MAGENTA),
            ("阶段 4", r"\langle L^2,R^2,F^2,B^2,U^2,D^2\rangle", "只用半转完成复原", r"[G_3:G_4]=663{,}552", GREEN),
        )
        cards = VGroup(*[phase_card(*spec) for spec in phase_specs])
        cards.arrange(DOWN, buff=0.18).scale(0.86).move_to(DOWN * 0.35)
        self.fix(cards)
        self.play(LaggedStart(*[FadeIn(card, shift=LEFT * 0.15) for card in cards], lag_ratio=0.22), run_time=1.8)

        for card in cards:
            self.play(Indicate(card[0], color=YELLOW, scale_factor=1.01), run_time=0.48)

        product = formula(
            r"2{,}048\cdot1{,}082{,}565\cdot29{,}400\cdot663{,}552",
            "=",
            r"43{,}252{,}003{,}274{,}489{,}856{,}000",
            font_size=39,
            color=CHARCOAL,
        )
        product[2].set_color(MAGENTA)
        product.move_to(DOWN * 3.45)
        self.fix(product)
        self.play(Write(product), run_time=1.0)
        self.wait(0.6)

        explanation = ctext(
            "每一步只区分下一子群的陪集；进入下一层后，前一阶段的条件不会再被破坏。",
            27,
            color=CHARCOAL,
        )
        explanation.move_to(DOWN * 3.45)
        self.fix(explanation)
        self.play(FadeOut(product), FadeIn(explanation, shift=UP * 0.06), run_time=0.6)
        self.wait(0.9)


# ---------------------------------------------------------------------------
# 7. Order seven and the bridge to permutations
# ---------------------------------------------------------------------------


class SevenCycleBridgeScene(LetteredRubiksCubeScene):
    """Execute one order-seven transformation and expose its corner cycle."""

    ORDER_SEVEN_ALG = "B2 F2 U B2 F2 L2 D L2 D' R2 D R2"

    def construct(self) -> None:
        background = paper_background("kraft_paper_002.png")
        self.add_fixed_in_frame_mobjects(background)

        title = ctext("7 的确可以：一个七角块循环", 48, bold=True)
        title.to_edge(UP, buff=0.5)
        self.fix(title)
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.65)

        style = CubeStyle.cartoon().with_(seam_width=1.6, shadow_opacity=0.13)
        cube = LetteredRubiksCube(total_size=3.35, style=style)
        cube.move_to(self.screen_point(-3.2, -0.3))
        self.add_cube(cube)
        self.remove(cube)

        algorithm = move_badge(
            r"g:=B^2F^2UB^2F^2L^2DL^2D'R^2DR^2",
            font_size=27,
        )
        algorithm.move_to(RIGHT * 3.65 + UP * 0.65)
        standard_model = ctext("标准状态模型：忽略单色中心贴纸自身朝向", 25, color=MUTED)
        standard_model.next_to(algorithm, DOWN, buff=0.22)
        self.fix(algorithm, standard_model)
        self.play(FadeIn(cube), FadeIn(algorithm, shift=LEFT * 0.12), FadeIn(standard_model), run_time=0.8)

        self.turn(
            cube,
            self.ORDER_SEVEN_ALG,
            run_time=0.18,
            rate_func=rate_functions.ease_in_out_sine,
        )

        cycle = formula(r"(A\ J\ I\ H\ C\ E\ G)", font_size=58, color=BLUE)
        order = formula(r"\operatorname{ord}(g)=7", font_size=53, color=MAGENTA)
        cycle_note = ctext("固定 K 和全部棱块，不改变任何角块或棱块的朝向", 27, color=CHARCOAL)
        result = VGroup(cycle, order, cycle_note).arrange(DOWN, buff=0.28)
        result.move_to(RIGHT * 3.65 + DOWN * 1.2)
        self.fix(result)
        self.play(FadeIn(cycle, shift=UP * 0.1), run_time=0.6)
        self.play(Write(order), run_time=0.65)
        self.play(FadeIn(cycle_note), run_time=0.5)

        next_lesson = course_badge(
            "Permutation → symmetric group → commutator → 3-cycle",
            preset="proposition",
            prefix="下一集：",
            font_size=27,
        )
        next_lesson.move_to(DOWN * 3.55)
        self.fix(next_lesson)
        self.play(FadeIn(next_lesson, shift=UP * 0.1), run_time=0.7)
        self.wait(1.0)
