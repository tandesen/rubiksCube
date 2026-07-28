from __future__ import annotations

from math import cos, sin, tau

import numpy as np
from manim import *

from rubikscube import CubeMove, RubiksCube
from rubikscube.cube_2x2 import RubiksCube2x2
from rubikscube.cube_utils import get_axis_from_face, get_faces_of_cubie

from pathlib import Path


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


def image_background(
    filename: str,
    opacity: float = 0.0,
    *,
    assets_dir: Path | None = None,
) -> ImageMobject:
    root = assets_dir or Path(__file__).resolve().parent.parent
    path = root / "assets" / "backgrouds" / filename

    bg = ImageMobject(str(path))
    frame_w, frame_h = config.frame_width, config.frame_height
    img_w, img_h = bg.width, bg.height  # 加载后的原始比例
    if img_w / img_h > frame_w / frame_h:
        # 图片更宽 → 以高度为准，左右会裁一点
        bg.set_height(frame_h)
    else:
        # 图片更高 → 以宽度为准，上下会裁一点
        bg.set_width(frame_w)
    bg.move_to(ORIGIN)
    bg.set_opacity(opacity)
    bg.set_z_index(-100)
    return bg


# Colors passed to the vendored manim-rubikscube plugin, in its expected
# order: [Up, Right, Front, Down, Left, Back].
CUBE_FACE_COLORS = [BLUE, RED, YELLOW, GREEN, ORANGE, WHITE]

# A fixed, solvable scramble so the cube looks "lived in" like the reference
# video, instead of a factory-solved cube.
CUBE_SCRAMBLE_STATE = "BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR"
CUBE_SOLVED_STATE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


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


    # shadow=False: this scene draws its own screen-space shadow below.
    body = RubiksCube(colors=list(CUBE_FACE_COLORS), shadow=False)
    body.set_state(CUBE_SOLVED_STATE)
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


def rubiks_cube_3d(scale: float = 1.0) -> VGroup:
    """Rubik's cube for a real ``ThreeDScene`` camera.

    Unlike :func:`rubiks_cube`, no orientation is baked into the mobject: the
    cube stays axis-aligned and the 3D look comes from the camera itself
    (perspective projection + phi/theta orientation). Face turns therefore use
    the plain ``CubeMove`` with canonical axes.
    """
    body = RubiksCube(colors=list(CUBE_FACE_COLORS), shadow=False)
    body.set_state(CUBE_SOLVED_STATE)
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


def rubiks_cube_2x2_3d(scale: float = 1.0) -> VGroup:
    """Pocket cube using the same camera, palette, and shadow as the 3x3."""
    body = RubiksCube2x2(colors=list(CUBE_FACE_COLORS), shadow=False)
    body.set_stroke(CHARCOAL, width=1.6)
    body.scale(0.63 * scale).move_to(ORIGIN)

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
        highlight.set_stroke(CHARCOAL, width=2.8, opacity=0.96)
        highlights.add(highlight)
    highlights.set_z_index(7)
    return highlights


def dim_sticker(color, amount: float = 0.58):
    """在原色基础上变暗，amount 越大越暗"""
    return interpolate_color(color, BLACK, amount)


def question_mark() -> Text:
    mark = Text("?", font=FONT, font_size=150, weight=BOLD, color=YELLOW)
    mark.set_stroke(CHARCOAL, width=3.5, opacity=0.9, background=True)
    mark.rotate(-6 * DEGREES)
    return mark


def number_line() -> VGroup:
#    formula = MathTex(
#        r"\frac{8! \times 3^{7} \times 12! \times 2^{11}}{2}",
#        font_size=48,
#        color=WHITE,
#    )
    number = Text("43,252,003,274,489,856,000", font="Menlo", font_size=58, color=WHITE)
    caption = ctext("超过 4 千亿亿种可能性", font_size=44, weight=BOLD, color=YELLOW)

    caption.set_stroke(
        CHARCOAL,
        width=1,
        opacity=0.9,
        background=True
    )
    group = VGroup(number, caption).arrange(DOWN, buff=0.28)
    return group


def cartoon_firework() -> VGroup:
    """An upward, flower-shaped firework in the video's paper-cut palette."""
    trails = VGroup()
    dots = VGroup()
    colors = [YELLOW, WHITE, ORANGE]
    burst_center = DOWN * 0.34
    for i in range(13):
        angle = interpolate(25 * DEGREES, 155 * DEGREES, i / 12)
        radius = 1.28 + 0.18 * (i % 3)
        end = burst_center + radius * np.array([cos(angle), sin(angle), 0])
        side = np.sign(end[0])
        control_1 = burst_center + np.array([0.16 * side, 0.48, 0])
        control_2 = end + np.array([-0.16 * side, 0.2, 0])
        trail = CubicBezier(burst_center, control_1, control_2, end)
        trail.set_stroke(colors[i % len(colors)], width=7)
        trails.add(trail)
        dots.add(Dot(end, radius=0.08, color=colors[(i + 1) % len(colors)]))

    launch = CubicBezier(
        DOWN * 1.28,                          # 起点：越负越靠下 → 线越长
        DOWN * 1.0 + LEFT * 0.08,
        DOWN * 0.62 + RIGHT * 0.08,
        burst_center,
    ).set_stroke(WHITE, width=6)
    flash = Circle(radius=0.15, fill_color=WHITE, fill_opacity=0.95, stroke_color=YELLOW, stroke_width=6)
    flash.move_to(burst_center)
    burst = VGroup(launch, trails, dots, flash)
    burst.launch = launch
    burst.trails = trails
    burst.dots = dots
    burst.flash = flash
    return burst


