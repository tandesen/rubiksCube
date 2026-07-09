from __future__ import annotations

from math import cos, sin, tau

import numpy as np
from manim import *

from rubikscube import CubeMove, RubiksCube
from rubikscube.cube_utils import get_axis_from_face


config.frame_width = 16
config.frame_height = 9
config.background_color = "#F6F1E8"

FONT = "PingFang SC"
CHARCOAL = "#232323"
MUTED = "#766F66"
PAPER = "#F6F1E8"
CYAN_BG = "#36B8A6"
ORANGE_BG = "#E8873A"
MAGENTA_BG = "#C23A82"
BLUE_BG = "#2E73B8"
YELLOW = "#F3D34A"
GREEN = "#31B56A"
RED = "#D64235"
WHITE = "#F8F6EF"
BLUE = "#2C74C9"
ORANGE = "#F08A33"


def ctext(text: str, font_size: int = 44, color: str = CHARCOAL, weight: str = NORMAL) -> Text:
    return Text(text, font=FONT, font_size=font_size, color=color, weight=weight)


def label(text: str, font_size: int = 28, color: str = MUTED) -> Text:
    return ctext(text, font_size=font_size, color=color)


def paper_background(color: str = PAPER, opacity: float = 1.0) -> VGroup:
    """Flat color background with light paper grain.

    This follows the reference video's large color-field style. Increase the
    number of dots if you want a more textured TED-Ed paper look.
    """
    bg = Rectangle(width=16.5, height=9.5, fill_color=color, fill_opacity=opacity, stroke_width=0)
    texture = VGroup()
    rng = np.random.default_rng(42)
    for _ in range(70):
        x = rng.uniform(-7.8, 7.8)
        y = rng.uniform(-4.2, 4.2)
        dot = Dot([x, y, 0], radius=rng.uniform(0.01, 0.12), color=WHITE, fill_opacity=0.28)
        texture.add(dot)
    return VGroup(bg, texture)


# Colors passed to the vendored manim-rubikscube plugin, in its expected
# order: [Up, Right, Front, Down, Left, Back].
CUBE_FACE_COLORS = [WHITE, RED, GREEN, YELLOW, ORANGE, BLUE]

# A fixed, solvable scramble so the cube looks "lived in" like the reference
# video, instead of a factory-solved cube.
CUBE_SCRAMBLE_STATE = "BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR"


def cube_orientation() -> np.ndarray:
    """World rotation that shows the front, top, and right faces.
    The scenes render with the default 2D camera (orthographic top-down view
    of the xy plane), so we bake the "3D look" into the mobject itself.
    """
    r1 = rotation_matrix(-90 * DEGREES, X_AXIS)
    r2 = rotation_matrix(60 * DEGREES, Y_AXIS)
    r3 = rotation_matrix(20 * DEGREES, X_AXIS)
    return r3 @ r2 @ r1


def depth_sort_cube(body: RubiksCube, base: float = 3.0) -> None:
    """Painter's algorithm for the plugin cube inside a plain 2D Scene.
    The default Cairo camera draws mobjects in z_index order and ignores the
    z coordinate, so we map each cubie face's world z onto a fractional
    z_index. Re-run every frame while a face is turning.
    """
    faces = [face for cubie in body.cubies.flatten() for face in cubie.submobjects]
    faces.sort(key=lambda face: face.get_center()[2])
    for i, face in enumerate(faces):
        face.z_index = base + i * 1e-3


class OrientedCubeMove(CubeMove):
    """CubeMove that works on a cube with a baked-in world orientation.
    The plugin assumes the cube sits axis-aligned, so we transform the turn
    axis by the same orientation matrix, and we re-run the painter's depth
    sort every frame because the turning layer changes occlusion.
    """
    def __init__(self, cube: RubiksCube, face: str, orientation: np.ndarray, **kwargs):
        super().__init__(cube, face, **kwargs)
        self.axis = orientation @ self.axis
    
    def interpolate_mobject(self, alpha: float) -> None:
        super().interpolate_mobject(alpha)
        depth_sort_cube(self.mobject)