def cartoon_clock() -> VGroup:
    """Small 1930s-cartoon-style alarm clock used as a one-second cue."""
    face = Circle(
        radius=0.36,
        fill_color=WHITE,
        fill_opacity=1,
        stroke_color=CHARCOAL,
        stroke_width=4,
    )
    bells = VGroup(
        Arc(radius=0.2, start_angle=20 * DEGREES, angle=140 * DEGREES, color=YELLOW, stroke_width=7).shift(LEFT * 0.27 + UP * 0.31),
        Arc(radius=0.2, start_angle=20 * DEGREES, angle=140 * DEGREES, color=YELLOW, stroke_width=7).shift(RIGHT * 0.27 + UP * 0.31),
    )
    legs = VGroup(
        Line(LEFT * 0.2 + DOWN * 0.29, LEFT * 0.3 + DOWN * 0.48, color=CHARCOAL, stroke_width=5),
        Line(RIGHT * 0.2 + DOWN * 0.29, RIGHT * 0.3 + DOWN * 0.48, color=CHARCOAL, stroke_width=5),
    )
    ticks = VGroup(*[
        Line(UP * 0.27, UP * 0.31, color=CHARCOAL, stroke_width=2).rotate(i * TAU / 12)
        for i in range(12)
    ])
    minute_hand = Line(ORIGIN, LEFT * 0.15 + UP * 0.08, color=CHARCOAL, stroke_width=5)
    second_hand = Line(ORIGIN, UP * 0.25, color=RED, stroke_width=3)
    hub = Dot(radius=0.045, color=CHARCOAL)
    clock = VGroup(bells, legs, face, ticks, minute_hand, second_hand, hub)
    clock.face = face
    clock.second_hand = second_hand
    return clock


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
        # self.add_fixed_in_frame_mobjects(paper_background(PAPER))
        self.add_fixed_in_frame_mobjects(image_background("kraft_paper_002.png", opacity=0.92))

        # 0-3s: quiet opening. The cube sits at the origin; keep the first
        # visual claim clear.
        cube = rubiks_cube_3d(scale=1.28)
        depth_sort_cube_camera(cube.body, self.camera)
        self.add_updater(lambda dt: depth_sort_cube_camera(cube.body, self.camera))

        # self.play(FadeIn(cube, shift=self.screen_point(0, 0.2)), run_time=1.0)
        self.add(cube)
        self.wait(0.5)
        # A gentle orbit sells the real 3D before anything else happens.
        # self.move_camera(theta=-120 * DEGREES, run_time=0.8)
        # self.wait(0.2)

        centers = list(cube.body.centers)
        other_faces = [
            face
            for cubie in cube.body.cubies.flatten()
            for face in cubie.submobjects
            if face not in centers
        ]
        original_fills = [face.get_fill_color() for face in other_faces]
        dimmed_fills = [dim_sticker(color) for color in original_fills]

        rings = VGroup(*[
            center.copy().set_fill(opacity=0).set_stroke(WHITE, width=2, opacity=0.88)
            for center in centers
        ])
        rings.set_z_index(7)

        # self.remove(intro)

        for _ in range(2):
            self.play(
                *[face.animate.set_fill(color) for face, color in zip(other_faces, dimmed_fills)],
                FadeIn(rings),
                run_time=0.5,
            )
            self.wait(0.2)
            self.play(
                *[face.animate.set_fill(color) for face, color in zip(other_faces, original_fills)],
                FadeOut(rings),
                run_time=0.5,
            )

        # THEN a few face turns: the centers just highlighted visibly stay in
        # place while the layers spin around them.
        for move in ("R", "U'", "F"):
            self.play(CubeMove(cube.body, move), run_time=0.56)

        question = question_mark().move_to(RIGHT * 2.88 + UP * 0.2)
        self.fix(question)
        self.play(CubeMove(cube.body, "L"), FadeIn(question, scale=0.65), run_time=0.45)
        self.play(Wiggle(question, rotation_angle=4 * DEGREES, scale_value=1.04), run_time=0.55)
        self.wait(0.35)

        # 6-12s: scale shock. Keep the cube small in the corner as a visual anchor.
        numbers = number_line()
        self.fix(numbers)
        self.play(
            FadeOut(question, shift=UP * 0.12),
            cube.animate.scale(0.42).move_to(self.screen_point(-6.6, -3.1)),
            run_time=1.0,
        )
        self.play(Write(numbers[0]), run_time=1.2)
        self.play(FadeIn(numbers[1], shift=UP * 0.15), run_time=0.8)
        self.wait(0.8)

        # 12-20s: one cube state per second, starting from the Big Bang.
        # The next paper backdrop drops in like a physical animation cel and
        # settles with a small vertical bounce.
        timeline_bg = image_background("kraft_paper_blue_003.png", opacity=0.92)
        timeline_bg.scale(1.25).shift(UP * 10.2)
        self.fix(timeline_bg)
        # 清除所有updater，避免后面每帧都重复计算魔方的前后遮挡关系。
        # self.clear_updaters()
        self.play(
            FadeOut(numbers),
            FadeOut(cube),
            timeline_bg.animate.shift(DOWN * 11.05),
            run_time=0.75,
            rate_func=smooth,
        )
        self.play(timeline_bg.animate.shift(UP * 0.1), run_time=0.1)
        self.play(timeline_bg.animate.shift(DOWN * 0.17), run_time=0.12)
        self.play(timeline_bg.animate.shift(UP * 0.07), run_time=0.1)

        # A single warm firework reads as the Big Bang without adding a label.
        firework = cartoon_firework()
        self.fix(firework)
        self.play(Create(firework.launch), run_time=0.32)
        self.play(GrowFromCenter(firework.flash), run_time=0.18)
        self.play(
            LaggedStart(
                *[Create(trail) for trail in firework.trails],
                *[GrowFromPoint(dot, firework.flash.get_center()) for dot in firework.dots],
                lag_ratio=0.03,
            ),
            run_time=0.72,
        )
        self.play(FadeOut(firework, shift=DOWN * 0.08), run_time=0.35)

        def new_counter_pair() -> tuple[VGroup, VGroup]:
            counter_cube = rubiks_cube_3d(scale=0.78)
            counter_cube.move_to(self.screen_point(0, 0.65))
            depth_sort_cube_camera(counter_cube.body, self.camera)
            self.add_updater(lambda dt: depth_sort_cube_camera(counter_cube.body, self.camera))
            # counter_cube.body.add_updater(lambda body: depth_sort_cube_camera(body, self.camera))
            clock = cartoon_clock().move_to(DOWN * 1.05)
            self.fix(clock)
            return counter_cube, clock

        archived_cubes: list[VGroup] = []
        archived_clocks: list[VGroup] = []

        counter_cube, clock = new_counter_pair()
        self.add(counter_cube)
        self.add_fixed_in_frame_mobjects(clock)

        # The center pair persists and accumulates moves. After each turn, a
        # snapshot of that exact state joins the stream on the left.
        for move in ("R", "U", "F"):
            self.play(
                CubeMove(counter_cube.body, move),
                Rotate(
                    clock.second_hand,
                    angle=-TAU,
                    about_point=clock.face.get_center(),
                ),
                run_time=0.48,
            )

            state_copy = counter_cube.copy()
            state_copy.body.clear_updaters() 
            depth_sort_cube_camera(state_copy.body, self.camera)  # 一次性排序
            # 不用再对各面**每一帧都**深度排序了，纯属浪费资源，后面复制的魔方不会再转动了。
            # state_copy.body.add_updater(lambda body: depth_sort_cube_camera(body, self.camera)) 
            clock_copy = clock.copy()
            self.add(state_copy)
            self.add_fixed_in_frame_mobjects(clock_copy)
            self.play(
                *[old.animate.shift(self.screen_point(-2.25, 0)) for old in archived_cubes],
                *[old.animate.shift(LEFT * 2.25) for old in archived_clocks],
                state_copy.animate.shift(self.screen_point(-2.25, 0)),
                clock_copy.animate.shift(LEFT * 2.25),
                run_time=0.68,
            )
            archived_cubes.append(state_copy)
            archived_clocks.append(clock_copy)
        
        # 最后中心的魔方再转一下
        self.play(
            CubeMove(counter_cube.body, "D"),
            Rotate(
                clock.second_hand,
                angle=-TAU,
                about_point=clock.face.get_center(),
            ),
            run_time=0.48,
        )

        self.wait(0.2)

        pie_center = RIGHT * 3.95 + UP * 0.65
        pie_radius = 0.95
        visible_slice_ratio = 0.028
        pie_start_angle = visible_slice_ratio * TAU / 2
        sweep_progress = ValueTracker(0)
        pie_fill = always_redraw(
            lambda: Sector(
                radius=pie_radius,
                start_angle=(
                    pie_start_angle
                    - visible_slice_ratio * sweep_progress.get_value() * TAU
                ),
                angle=(
                    -max(sweep_progress.get_value(), 0.001)
                    * (1 - visible_slice_ratio)
                    * TAU
                ),
                fill_color=WHITE,
                fill_opacity=0.88,
                stroke_width=0,
            ).shift(pie_center)
        )
        pie_outline = Circle(
            radius=pie_radius,
            color=CHARCOAL,
            stroke_width=3,
        ).move_to(pie_center)
        one_percent_slice = always_redraw(
            lambda: Sector(
                radius=pie_radius,
                start_angle=pie_start_angle,
                angle=(
                    -max(sweep_progress.get_value(), 0.001)
                    * visible_slice_ratio
                    * TAU
                ),
                fill_color=YELLOW,
                fill_opacity=1,
                stroke_width=0,
            ).shift(pie_center)
        )
        # one_percent = MathTex(r"\approx 1\%", font_size=58, color=YELLOW)
        one_percent = Text("≈1%", font="Menlo", font_size=54, color=YELLOW)
        one_percent.set_stroke(CHARCOAL, width=2, opacity=0.8, background=True)
        one_percent.next_to(pie_outline, RIGHT, buff=0.32)
        self.fix(pie_fill, pie_outline, one_percent_slice, one_percent)
        self.add_fixed_in_frame_mobjects(pie_fill, one_percent_slice)

        years = Text("138亿年", font="Menlo", font_size=42, color=YELLOW)
        years.set_stroke(CHARCOAL, width=2, opacity=0.8, background=True)
        years.next_to(pie_outline, RIGHT, buff=0.22)
        self.fix(years)  # 和 one_percent 一样 fixed-in-frame

        self.play(Create(pie_outline), run_time=0.22)
        self.play(FadeIn(years, shift=UP * 0.1), run_time=0.55)  # 卡在「138亿年」
        self.play(sweep_progress.animate.set_value(1), run_time=2.22, rate_func=linear)
        pie_fill.clear_updaters()
        one_percent_slice.clear_updaters()
        # 或：ReplacementTransform(years, one_percent)
        self.play(ReplacementTransform(years, one_percent), run_time=0.64)
        # self.play(FadeIn(one_percent, shift=UP * 0.14), run_time=0.4)
        progress_pie = VGroup(pie_fill, pie_outline, one_percent_slice, one_percent)
        self.wait(0.8)