def rubiks_cube(scale: float = 1.0) -> VGroup:
    """Rubik's cube built from the vendored manim-rubikscube plugin.
    Returns the same wrapper structure the scenes already rely on:
    ``cube.body`` (the RubiksCube), ``cube.shadow``, and
    ``cube.body.centers`` (the three visible center stickers for blinking).
    ``cube.orientation`` feeds OrientedCubeMove for face turns.
    """
    orientation = cube_orientation()


    body = RubiksCube(colors=list(CUBE_FACE_COLORS))
    body.set_state(CUBE_SCRAMBLE_STATE)
    body.set_stroke(CHARCOAL, width=1.4)
    body.apply_matrix(orientation)
    body.scale(0.42 * scale).move_to(ORIGIN)
    depth_sort_cube(body)

    body.centers = VGroup(
        body.cubies[0, 1, 1].get_face("F"),
        body.cubies[1, 1, 2].get_face("U"),
        body.cubies[1, 0, 1].get_face("R"),
    )

    shadow = Ellipse(width=2.9 * scale, height=0.4 * scale, fill_color=BLACK, fill_opacity=0.18, stroke_width=0)
    shadow.move_to(body.get_bottom() + DOWN * 0.18)
    shadow.set_z_index(1)


    cube = VGroup(shadow, body)
    cube.shadow = shadow
    cube.body = body
    cube.orientation = orientation
    return cube


# def play_cube_move(scene: Scene, cube: VGroup, move: str, run_time: float = 0.9) -> None:
#     """Play one face turn on a rubiks_cube() wrapper, keeping depth order valid."""
#     def resort(body: RubiksCube) -> None:
#         depth_sort_cube(body)
#     cube.body.add_updater(resort)
#     scene.play(OrientedCubeMove(cube.body, move, cube.orientation), run_time=run_time)
#     cube.body.remove_updater(resort)
#     depth_sort_cube(cube.body)

def rubiks_cube_3d(scale: float = 1.0) -> VGroup:
    """Rubik's cube for a real ``ThreeDScene`` camera.

    Unlike :func:`rubiks_cube`, no orientation is baked into the mobject: the
    cube stays axis-aligned and the 3D look comes from the camera itself
    (perspective projection + phi/theta orientation). Face turns therefore use
    the plain ``CubeMove`` with canonical axes.
    """
    body = RubiksCube(colors=list(CUBE_FACE_COLORS))
    body.set_state(CUBE_SCRAMBLE_STATE)
    body.set_stroke(CHARCOAL, width=1.4)
    body.scale(0.42 * scale).move_to(ORIGIN)

    body.centers = VGroup(
        body.cubies[0, 1, 1].get_face("F"),
        body.cubies[1, 1, 2].get_face("U"),
        body.cubies[1, 0, 1].get_face("R"),
    )

    # Ground shadow: a disc in the horizontal xy-plane just below the cube;
    # the camera's viewing angle foreshortens it into an ellipse.
    shadow = Circle(radius=1.05 * scale, fill_color=BLACK, fill_opacity=0.16, stroke_width=0)
    shadow.move_to(IN * (0.63 * scale + 0.22))
    shadow.set_z_index(1)

    cube = VGroup(shadow, body)
    cube.shadow = shadow
    cube.body = body
    return cube


def depth_sort_cube_camera(body: RubiksCube, camera, base: float = 3.0) -> None:
    """Painter's algorithm for the cube under a ``ThreeDCamera``.

    The Cairo 3D camera projects points but still draws in z_index order, so
    we sort every cubie face by its depth along the camera's viewing axis
    (row 2 of the camera rotation matrix = distance toward the camera) and
    assign fractional z_index values. Re-run every frame via a scene updater
    so face turns and camera moves keep the occlusion correct.
    """
    view = camera.get_rotation_matrix()[2]
    faces = [face for cubie in body.cubies.flatten() for face in cubie.submobjects]
    faces.sort(key=lambda face: np.dot(view, face.get_center()))
    for i, face in enumerate(faces):
        face.z_index = base + i * 1e-3


def center_highlights(cube: VGroup) -> VGroup:
    """Copies of the three visible center stickers used for one blink."""
    highlights = VGroup()
    for center in cube.body.centers:
        highlight = center.copy()
        highlight.scale(1.18, about_point=center.get_center())
        highlight.set_fill(YELLOW, opacity=0.74)
        highlight.set_stroke(WHITE, width=3.5, opacity=0.96)
        highlights.add(highlight)
    highlights.set_z_index(7)
    return highlights


def number_line() -> VGroup:
    number = Text("43,252,003,274,489,856,000", font="Menlo", font_size=58, color=WHITE)
    approx = Text("≈ 4.3 × 10¹⁹", font="Menlo", font_size=42, color=YELLOW)
    caption = ctext("超过 4 千亿亿种状态", font_size=34, color=WHITE)
    group = VGroup(number, approx, caption).arrange(DOWN, buff=0.28)
    return group


def make_timeline() -> VGroup:
    line = Line(LEFT * 5.4, RIGHT * 5.4, color=WHITE, stroke_width=5)
    start = Dot(line.get_start(), radius=0.11, color=YELLOW)
    end = Dot(line.get_end(), radius=0.11, color=YELLOW)
    progress = Line(line.get_start(), line.get_start() + RIGHT * 0.108, color=YELLOW, stroke_width=10)
    start_label = label("宇宙大爆炸", 26, WHITE).next_to(start, DOWN, buff=0.25)
    end_label = label("今天", 26, WHITE).next_to(end, DOWN, buff=0.25)
    one_percent = Text("1%", font="Menlo", font_size=54, color=YELLOW).next_to(progress, UP, buff=0.35)
    note = ctext("每秒记录一个新状态，138 亿年也只看完大约 1%", 32, WHITE)
    note.next_to(line, UP, buff=0.95)
    return VGroup(line, start, end, progress, start_label, end_label, one_percent, note)


def earth_layers() -> VGroup:
    earth = Circle(radius=1.15, color=BLUE, fill_color=BLUE, fill_opacity=0.9)
    land = VGroup(
        Ellipse(width=0.92, height=0.32, color=GREEN, fill_color=GREEN, fill_opacity=0.95).move_to(earth.get_center() + LEFT * 0.32 + UP * 0.2),
        Ellipse(width=0.55, height=0.22, color=GREEN, fill_color=GREEN, fill_opacity=0.95).move_to(earth.get_center() + RIGHT * 0.46 + DOWN * 0.2),
    )
    rings = VGroup()
    for i in range(8):
        ring = Circle(radius=1.24 + i * 0.08, color=YELLOW, stroke_width=2.2, stroke_opacity=0.45)
        rings.add(ring)
    caption = ctext("1 cm² 小格子铺满地球表面：8 层还要多", 32, WHITE)
    caption.next_to(rings, DOWN, buff=0.35)
    return VGroup(rings, earth, land, caption)


def state_cloud() -> VGroup:
    group = VGroup()
    colors = [RED, YELLOW, GREEN, BLUE, ORANGE, WHITE]
    for i in range(84):
        angle = i * tau / 84
        radius = 1.1 + (i % 7) * 0.28
        x = radius * cos(angle)
        y = radius * sin(angle) * 0.65
        sq = Square(side_length=0.13, fill_color=colors[i % len(colors)], fill_opacity=1, stroke_width=0)
        sq.move_to([x, y, 0])
        group.add(sq)
    return group


def group_theory_diagram() -> VGroup:
    nodes = VGroup()
    specs = [
        ("角块排列", "S₈", LEFT * 3.9 + UP * 1.1, MAGENTA_BG),
        ("棱块排列", "S₁₂", RIGHT * 3.9 + UP * 1.1, CYAN_BG),
        ("朝向守恒", "mod 3 / mod 2", LEFT * 3.9 + DOWN * 1.25, ORANGE_BG),
        ("奇偶性", "sgn(σ)=sgn(τ)", RIGHT * 3.9 + DOWN * 1.25, BLUE_BG),
    ]
    for title, formula, pos, color in specs:
        box = RoundedRectangle(corner_radius=0.08, width=3.0, height=1.15, fill_color=color, fill_opacity=0.92, stroke_color=WHITE, stroke_width=2)
        title_mob = ctext(title, 25, WHITE)
        formula_mob = Text(formula, font="Menlo", font_size=25, color=YELLOW)
        content = VGroup(title_mob, formula_mob).arrange(DOWN, buff=0.12).move_to(box)
        nodes.add(VGroup(box, content).move_to(pos))

    center = Circle(radius=0.86, color=WHITE, stroke_width=3)
    center_label = ctext("群论", 32, WHITE).move_to(center)
    arrows = VGroup()
    for node in nodes:
        arrows.add(Line(center.get_center(), node.get_center(), color=WHITE, stroke_width=2.5).set_opacity(0.55))
    return VGroup(arrows, nodes, center, center_label)