class GroupTheoryBridgeScene(ThreeDScene):
    def fix(self, *mobjects: Mobject) -> None:
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.remove(*mobjects)

    def screen_point(self, x: float, y: float) -> np.ndarray:
        rotation = self.camera.get_rotation_matrix()
        return x * rotation[0] + y * rotation[1]

    def construct(self) -> None:
        self.set_camera_orientation(phi=65 * DEGREES, theta=-135 * DEGREES)

        active_bodies = []

        def sort_active_cubes(dt: float) -> None:
            for body in active_bodies:
                depth_sort_cube_camera(body, self.camera)

        def cubie_stickers(cubie) -> list[Mobject]:
            return [
                cubie.get_face(face)
                for face in get_faces_of_cubie(cubie.indices, cubie.dim)
            ]

        def other_stickers(body, excluded) -> list[Mobject]:
            excluded_ids = {id(cubie) for cubie in excluded}
            return [
                face
                for cubie in body.cubies.flatten()
                if id(cubie) not in excluded_ids
                for face in cubie_stickers(cubie)
            ]

        def swap_arrows(
            first_cubie, 
            second_cubie, 
            *, 
            extend_start: float = 2.6, 
            extend_end: float = 1.2) -> VGroup:
            """Curved swap arrows in the camera-facing plane (true 3D overlay).

            Built from the projected cubie centers, then inverse-scaled before
            being embedded on a camera-facing plane in front of both cubies
            (no fixed-in-frame HUD, no per-frame updater).
            """
            rot = self.camera.get_rotation_matrix()
            right, up, out = rot[0], rot[1], rot[2]

            # Aim at visible sticker centers (not the whole-cubie core), so tips
            # land on the module the eye actually sees.
            def module_center(cubie) -> np.ndarray:
                faces = get_faces_of_cubie(cubie.indices, cubie.dim)
                points = [cubie.get_face(name).get_center() for name in faces]
                return sum(points) / len(points)

            c1 = module_center(first_cubie)
            c2 = module_center(second_cubie)
            frame_center = self.camera.frame_center
            depths = [np.dot(center - frame_center, out) for center in (c1, c2)]
            depth = max(depths) + 0.08

            p1, p2 = (self.camera.project_point(center) for center in (c1, c2))
            p1[2] = p2[2] = 0
            # Slightly lengthen so CurvedArrow tips reach the module centers.
            delta = p2 - p1
            length = np.linalg.norm(delta)
            if length > 1e-6:
                extend = 0.1 * delta / length
                p1 = p1 - extend_start * extend
                p2 = p2 + extend_end * extend
            fronts = (
                CurvedArrow(p1, p2, angle=-0.72, color=MAGENTA_BG, stroke_width=6),
                CurvedArrow(p2, p1, angle=-0.72, color=CYAN_BG, stroke_width=6),
            )
            arrows = VGroup()
            embed = np.column_stack([right, up, out])
            projection_scale = (
                self.camera.get_focal_distance()
                / (self.camera.get_focal_distance() - depth)
                * self.camera.get_zoom()
            )
            for front in fronts:
                shadow = front.copy().set_color(CHARCOAL).set_stroke(CHARCOAL, width=9)
                shadow.shift(RIGHT * 0.045 + DOWN * 0.055)
                pair = VGroup(shadow, front)
                pair.scale(1 / projection_scale, about_point=ORIGIN)
                pair.apply_matrix(embed)
                pair.shift(frame_center + depth * out)
                arrows.add(pair)
            arrows.set_z_index(20)
            return arrows

        def cube_badge(text: str, center: np.ndarray) -> VGroup:
            box = RoundedRectangle(
                width=1.75,
                height=0.86,
                corner_radius=0.18,
                fill_color=CHARCOAL,
                fill_opacity=0.84,
                stroke_color=WHITE,
                stroke_width=2.5,
            )
            value = Text(text, font="Menlo", font_size=38, color=YELLOW)
            badge = VGroup(box, value).move_to(center)
            badge.set_z_index(21)
            return badge

        self.add_updater(sort_active_cubes)

        # 3x3: two chosen corner cubies are easy to point at, but the rest of
        # the cube cannot stay fixed while only those two exchange positions.
        blue_bg = image_background("kraft_paper_green_003.png", opacity=0.92)
        blue_bg.scale(1.15)
        self.add_fixed_in_frame_mobjects(blue_bg)

        cube_3x3 = rubiks_cube_3d(scale=1.88)
        cube_3x3.move_to(self.screen_point(-1.11, 1.77))
        active_bodies.append(cube_3x3.body)
        depth_sort_cube_camera(cube_3x3.body, self.camera)
        self.add(cube_3x3)
        self.wait(0.35)

        target_3x3 = [
            cube_3x3.body.cubies[0, 0, 2],
            cube_3x3.body.cubies[0, 2, 2],
        ]
        target_3x3_faces = [cubie_stickers(cubie) for cubie in target_3x3]
        rest_3x3_faces = other_stickers(cube_3x3.body, target_3x3)
        # badge_3x3 = cube_badge("3×3", RIGHT * 3.35 + UP * 0.72)
        arrows_3x3 = swap_arrows(*target_3x3)


        cross_path = Path(__file__).resolve().parent.parent / "pics" / "叉号.png"

        impossible = ImageMobject(str(cross_path))
        # impossible.scale(2.8)
        impossible.set_height(2.6)
        impossible.move_to(RIGHT * 3.85 + UP * 0.11)
        impossible.set_z_index(22)

        # impossible = cartoon_x(RIGHT * 3.35 + DOWN * 0.42)
        # self.fix(badge_3x3, impossible)
        self.fix(impossible)

        # 在 747 行 self.play 之前
        original_target_fills = [
            [face.get_fill_color() for face in faces]
            for faces in target_3x3_faces
        ]
        # rest 只改了描边，fill 没动

        # 演示第一种情况。不可能只交换两个角块。
        self.play(
            # FadeIn(badge_3x3, shift=UP * 0.12),
            *[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=2.6)
                for faces, color in zip(target_3x3_faces, (MAGENTA_BG, CYAN_BG))
                for face in faces
            ],
            run_time=0.77,
        )
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(Create(arrow[0]), Create(arrow[1]), lag_ratio=0)
                    for arrow in arrows_3x3
                ],
                lag_ratio=0.14,
            ),
            run_time=0.77,
        )
        self.play(
            *[
                face.animate.set_stroke(WHITE, width=3.2, opacity=0.95)
                for face in rest_3x3_faces
            ],
            run_time=0.77,
        )

        self.play(
            FadeOut(arrows_3x3),
            *[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=1.4)
                for faces, colors in zip(target_3x3_faces, original_target_fills)
                for face, color in zip(faces, colors)
            ],
            *[
                face.animate.set_stroke(CHARCOAL, width=1.4, opacity=1)
                for face in rest_3x3_faces
            ],
            run_time=0.77,
            rate_func=smooth,
        )

        # 演示第二种情况。不可能只交换两个边棱块。
        target2_3x3 = [
            cube_3x3.body.cubies[0, 0, 1],
            cube_3x3.body.cubies[0, 1, 2],
        ]
        target2_3x3_faces = [cubie_stickers(cubie) for cubie in target2_3x3]
        rest2_3x3_faces = other_stickers(cube_3x3.body, target2_3x3)
        arrows2_3x3 = swap_arrows(*target2_3x3)


        self.play(
            # FadeIn(badge_3x3, shift=UP * 0.12),
            *[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=2.6)
                for faces, color in zip(target2_3x3_faces, (MAGENTA_BG, CYAN_BG))
                for face in faces
            ],
            run_time=0.77,
        )
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(Create(arrow[0]), Create(arrow[1]), lag_ratio=0)
                    for arrow in arrows2_3x3
                ],
                lag_ratio=0.14,
            ),
            run_time=0.77,
        )
        self.play(
            *[
                face.animate.set_stroke(WHITE, width=3.2, opacity=0.95)
                for face in rest2_3x3_faces
            ],
            run_time=0.77,
        )

        self.play(GrowFromCenter(impossible), run_time=0.36)
        self.play(Wiggle(impossible, rotation_angle=5 * DEGREES, scale_value=1.06), run_time=0.48)
        self.wait(1.11)

        # Slide to a warm paper cel for the 2x2 counterexample.
        orange_bg = image_background("kraft_paper_blue_003.png", opacity=0.88)
        orange_bg.scale(1.05).shift(UP * 12)
        orange_bg.set_z_index(-90)
        self.fix(orange_bg)
        self.play(
            cube_3x3.animate.shift(self.screen_point(-8.0, 0)),
            # FadeOut(VGroup(badge_3x3, arrows_3x3, impossible)),
            FadeOut(Group(arrows2_3x3, impossible)),
            orange_bg.animate.shift(DOWN * 12),
            run_time=0.86,
            rate_func=smooth,
        )
        self.remove(cube_3x3)
        active_bodies.clear()

        # 2x2: F R U B D swaps the two colored cubies and fixes the positions
        # of the six white-outlined cubies.
        cube_2x2 = rubiks_cube_2x2_3d(scale=1.65)
        cube_2x2.move_to(self.screen_point(-2.15, 0.08))
        active_bodies.append(cube_2x2.body)
        depth_sort_cube_camera(cube_2x2.body, self.camera)
        self.add(cube_2x2)

        target_2x2 = [
            cube_2x2.body.cubies[0, 0, 1],
            cube_2x2.body.cubies[0, 1, 1],
        ]
        target_2x2_faces = [cubie_stickers(cubie) for cubie in target_2x2]
        rest_2x2_faces = other_stickers(cube_2x2.body, target_2x2)
        # badge_2x2 = cube_badge("2×2", RIGHT * 3.35 + UP * 0.72)
        arrows_2x2 = swap_arrows(*target_2x2)


        check_path = Path(__file__).resolve().parent.parent / "pics" / "对号.png"

        possible = ImageMobject(str(check_path))
        # possible.scale(2.8)
        possible.set_height(2.6)
        possible.move_to(RIGHT * 3.85 + UP * 0.11)
        possible.set_z_index(22)


        # possible = cartoon_check(RIGHT * 3.35 + DOWN * 0.42)
        # self.fix(badge_2x2, possible)
        self.fix(possible)

        self.play(
            # FadeIn(badge_2x2, shift=UP * 0.12),
            *[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=2.8)
                for faces, color in zip(target_2x2_faces, (MAGENTA_BG, CYAN_BG))
                for face in faces
            ],
            run_time=0.4,
        )
        self.play(
            *[
                face.animate.set_stroke(WHITE, width=3.6, opacity=1)
                for face in rest_2x2_faces
            ],
            LaggedStart(
                *[
                    AnimationGroup(Create(arrow[0]), Create(arrow[1]), lag_ratio=0)
                    for arrow in arrows_2x2
                ],
                lag_ratio=0.14,
            ),
            run_time=0.4,
        )
        self.play(
            FadeOut(arrows_2x2),
            *[
                face.animate.set_stroke(CHARCOAL, width=1.6, opacity=1)
                for face in rest_2x2_faces
            ],
            run_time=0.3,
        )

        moves_2x2 = ("F2", "R", "B'", "U", "F", "D2", "L2", "D", "B", "L'")
        badges_2x2: list[VGroup] = []
        for move in moves_2x2:
            box = RoundedRectangle(
                width=0.78,
                height=0.62,
                corner_radius=0.14,
                fill_color=CHARCOAL,
                fill_opacity=0.84,
                stroke_color=WHITE,
                stroke_width=2.2,
            )
            text = Text(move, font="Menlo", font_size=26, color=YELLOW)
            badges_2x2.append(VGroup(box, text))
        row1 = VGroup(*badges_2x2[:5]).arrange(RIGHT, buff=0.1)
        row2 = VGroup(*badges_2x2[5:]).arrange(RIGHT, buff=0.1)
        move_badges_2x2 = VGroup(row1, row2).arrange(DOWN, buff=0.14)
        move_badges_2x2.move_to(RIGHT * 3.35 + UP * 0.15)
        move_badges_2x2.set_z_index(24)
        self.fix(move_badges_2x2)
        self.play(
            LaggedStart(
                *[FadeIn(badge, shift=LEFT * 0.1) for badge in badges_2x2],
                lag_ratio=0.08,
            ),
            run_time=0.4,
        )
        for move, badge in zip(moves_2x2, badges_2x2):
            self.play(
                CubeMove(cube_2x2.body, move),
                Indicate(badge, color=YELLOW, scale_factor=1.1),
                run_time=0.38,
            )
        self.play(FadeOut(move_badges_2x2), run_time=0.3)
        self.play(GrowFromCenter(possible), run_time=0.3)
        self.play(Wiggle(possible, rotation_angle=4 * DEGREES, scale_value=1.05), run_time=0.3)
        self.wait(0.3)

        # Commutator cel: smaller paper slides in from the right, leaving the
        # previous background visible around the edges.
        commutator_bg = image_background("kraft_paper_pink_003.png", opacity=0.88)
        commutator_bg.scale(0.95).shift(RIGHT * 20)
        commutator_bg.set_z_index(-80)
        self.fix(commutator_bg)
        self.play(
            cube_2x2.animate.shift(self.screen_point(-8.0, 0)),
            # FadeOut(Group(move_badges_2x2, possible)),
            FadeOut(possible),
            commutator_bg.animate.shift(LEFT * 20),
            run_time=0.86,
            rate_func=smooth,
        )
        self.remove(cube_2x2)
        active_bodies.clear()

        commutator_cube = rubiks_cube_3d(scale=1.88)
        commutator_cube.move_to(self.screen_point(0, 0.28))
        active_bodies.append(commutator_cube.body)
        depth_sort_cube_camera(commutator_cube.body, self.camera)
        self.add(commutator_cube)

        self.wait(0.4)

        move_badges = VGroup()
        for character in ("上", "左", "下", "右"):
            box = RoundedRectangle(
                width=0.92,
                height=0.68,
                corner_radius=0.15,
                fill_color=PAPER,
                fill_opacity=0.1,
                stroke_color=WHITE,
                stroke_width=2,
            )
            text = ctext(character, font_size=30, color=WHITE)
            move_badges.add(VGroup(box, text))
        move_badges.arrange(RIGHT, buff=0.22).move_to(DOWN * 2.88)
        move_badges.set_z_index(24)
        self.fix(move_badges)
        self.play(
            LaggedStart(*[FadeIn(badge, shift=UP * 0.12) for badge in move_badges], lag_ratio=0.1),
            run_time=0.55,
        )

        # Preview the bottom cross, then return to the hero angle for the
        # familiar "上左下右" sequence.
        cross_positions = [
            (0, 1, 0),  # 底面 前棱：有 D + F
            (1, 0, 0),  # 底面 右棱：有 D + R
            (1, 1, 0),  # 底面 中心：只有 D
            (1, 2, 0),  # 底面 左棱：有 D + L
            (2, 1, 0),  # 底面 后棱：有 D + B
        ]
        # 底面上朝下的十字贴纸
        cross_faces = [
            commutator_cube.body.cubies[pos].get_face("D")
            for pos in cross_positions
        ]
        # 四个棱块连着的侧面贴纸
        side_face_by_edge = {
            (0, 1, 0): "F",
            (1, 0, 0): "R",
            (1, 2, 0): "L",
            (2, 1, 0): "B",
        }
        cross_faces += [
            commutator_cube.body.cubies[pos].get_face(face)
            for pos, face in side_face_by_edge.items()
        ]
        original_cross_colors = [face.get_fill_color() for face in cross_faces]
        self.move_camera(
            phi=145 * DEGREES,
            theta=-145 * DEGREES,
            added_anims=[
                face.animate.set_fill(CYAN_BG, opacity=1).set_stroke(WHITE, width=3)
                for face in cross_faces
            ],
            run_time=1.22,
        )
        self.play(
            LaggedStart(*[Indicate(face, color=YELLOW, scale_factor=1.06) for face in cross_faces], lag_ratio=0.08),
            run_time=0.88,
        )
        self.move_camera(
            phi=65 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=1.4)
                for face, color in zip(cross_faces, original_cross_colors)
            ],
            run_time=1.22,
        )

        swapped_corners = [
            commutator_cube.body.cubies[0, 0, 0],
            commutator_cube.body.cubies[0, 0, 2],
        ]
        swapped_corner_faces = [cubie_stickers(cubie) for cubie in swapped_corners]
        self.play(
            *[
                face.animate.set_fill(color, opacity=1).set_stroke(WHITE, width=2.5)
                for faces, color in zip(swapped_corner_faces, (MAGENTA_BG, CYAN_BG))
                for face in faces
            ],
            run_time=0.5,
        )


        for move, badge in zip(("R", "U", "R'", "U'"), move_badges):
            self.play(
                CubeMove(commutator_cube.body, move),
                Indicate(badge, color=YELLOW, scale_factor=1.1),
                run_time=0.77,
            )

        # The same five bottom-cross stickers return to their original
        # positions; reveal them again while the camera swings underneath.
        self.move_camera(
            phi=135 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                face.animate.set_fill(CYAN_BG, opacity=1).set_stroke(WHITE, width=3)
                for face in cross_faces
            ],
            run_time=1.22,
        )
        self.play(
            LaggedStart(*[Indicate(face, color=YELLOW, scale_factor=1.06) for face in cross_faces], lag_ratio=0.08),
            run_time=0.88,
        )
        self.move_camera(
            phi=65 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                face.animate.set_fill(color, opacity=1).set_stroke(CHARCOAL, width=1.4)
                for face, color in zip(cross_faces, original_cross_colors)
            ],
            run_time=1.22,
        )

        corner_swap = swap_arrows(*swapped_corners)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(Create(arrow[0]), Create(arrow[1]), lag_ratio=0)
                    for arrow in corner_swap
                ],
                lag_ratio=0.14,
            ),
            run_time=0.77,
        )
        self.wait(2.3)

        formula = MathTex(
            r"ABA^{-1}B^{-1}",
            font_size=82,
            color=YELLOW,
        )
        formula.move_to(RIGHT * 3.3 + UP * 0.1)
        title_en = Text("Commutator", font="Menlo", font_size=52, color=WHITE)
        title_zh = ctext("交换子", font_size=34, color=YELLOW)
        formula_name = VGroup(title_en, title_zh).arrange(DOWN, buff=0.18)
        formula_name.move_to(RIGHT * 3.3 + UP * 0.05)
        self.fix(formula, formula_name)
        self.play(
            commutator_cube.animate.scale(0.82).move_to(self.screen_point(-3.25, 0.12)),
            FadeOut(corner_swap),
            FadeOut(move_badges),
            run_time=0.72,
        )
        self.play(Write(title_en), run_time=0.8)
        self.play(FadeIn(title_zh, shift=UP * 0.12), run_time=0.45)
        self.wait(2.3)
        self.play(
            # FadeOut(formula_name, shift=UP * 0.08),
            # Write(formula),
            ReplacementTransform(formula_name, formula),
            run_time=0.9,
        )
        self.wait(2.8)