DIMMED_STICKER = "#4A443C"


class OpeningScaleScene(ThreeDScene):
    """Opening scene with a real 3D camera.

    The cube is a true 3D mobject viewed through the ``ThreeDCamera``
    (perspective projection); all text panels and backgrounds are fixed in
    frame so they behave like a 2D overlay.
    """

    def fix(self, *mobjects: Mobject) -> None:
        """Register 2D overlay mobjects as fixed-in-frame without showing
        them yet, so they can still be animated in with FadeIn/Write."""
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.remove(*mobjects)

    def screen_point(self, x: float, y: float) -> np.ndarray:
        """World point that projects to frame coordinates (x, y).

        Uses the camera rotation matrix: rows 0/1 are the world directions of
        screen-right and screen-up. A point in the camera plane through the
        origin has zero depth, so the perspective factor is exactly 1.
        """
        rot = self.camera.get_rotation_matrix()
        return x * rot[0] + y * rot[1]

    def construct(self) -> None:
        self.set_camera_orientation(phi=65 * DEGREES, theta=-135 * DEGREES)
        self.add_fixed_in_frame_mobjects(paper_background(PAPER))

        # 0-3s: quiet opening. The cube sits at the origin; keep the first
        # visual claim clear.
        cube = rubiks_cube_3d(scale=0.95)
        depth_sort_cube_camera(cube.body, self.camera)
        self.add_updater(lambda dt: depth_sort_cube_camera(cube.body, self.camera))

        title = ctext("一个巴掌大的玩具", 48, CHARCOAL)
        subtitle = label("到底能有多少种状态？", 32, MUTED)
        intro = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.7)
        self.fix(intro)

        self.play(FadeIn(cube, shift=self.screen_point(0, 0.2)), Write(intro), run_time=2.0)
        # A gentle orbit sells the real 3D before anything else happens.
        self.move_camera(theta=-120 * DEGREES, run_time=1.6)
        self.wait(0.2)

        # Counting convention FIRST: hold the three visible center stickers
        # for three seconds while every other sticker dims for contrast.
        center_label_text = ctext("中心固定", font_size=28, color=WHITE)
        center_label_box = BackgroundRectangle(center_label_text, color=CHARCOAL, fill_opacity=0.78, buff=0.14)
        center_label = VGroup(center_label_box, center_label_text)
        center_label.set_z_index(8)
        center_label.to_edge(DOWN, buff=0.9)
        self.fix(center_label)

        centers = list(cube.body.centers)
        other_faces = [
            face
            for cubie in cube.body.cubies.flatten()
            for face in cubie.submobjects
            if face not in centers
        ]
        original_fills = [face.get_fill_color() for face in other_faces]
        rings = VGroup(*[
            center.copy().set_fill(opacity=0).set_stroke(WHITE, width=4, opacity=0.95)
            for center in centers
        ])
        rings.set_z_index(7)

        self.play(FadeOut(intro, shift=UP * 0.2), FadeIn(center_label), run_time=0.45)
        self.play(
            *[face.animate.set_fill(DIMMED_STICKER) for face in other_faces],
            FadeIn(rings),
            run_time=0.6,
        )
        self.wait(3.0)
        self.play(
            *[face.animate.set_fill(color) for face, color in zip(other_faces, original_fills)],
            FadeOut(rings),
            run_time=0.6,
        )

        # THEN a few face turns: the centers just highlighted visibly stay in
        # place while the layers spin around them.
        for move in ("R", "U'", "F"):
            self.play(CubeMove(cube.body, move), run_time=0.55)
        self.play(FadeOut(center_label), run_time=0.25)
        self.wait(0.35)

        # 6-12s: scale shock. Keep the cube small in the corner as a visual anchor.
        number_bg = paper_background(CHARCOAL)
        numbers = number_line()
        self.fix(number_bg, numbers)
        self.play(
            FadeIn(number_bg),
            cube.animate.scale(0.45).move_to(self.screen_point(-6.6, -3.1)),
            run_time=1.0,
        )
        self.play(Write(numbers[0]), run_time=1.2)
        self.play(FadeIn(numbers[1], shift=UP * 0.15), FadeIn(numbers[2], shift=UP * 0.15), run_time=0.8)
        self.wait(0.8)

        # 12-20s: time analogy. The yellow progress line intentionally moves
        # only about 1% of the full timeline.
        timeline_bg = paper_background(CYAN_BG)
        timeline = make_timeline()
        self.fix(timeline_bg, timeline)
        self.play(FadeOut(numbers), FadeIn(timeline_bg), run_time=0.7)
        self.play(Create(timeline[0]), FadeIn(timeline[1:3]), run_time=0.8)
        self.play(GrowFromPoint(timeline[3], timeline[3].get_start()), FadeIn(timeline[4:]), run_time=1.4)
        self.wait(0.8)

        # 20-30s: Earth-surface analogy. The rings are a visual shorthand for
        # repeated layers, not a literal geographic map.
        earth_bg = paper_background(BLUE_BG)
        earth = earth_layers().move_to(ORIGIN)
        self.fix(earth_bg, earth)
        self.play(FadeOut(timeline), FadeIn(earth_bg), run_time=0.5)
        self.play(FadeIn(earth[1:3], scale=0.9), run_time=0.7)
        self.play(LaggedStart(*[Create(ring) for ring in earth[0]], lag_ratio=0.08), FadeIn(earth[3]), run_time=1.6)
        self.wait(0.6)


# 2D version
# class OpeningScaleScene(Scene):
#     def construct(self) -> None:
#         # 0-3s: quiet opening. Keep the cube stable so the first visual claim is clear.
#         self.add(paper_background(PAPER))
#         title = ctext("一个巴掌大的玩具", 48, CHARCOAL)
#         subtitle = label("到底能有多少种状态？", 32, MUTED)
#         cube = rubiks_cube(scale=0.95).move_to(ORIGIN + DOWN * 0.25)
#         intro = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.7)

#         self.play(FadeIn(cube, shift=UP * 0.2), Write(intro), run_time=2.0)
#         self.wait(0.3)

#         # 3-5s: a few face turns so the cube reads as a real, working puzzle
#         # before we start talking about its states.
#         for move in ("R", "U'", "F"):
#             self.play(OrientedCubeMove(cube.body, move, cube.orientation), run_time=0.55)
#         self.wait(0.25)
#         # Counting convention: the three visible center stickers blink
#         # three times.

#         center_label_text = ctext("中心固定", font_size=28, color=WHITE)
#         center_label_box = BackgroundRectangle(center_label_text, color=CHARCOAL, fill_opacity=0.78, buff=0.14)
#         center_label = VGroup(center_label_box, center_label_text)
#         center_label.set_z_index(8)
#         center_label.next_to(cube, DOWN, buff=0.28)
#         self.play(FadeOut(intro, shift=UP * 0.2), FadeIn(center_label), run_time=0.45)
#         for _ in range(3):
#             blink = center_highlights(cube)
#             self.play(FadeIn(blink, scale=1.08), run_time=0.08)
#             self.wait(0.14)
#             self.play(FadeOut(blink), run_time=0.08)
#         self.play(FadeOut(center_label), run_time=0.25)
#         self.wait(0.35)

#         # 6-12s: scale shock. Keep the cube small in the corner as a visual anchor.
#         number_bg = paper_background(CHARCOAL)
#         numbers = number_line()
#         self.play(FadeIn(number_bg), cube.animate.scale(0.45).to_corner(DL, buff=0.65), run_time=1.0)
#         self.play(Write(numbers[0]), run_time=1.2)
#         self.play(FadeIn(numbers[1], shift=UP * 0.15), FadeIn(numbers[2], shift=UP * 0.15), run_time=0.8)
#         self.wait(0.8)