class SuperflipScene(ThreeDScene):
    """~8s demo: highlight the edges, then reveal the Superflip state."""

    def fix(self, *mobjects: Mobject) -> None:
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.remove(*mobjects)

    def screen_point(self, x: float, y: float) -> np.ndarray:
        rotation = self.camera.get_rotation_matrix()
        return x * rotation[0] + y * rotation[1]

    def construct(self) -> None:
        self.set_camera_orientation(phi=65 * DEGREES, theta=-135 * DEGREES)
        self.add_fixed_in_frame_mobjects(image_background("kraft_paper_002.png", opacity=0.92))
        title = Text("Superflip", font="Menlo", weight=BOLD, font_size=58, color=YELLOW)
        title.set_stroke(CHARCOAL, width=2, opacity=0.9, background=True)
        title.to_edge(UP, buff=0.68)
        title.set_z_index(30)
        self.add_fixed_in_frame_mobjects(title)

        cube = rubiks_cube_3d(scale=1.45)
        cube.move_to(ORIGIN)
        depth_sort_cube_camera(cube.body, self.camera)
        self.add_updater(lambda dt: depth_sort_cube_camera(cube.body, self.camera))
        self.add(cube)
        self.wait(0.8)
        self.wait(0.25)

        # Edge cubies: exactly two coordinates at an extreme (0 or 2).
        edge_cubies = [
            cube.body.cubies[x, y, z]
            for x in range(3)
            for y in range(3)
            for z in range(3)
            if sum(c != 1 for c in (x, y, z)) == 2
        ]
        edge_faces = [
            face
            for cubie in edge_cubies
            for face_name in get_faces_of_cubie(cubie.indices, cubie.dim)
            for face in [cubie.get_face(face_name)]
        ]
        original_edge_strokes = [
            (face.get_stroke_color(), face.get_stroke_width())
            for face in edge_faces
        ]
        edge_face_ids = {id(face) for face in edge_faces}
        other_faces = [
            face
            for cubie in cube.body.cubies.flatten()
            for face_name in get_faces_of_cubie(cubie.indices, cubie.dim)
            for face in [cubie.get_face(face_name)]
            if id(face) not in edge_face_ids
        ]
        original_other_fills = [face.get_fill_color() for face in other_faces]
        dimmed_other_fills = [dim_sticker(color) for color in original_other_fills]

        # Dim centers and corners so the white-outlined edge stickers read as
        # one family, matching the focus treatment used in the earlier scenes.
        self.play(
            *[
                face.animate.set_fill(color, opacity=1)
                for face, color in zip(other_faces, dimmed_other_fills)
            ],
            *[
                face.animate.set_stroke(WHITE, width=3.2, opacity=0.95)
                for face in edge_faces
            ],
            run_time=0.7,
        )
        self.wait(2.1)

        self.play(
            *[
                face.animate.set_stroke(stroke, width=width, opacity=1)
                for face, (stroke, width) in zip(edge_faces, original_edge_strokes)
            ],
            *[
                face.animate.set_fill(color, opacity=1)
                for face, color in zip(other_faces, original_other_fills)
            ],
            run_time=0.65,
        )
        self.wait(0.15)

        # Superflip: flip every edge in place by swapping its two sticker colors.
        flip_anims = []
        for cubie in edge_cubies:
            names = get_faces_of_cubie(cubie.indices, cubie.dim)
            face_a = cubie.get_face(names[0])
            face_b = cubie.get_face(names[1])
            color_a = face_a.get_fill_color()
            color_b = face_b.get_fill_color()
            flip_anims.append(face_a.animate.set_fill(color_b, opacity=1))
            flip_anims.append(face_b.animate.set_fill(color_a, opacity=1))
        self.play(*flip_anims, run_time=1.35)
        self.wait(1.6)