#         # 12-20s: time analogy. The yellow progress line intentionally moves
#         # only about 1% of the full timeline.
#         timeline_bg = paper_background(CYAN_BG)
#         timeline = make_timeline()
#         self.play(FadeOut(numbers), FadeIn(timeline_bg), run_time=0.7)
#         self.play(Create(timeline[0]), FadeIn(timeline[1:3]), run_time=0.8)
#         self.play(GrowFromPoint(timeline[3], timeline[3].get_start()), FadeIn(timeline[4:]), run_time=1.4)
#         self.wait(0.8)

#         # 20-30s: Earth-surface analogy. The rings are a visual shorthand for
#         # repeated layers, not a literal geographic map.
#         earth = earth_layers().move_to(ORIGIN)
#         self.play(FadeOut(timeline), FadeIn(paper_background(BLUE_BG)), run_time=0.5)
#         self.play(FadeIn(earth[1:3], scale=0.9), run_time=0.7)
#         self.play(LaggedStart(*[Create(ring) for ring in earth[0]], lag_ratio=0.08), FadeIn(earth[3]), run_time=1.6)
#         self.wait(0.6)


class GroupTheoryBridgeScene(Scene):
    def construct(self) -> None:
        self.add(paper_background(MAGENTA_BG))
        cube = rubiks_cube(scale=0.52).to_edge(LEFT, buff=0.85).shift(UP * 0.15)
        cloud = state_cloud().scale(0.9).shift(RIGHT * 1.2)
        prompt = ctext("不是手法复杂，而是状态空间太大", 38, WHITE).to_edge(UP, buff=0.65)
        self.play(FadeIn(cube), LaggedStart(*[FadeIn(s, scale=0.6) for s in cloud], lag_ratio=0.01), Write(prompt), run_time=2.5)
        self.wait(0.4)

        diagram = group_theory_diagram()
        self.play(
            cloud.animate.scale(0.25).move_to(ORIGIN).set_opacity(0.25),
            cube.animate.scale(0.7).to_corner(DL, buff=0.6),
            FadeOut(prompt, shift=UP * 0.2),
            run_time=1.1,
        )
        self.play(FadeIn(diagram[0]), FadeIn(diagram[2:]), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(node, shift=UP * 0.12) for node in diagram[1]], lag_ratio=0.15), run_time=1.6)
        self.wait(0.4)

        comm_bg = paper_background(CHARCOAL)
        formula = Text("A  B  A⁻¹  B⁻¹", font="Menlo", font_size=66, color=YELLOW)
        formula_label = ctext("交换子：先做，再撤销，只留下一个小变化", 36, WHITE)
        formula_group = VGroup(formula, formula_label).arrange(DOWN, buff=0.45)
        self.play(FadeIn(comm_bg), FadeOut(diagram), FadeOut(cloud), FadeOut(cube), run_time=0.7)
        self.play(Write(formula), FadeIn(formula_label, shift=UP * 0.2), run_time=1.3)
        self.wait(0.7)

        final_bg = paper_background(ORANGE_BG)
        final_cube = rubiks_cube(scale=0.78).shift(LEFT * 3.6)
        series = ctext("群论与魔方 01", 52, WHITE, weight=BOLD)
        episode = ctext("为什么一个玩具能装下这么多数学？", 36, WHITE)
        final_text = VGroup(series, episode).arrange(DOWN, buff=0.28).shift(RIGHT * 1.6)
        self.play(FadeIn(final_bg), FadeOut(formula_group), run_time=0.6)
        self.play(FadeIn(final_cube, shift=RIGHT * 0.3), Write(final_text), run_time=1.5)
        self.play(OrientedCubeMove(final_cube.body, "U", final_cube.orientation), run_time=0.9)
        self.play(OrientedCubeMove(final_cube.body, "R'", final_cube.orientation), run_time=0.7)
        self.wait(0.8)
