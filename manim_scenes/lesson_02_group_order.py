from __future__ import annotations

from pathlib import Path

import numpy as np

from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    UL,
    UP,
    AnimationGroup,
    Circle,
    Create,
    CubicBezier,
    DEGREES,
    DashedVMobject,
    Ellipse,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    ImageMobject,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    ReplacementTransform,
    RoundedRectangle,
    Rotate,
    Succession,
    Text,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    Wiggle,
    Write,
    BOLD,
    NORMAL,
    config,
    rate_functions,
)

from rubikscube import (
    BADGE_PRESETS,
    CubeMove,
    RubiksCube,
    RubiksCubeScene,
    course_badge,
    def_heading,
    depth_sort_cube,
    face_rings,
    grow_def_heading,
    notation_tag,
    normalize,
    proof_heading,
)


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

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "backgrouds"
PICS_DIR = Path(__file__).resolve().parent.parent / "pics"


# ---------------------------------------------------------------------------
# Shared overlay helpers
# ---------------------------------------------------------------------------


def paper_background(filename: str) -> ImageMobject:
    background = ImageMobject(str(ASSETS_DIR / filename))
    background.scale_to_fit_width(config.frame_width)
    if background.height < config.frame_height:
        background.scale_to_fit_height(config.frame_height)
    background.move_to(ORIGIN)
    background.set_z_index(-100)
    return background


def image_background(filename: str, *, opacity: float = 1.0) -> ImageMobject:
    """Background image scaled to cover the frame (no letterboxing gaps)."""
    bg = ImageMobject(str(ASSETS_DIR / filename))
    frame_w, frame_h = config.frame_width, config.frame_height
    if bg.width / bg.height > frame_w / frame_h:
        bg.scale_to_fit_height(frame_h)
    else:
        bg.scale_to_fit_width(frame_w)
    bg.move_to(ORIGIN)
    bg.set_opacity(opacity)
    bg.set_z_index(-100)
    return bg


def prepare_background_wipe_down(filename: str, *, overscale: float = 1.08) -> ImageMobject:
    """Place a full-bleed background above the frame, ready to slide down."""
    bg = image_background(filename)
    bg.scale(overscale)
    bg.shift(UP * 12)
    bg.set_z_index(-90)
    return bg


def play_paper_drop(
    scene: RubiksCubeScene,
    backdrop: ImageMobject,
    *,
    drop: float = 11.05,
    run_time: float = 0.75,
) -> None:
    """Slide a paper backdrop down from above, then settle with a small bounce."""
    scene.play(
        backdrop.animate.shift(DOWN * drop),
        run_time=run_time,
        rate_func=rate_functions.smooth,
    )
    scene.play(backdrop.animate.shift(UP * 0.1), run_time=0.1)
    scene.play(backdrop.animate.shift(DOWN * 0.17), run_time=0.12)
    scene.play(backdrop.animate.shift(UP * 0.07), run_time=0.1)


def play_definition_highlight(
    scene: RubiksCubeScene,
    definition: MathTex,
    highlight_indices: tuple[int, ...],
    *,
    indicate_indices: tuple[int, ...] = (),
    delayed_highlight_indices: tuple[int, ...] = (),
    pause: float = 0.45,
    delayed_pause: float = 0.55,
) -> None:
    if not highlight_indices and not indicate_indices and not delayed_highlight_indices:
        scene.play(Indicate(definition, color=YELLOW, scale_factor=1.04), run_time=1.0)
        return
    for index, part_index in enumerate(highlight_indices):
        scene.play(definition[part_index].animate.set_color(YELLOW), run_time=0.35)
        if index < len(highlight_indices) - 1:
            scene.wait(pause)
    if highlight_indices and indicate_indices:
        scene.wait(pause)
    for part_index in indicate_indices:
        part = definition[part_index]
        scene.play(Indicate(part, color=YELLOW, scale_factor=1.04), run_time=0.75)
        scene.play(part.animate.set_color(CHARCOAL), run_time=0.25)
    if delayed_highlight_indices and (highlight_indices or indicate_indices):
        scene.wait(delayed_pause)
    for part_index in delayed_highlight_indices:
        scene.play(definition[part_index].animate.set_color(YELLOW), run_time=0.35)


def ctext(text: str, font_size: int, color: str = PAPER) -> Text:
    value = Text(text, font=FONT, font_size=font_size, color=color)
    value.set_stroke(CHARCOAL, width=1.8, opacity=0.75, background=True)
    return value


def formula(*tex: str, font_size: int = 58, color: str = PAPER) -> MathTex:
    value = MathTex(*tex, font_size=font_size, color=color)
    value.set_stroke(CHARCOAL, width=2.2, opacity=0.8, background=True)
    return value


def question_mark() -> Text:
    mark = Text("?", font=FONT, font_size=130, color=YELLOW)
    mark.set_stroke(CHARCOAL, width=2.5, opacity=0.85, background=True)
    return mark


def state_count_panel() -> VGroup:
    number = Text(
        "43,252,003,274,489,856,000",
        font="Menlo",
        font_size=46,
        color=PAPER,
    )
    number.set_stroke(CHARCOAL, width=1.6, opacity=0.75, background=True)
    caption = ctext("超过 4 千亿亿种状态", 38, color=BLUE)
    return VGroup(number, caption).arrange(DOWN, buff=0.22)


def order_card(element: str, order: int) -> VGroup:
    box = RoundedRectangle(
        width=4.3,
        height=1.05,
        corner_radius=0.2,
        fill_color=CHARCOAL,
        fill_opacity=0.78,
        stroke_color=PAPER,
        stroke_width=2.2,
    )
    value = formula(
        rf"\operatorname{{ord}}\!\left({element}\right)",
        "=",
        str(order),
        font_size=42,
    )
    value[2].set_color(YELLOW)
    return VGroup(box, value)


def set_member(value: str, color: str = PAPER) -> VGroup:
    disk = Circle(
        radius=0.38,
        fill_color=color,
        fill_opacity=0.96,
        stroke_color=CHARCOAL,
        stroke_width=1.5,
    )
    label = MathTex(value, font_size=34, color=CHARCOAL)
    return VGroup(disk, label)


POOL_BALL_COLORS: dict[str, str] = {
    "-7": "#1E6BD6",
    "-3": "#F4C430",
    "-2": "#4A2D7A",
    "-1": "#E05A2B",
    "0": "#F5F5F0",
    "1": "#F4C430",
    "2": "#1E6BD6",
    "3": "#C41E3A",
    "4": "#6B2D8E",
    "5": "#FF6F3C",
    "6": "#B91C3C",
    "7": "#8B1530",
    "8": "#232323",
    "9": "#FFD700",
    "14": "#1B7D4E",
    "15": "#C41E3A",
}


def pool_ball(value: str, *, radius: float = 0.36) -> VGroup:
    """Billiard-style numbered ball (flat 2D: color disk + gloss + label)."""
    fill = POOL_BALL_COLORS.get(value, BLUE)
    light = value in {"0", "1", "9", "-3"}
    ball = Circle(
        radius=radius,
        fill_color=fill,
        fill_opacity=1.0,
        stroke_color=CHARCOAL,
        stroke_width=2.4,
    )
    shine = Circle(radius=radius * 0.2, fill_color=PAPER, fill_opacity=0.5, stroke_width=0)
    shine.move_to(ball.get_center() + UL * radius * 0.4)
    label_color = CHARCOAL if light else PAPER
    label = MathTex(value, font_size=int(30 * radius / 0.36), color=label_color)
    return VGroup(ball, shine, label)


def pool_ball_cluster(
    values: tuple[str, ...],
    center: np.ndarray,
    *,
    radius: float = 0.44,
    row_buff: float = 0.32,
    col_buff: float = 0.34,
) -> tuple[VGroup, VGroup, list[np.ndarray]]:
    """Lay out six balls as 1 + 2 + 3 rows; return cluster, flat group, targets."""
    if len(values) != 6:
        raise ValueError("pool_ball_cluster expects exactly six ball labels")
    row1 = VGroup(pool_ball(values[0], radius=radius))
    row2 = VGroup(pool_ball(values[1], radius=radius), pool_ball(values[2], radius=radius))
    row2.arrange(RIGHT, buff=row_buff)
    row3 = VGroup(
        pool_ball(values[3], radius=radius),
        pool_ball(values[4], radius=radius),
        pool_ball(values[5], radius=radius),
    )
    row3.arrange(RIGHT, buff=row_buff)
    cluster = VGroup(row1, row2, row3).arrange(DOWN, buff=col_buff)
    cluster.move_to(center)
    balls = VGroup(*row1, *row2, *row3)
    targets = [np.array(ball.get_center()) for ball in balls]
    return cluster, balls, targets


def pool_balls_enter_from_left(
    scene: RubiksCubeScene,
    balls: VGroup,
    targets: list[np.ndarray],
    *,
    lag_ratio: float = 0.16,
    run_time: float = 1.55,
) -> None:
    """Balls enter from the left along arcing paths, then settle with a small bounce."""
    animations = []
    for index, (ball, target) in enumerate(zip(balls, targets, strict=True)):
        wave = 1.0 if index % 2 == 0 else -1.0
        start = np.array([-8.8, target[1] + wave * 0.85, 0.0])
        ball.move_to(start)
        control_1 = start + RIGHT * 3.4 + UP * (1.35 * wave)
        control_2 = target + LEFT * 1.1 + UP * (0.45 * wave)
        path = CubicBezier(start, control_1, control_2, target)
        animations.append(MoveAlongPath(ball, path).set_rate_func(rate_functions.ease_out_cubic))
    scene.play(LaggedStart(*animations, lag_ratio=lag_ratio), run_time=run_time)
    scene.play(
        LaggedStart(
            *[ball.animate.shift(UP * 0.12) for ball in balls],
            lag_ratio=0.08,
        ),
        run_time=0.22,
    )
    scene.play(
        LaggedStart(
            *[
                ball.animate.shift(DOWN * 0.12).set_rate_func(rate_functions.ease_out_bounce)
                for ball in balls
            ],
            lag_ratio=0.08,
        ),
        run_time=0.42,
    )


def pool_ball_equation(*parts: str, ball_radius: float = 0.34) -> VGroup:
    """Lay out numbered pool balls with ``+``, ``=`` operators between."""
    row = VGroup()
    for part in parts:
        if part in {"+", "=", "×", "*"}:
            row.add(ctext(part, 38, color=CHARCOAL))
        else:
            row.add(pool_ball(part, radius=ball_radius))
    row.arrange(RIGHT, buff=0.2)
    return row


def play_pool_ball_equation_enter(
    scene: RubiksCubeScene,
    row: VGroup,
    *,
    start_offset: np.ndarray | None = None,
    lag_ratio: float = 0.1,
) -> None:
    """Reveal operators, then settle the three balls with three low arcs."""
    if start_offset is None:
        start_offset = LEFT * 0.45 + UP * 0.45

    operators = VGroup(*[part for part in row if isinstance(part, Text)])
    balls = VGroup(*[part for part in row if not isinstance(part, Text)])
    targets = [np.array(ball.get_center()) for ball in balls]

    for ball, target in zip(balls, targets, strict=True):
        ball.move_to(target + start_offset)

    scene.play(FadeIn(operators, shift=UP * 0.06), run_time=0.55)
    scene.play(
        LaggedStart(*[FadeIn(ball, scale=0.94) for ball in balls], lag_ratio=lag_ratio),
        run_time=0.32,
    )

    bounce_specs = (
        (0.68, 0.18, 0.44),
        (0.32, 0.11, 0.38),
        (0.0, 0.08, 0.34),
    )
    ground_offset = np.array([start_offset[0], 0.0, 0.0])
    starts = [target + start_offset for target in targets]
    for remaining, peak_height, run_time in bounce_specs:
        landings = [target + ground_offset * remaining for target in targets]
        paths = []
        for ball, start, landing in zip(balls, starts, landings, strict=True):
            travel = landing - start
            path = CubicBezier(
                start,
                start + travel * 0.32 + UP * peak_height,
                start + travel * 0.68 + UP * peak_height,
                landing,
            )
            paths.append(MoveAlongPath(ball, path).set_rate_func(rate_functions.linear))
        scene.play(
            LaggedStart(*paths, lag_ratio=lag_ratio),
            run_time=run_time,
        )
        starts = landings


POOL_BALL_RADIUS = 0.34
POOL_GROUND_Y = -1.78
POOL_FIRST_HOLE_X = 0.2
POOL_SECOND_HOLE_X = 3.2


def pool_pocket(x: float, *, ground_y: float = POOL_GROUND_Y) -> VGroup:
    """Create a fixed 2D pocket centered on the invisible ground line."""
    rim = Ellipse(
        width=0.92,
        height=0.3,
        fill_color=CHARCOAL,
        fill_opacity=0.92,
        stroke_color=PAPER,
        stroke_width=1.2,
        stroke_opacity=0.65,
    )
    inner = Ellipse(
        width=0.62,
        height=0.15,
        fill_color=BLACK,
        fill_opacity=1.0,
        stroke_width=0,
    )
    pocket = VGroup(rim, inner).move_to(np.array([x, ground_y, 0.0]))
    pocket.set_z_index(8)
    return pocket


def roll_pool_ball(
    ball: VGroup,
    target_x: float,
    *,
    run_time: float,
    rate_func,
    ball_radius: float = POOL_BALL_RADIUS,
) -> UpdateFromAlphaFunc:
    """Move and rotate the whole ball without deforming its circular shell."""
    start = ball.copy()
    start_center = np.array(ball.get_center())
    distance = target_x - start_center[0]

    def update(mobject: VGroup, alpha: float) -> None:
        mobject.become(start)
        mobject.shift(RIGHT * distance * alpha)
        mobject.rotate(
            -distance * alpha / ball_radius,
            axis=OUT,
            about_point=mobject.get_center(),
        )

    return UpdateFromAlphaFunc(
        ball,
        update,
        run_time=run_time,
        rate_func=rate_func,
    )


def play_closure_pool_demo(
    scene: RubiksCubeScene,
    definition: MathTex,
) -> VGroup:
    """Animate ``7 + (-3) = 4`` as two balls entering and leaving pockets."""
    ball_radius = POOL_BALL_RADIUS
    ball_y = POOL_GROUND_Y + ball_radius
    first_hole_x = POOL_FIRST_HOLE_X
    second_hole_x = POOL_SECOND_HOLE_X

    first_hole = pool_pocket(first_hole_x)
    second_hole = pool_pocket(second_hole_x)
    ball_7 = pool_ball("7", radius=ball_radius).move_to(np.array([-4.8, ball_y, 0.0]))
    ball_minus_3 = pool_ball("-3", radius=ball_radius).move_to(np.array([-1.8, ball_y, 0.0]))
    ball_4 = pool_ball("4", radius=ball_radius).move_to(np.array([second_hole_x, ball_y, 0.0]))
    balls = VGroup(ball_7, ball_minus_3, ball_4).set_z_index(12)
    demo = VGroup(first_hole, second_hole, balls)
    scene.fix(demo)

    scene.play(
        Indicate(definition, color=YELLOW, scale_factor=1.04),
        FadeIn(first_hole),
        FadeIn(second_hole),
        FadeIn(ball_7, shift=RIGHT * 0.08),
        FadeIn(ball_minus_3, shift=RIGHT * 0.08),
        run_time=0.55,
    )

    collision_x = ball_minus_3.get_center()[0] - 2 * ball_radius
    scene.play(
        roll_pool_ball(
            ball_7,
            collision_x,
            run_time=0.82,
            rate_func=rate_functions.ease_in_sine,
        )
    )

    # After impact, both balls keep moving. The struck ball reaches the pocket
    # first; the 7-ball follows more slowly, like a follow/topspin shot.
    scene.play(
        AnimationGroup(
            Succession(
                roll_pool_ball(
                    ball_minus_3,
                    first_hole_x,
                    run_time=0.58,
                    rate_func=rate_functions.linear,
                ),
                FadeOut(ball_minus_3, shift=DOWN * 0.25, scale=0.18, run_time=0.16),
            ),
            Succession(
                roll_pool_ball(
                    ball_7,
                    first_hole_x,
                    run_time=1.15,
                    rate_func=rate_functions.linear,
                ),
                FadeOut(ball_7, shift=DOWN * 0.25, scale=0.18, run_time=0.16),
            ),
            lag_ratio=0,
        )
    )
    balls.remove(ball_7, ball_minus_3)

    scene.play(FadeIn(ball_4, shift=UP * 0.18, scale=0.18), run_time=0.3)
    scene.play(
        roll_pool_ball(
            ball_4,
            second_hole_x + 2 * PI * ball_radius,
            run_time=0.92,
            rate_func=rate_functions.linear,
        )
    )
    return demo


def play_axiom_pool_demo(
    scene: RubiksCubeScene,
    formula_part: MathTex,
    *,
    left_value: str,
    right_value: str,
    result_value: str,
    final_wait: float,
    initial_wait: float = 0.0,
    highlight_formula: bool = True,
) -> VGroup:
    """Animate one binary operation while highlighting its axiom formula."""
    ball_radius = POOL_BALL_RADIUS
    ball_y = POOL_GROUND_Y + ball_radius
    first_hole_x = POOL_FIRST_HOLE_X
    second_hole_x = POOL_SECOND_HOLE_X
    left_x = -4.6
    right_x = -2.0
    result_x = second_hole_x + 2 * PI * ball_radius

    first_hole = pool_pocket(first_hole_x)
    second_hole = pool_pocket(second_hole_x)
    striker = pool_ball(left_value, radius=ball_radius).move_to(np.array([left_x, ball_y, 0.0]))
    struck = pool_ball(right_value, radius=ball_radius).move_to(np.array([right_x, ball_y, 0.0]))
    result = pool_ball(result_value, radius=ball_radius).move_to(
        np.array([second_hole_x, ball_y, 0.0])
    )
    balls = VGroup(striker, struck, result).set_z_index(12)
    demo = VGroup(first_hole, second_hole, balls)
    scene.fix(demo)

    entrance = [
        FadeIn(first_hole),
        FadeIn(second_hole),
        FadeIn(striker, shift=RIGHT * 0.08),
        FadeIn(struck, shift=RIGHT * 0.08),
    ]
    if highlight_formula:
        scene.play(
            Indicate(formula_part, color=YELLOW, scale_factor=1.04),
            *entrance,
            run_time=1.0,
        )
    else:
        scene.play(*entrance, run_time=0.55)
    if initial_wait:
        scene.wait(initial_wait)

    collision_x = struck.get_center()[0] - 2 * ball_radius
    scene.play(
        roll_pool_ball(
            striker,
            collision_x,
            run_time=0.48,
            rate_func=rate_functions.ease_in_sine,
        )
    )
    scene.play(
        AnimationGroup(
            Succession(
                roll_pool_ball(
                    struck,
                    first_hole_x,
                    run_time=0.42,
                    rate_func=rate_functions.linear,
                ),
                FadeOut(struck, shift=DOWN * 0.25, scale=0.18, run_time=0.12),
            ),
            Succession(
                roll_pool_ball(
                    striker,
                    first_hole_x,
                    run_time=0.75,
                    rate_func=rate_functions.linear,
                ),
                FadeOut(striker, shift=DOWN * 0.25, scale=0.18, run_time=0.12),
            ),
            lag_ratio=0,
        )
    )
    balls.remove(striker, struck)

    scene.play(FadeIn(result, shift=UP * 0.18, scale=0.18), run_time=0.18)
    scene.play(
        roll_pool_ball(
            result,
            result_x,
            run_time=0.78,
            rate_func=rate_functions.linear,
        )
    )
    scene.wait(final_wait)
    return demo


AXIOM_NAMES = ("封闭性", "结合律", "单位元", "逆元")
AXIOM_CHIP_Y_ROW = 3.58
AXIOM_CHIP_Y_HERO = 2.28
AXIOM_CHIP_LEFT_BUFF = 0.68


def axiom_chip(index: int, *, large: bool = False, active: bool = True) -> VGroup:
    name = AXIOM_NAMES[index]
    font_size = 38 if large else 22
    height = 1.02 if large else 0.58
    min_width = 5.0 if large else 3.45
    text = Text(
        f"公理{index + 1}  {name}",
        font=FONT,
        font_size=font_size,
        color=CHARCOAL if active else PAPER,
        weight=BOLD if large and active else NORMAL,
    )
    box = RoundedRectangle(
        width=max(min_width, text.width + 0.48 if large else text.width + 0.42),
        height=height,
        corner_radius=0.1,
        fill_color=YELLOW if active else CHARCOAL,
        fill_opacity=0.96 if active else 0.48,
        stroke_color=PAPER,
        stroke_width=1.4,
    )
    text.move_to(box.get_center())
    return VGroup(box, text)


def axiom_row_slot_center(index: int) -> np.ndarray:
    """Center of chip ``index`` in the four-chip top row."""
    slots = VGroup(*[axiom_chip(i, large=False, active=False) for i in range(4)])
    slots.arrange(RIGHT, buff=0.18)
    slots.move_to(UP * AXIOM_CHIP_Y_ROW)
    return np.array(slots[index].get_center())


def axiom_body(
    definition_parts: tuple[str, ...],
    integer_tex: str,
) -> tuple[VGroup, VGroup]:
    definition = formula(*definition_parts, font_size=56, color=CHARCOAL)
    definition.move_to(UP * 1.0)

    divider = Line(
        LEFT * 6.8 + UP * 0.14,
        RIGHT * 6.8 + UP * 0.14,
        color=PAPER,
        stroke_width=1.5,
        stroke_opacity=0.66,
    )

    integer_example = formula(integer_tex, font_size=54, color=CHARCOAL)
    integer_example.move_to(DOWN * 1.44)

    return VGroup(definition, divider), integer_example


OPENING_ORDER_EXAMPLES: tuple[tuple[str, int], ...] = (
    ("R U", 105),
    ("U L D R", 315),
    ("R U2 D' B D'", 1260),
)


def moves_to_latex(moves: str) -> str:
    """Executable notation (``U2``, ``D'``) → MathTex (``U^2``, ``D'``)."""
    if any(ch in moves for ch in "^_{}"):
        return moves.replace(" ", r"\ ")
    parts: list[str] = []
    for token in moves.split():
        if len(token) == 1:
            parts.append(token)
        elif len(token) == 2 and token[1] == "2":
            parts.append(f"{token[0]}^2")
        elif len(token) == 2 and token[1] == "'":
            parts.append(f"{token[0]}'")
        else:
            parts.append(token)
    return r"\ ".join(parts)


def move_sequence_badge(moves: str, *, font_size: int = 52) -> VGroup:
    style = BADGE_PRESETS["move"].merged(font_size=font_size)
    tokens = moves.split()
    if len(tokens) > 1:
        tex_parts: list[str] = []
        for index, token in enumerate(tokens):
            tex_parts.append(moves_to_latex(token))
            if index < len(tokens) - 1:
                tex_parts.append(r"\ ")
        label = formula(*tex_parts, font_size=style.font_size)
    else:
        label = formula(moves_to_latex(moves), font_size=style.font_size)
    box = RoundedRectangle(
        width=max(2.4, label.width + 2 * style.h_padding),
        height=style.height,
        corner_radius=style.corner_radius,
        fill_color=style.fill_color,
        fill_opacity=style.fill_opacity,
        stroke_color=style.stroke_color,
        stroke_width=style.stroke_width,
    )
    label.move_to(box.get_center())
    return VGroup(box, label)


def invert_move_sequence(moves: str) -> str:
    """Reverse a move sequence and invert each move (for returning to solved)."""
    inverted: list[str] = []
    for move in reversed(moves.split()):
        if move.endswith("'"):
            inverted.append(move[:-1])
        elif move.endswith("2"):
            inverted.append(move)
        else:
            inverted.append(f"{move}'")
    return " ".join(inverted)


def chaos_image() -> ImageMobject:
    """Load chaos2.png, remove checkerboard backdrop, crop to illustration."""
    import numpy as np
    from PIL import Image

    arr = np.array(Image.open(PICS_DIR / "chaos2.png").convert("RGBA"))

    rgb = arr[:, :, :3].astype(float)
    max_channel = np.max(rgb, axis=2)
    min_channel = np.min(rgb, axis=2)
    # 灰白棋盘格：亮度高且 R≈G≈B；保留中间彩色/黑色线条。
    checkerboard = (max_channel >= 190) & ((max_channel - min_channel) < 30)
    arr[checkerboard, 3] = 0

    opaque = arr[:, :, 3] > 0
    ys, xs = np.where(opaque)
    pad = 12
    y0 = max(0, int(ys.min()) - pad)
    y1 = min(arr.shape[0], int(ys.max()) + pad + 1)
    x0 = max(0, int(xs.min()) - pad)
    x1 = min(arr.shape[1], int(xs.max()) + pad + 1)
    arr = arr[y0:y1, x0:x1]

    image = ImageMobject(arr)
    image.scale_to_fit_height(3.8)
    image.move_to(ORIGIN)
    return image


# ---------------------------------------------------------------------------
# Opening hook
# ---------------------------------------------------------------------------


class Lesson02OpeningScene(RubiksCubeScene):
    """口播稿开头：状态规模 → 固定公式必复原 → 引入群。"""

    REPEAT_MOVE = "R  U  R'  U'"
    REPEAT_ORDER = 6

    def construct(self) -> None:
        background = paper_background("kraft_paper_002.png")
        self.add_fixed_in_frame_mobjects(background)

        # --- 复刻 lesson_01 开场：魔方居中、中心块闪烁、转几层 ---
        cube = self.add_cube(RubiksCube(total_size=2.75).move_to(ORIGIN))
        self.wait(0.5)

        for _ in range(1):
            rings = face_rings(
                cube.visible_center_stickers(),
                color=PAPER,
                width=2.2,
                scale=1.06,
            )
            self.play(cube.focus(cube.center_cubies()), FadeIn(rings), run_time=0.5)
            self.wait(0.2)
            self.play(FadeOut(rings), cube.reset_look(), run_time=0.5)

            # self.play(cube.focus(cube.center_cubies()), run_time=0.5)
            # self.wait(0.2)
            # self.play(cube.reset_look(), run_time=0.5)


        for move in ("R", "U'"):
            self.play(CubeMove(cube, move), run_time=0.56)

        # --- 魔方缩到左下角，再出现「4 千亿亿」数字（与 lesson_01 相同节奏）---
        stats = state_count_panel()
        stats.move_to(UP * 0.35)
        self.fix(stats)
        self.play(
            cube.animate.scale(0.42).move_to(self.screen_point(-6.6, -3.1)),
            run_time=1.0,
        )
        self.play(Write(stats[0]), run_time=1.2)
        self.play(FadeIn(stats[1], shift=UP * 0.15), run_time=0.8)
        self.wait(0.8)

        # 「这看起来无从下手」—— 展示 chaos 插图 ~1s
        chaos = chaos_image()
        self.fix(chaos)
        self.play(
            FadeOut(stats),
            FadeOut(cube),
            FadeIn(chaos, scale=0.88),
            run_time=0.75,
        )
        self.play(Wiggle(chaos, rotation_angle=3 * PI / 180, scale_value=1.04), run_time=0.55)
        self.wait(1.0)

        # --- 固定公式 R U R' U'：第一次完整转动，之后暗淡→恢复切状态 ---
        panel_up = UP * 0.45
        sequence = move_sequence_badge(self.REPEAT_MOVE)
        sequence.move_to(RIGHT * 3.55 + UP * 0.55 + panel_up)
        self.fix(sequence)

        demo_cube = self.add_cube(
            RubiksCube(total_size=2.35).move_to(self.screen_point(-4.0, 0.1))
        )
        self.play(
            FadeOut(chaos),
            FadeIn(demo_cube),
            FadeIn(sequence, shift=LEFT * 0.12),
            run_time=0.65,
        )

        repeat_labels = ("一次", "两次", "三次", "四次", "五次", "六次")
        count_label = ctext(repeat_labels[0], 44, color=BLUE)
        count_label.move_to(RIGHT * 3.55 + DOWN * 0.55 + panel_up)
        self.fix(count_label)

        # 第 1 次：逐步播放 R U R' U'
        self.turn(demo_cube, self.REPEAT_MOVE, run_time=0.5, wait=0.06)
        self.play(FadeIn(count_label, shift=UP * 0.08), run_time=0.4)
        self.wait(0.55)

        # 第 2–6 次：全体 blink → do_moves 切状态
        all_cubies = list(demo_cube.cubies.flatten())
        for index in range(2, self.REPEAT_ORDER + 1):
            next_label = ctext(repeat_labels[index - 1], 44, color=BLUE)
            next_label.move_to(count_label)
            self.fix(next_label)
            self.play(
                demo_cube.blink(all_cubies),
                Indicate(sequence, color=YELLOW, scale_factor=1.04),
                run_time=0.55,
            )
            demo_cube.do_moves(self.REPEAT_MOVE)
            self.play(
                ReplacementTransform(count_label, next_label),
                run_time=0.48,
            )
            count_label = next_label
            self.wait(0.3)

        # 「六次」→「恢复」：FadeOut / FadeIn（汉字 Transform 易扭曲）
        count_anchor = count_label.get_center()
        restored_label = ctext("恢复原状", 44, color=BLUE)
        restored_label.move_to(count_anchor)
        self.fix(restored_label)
        self.play(FadeOut(count_label), FadeIn(restored_label), run_time=0.4)
        count_label = restored_label
        self.wait(1.5)

        # 「那为什么它一定会复原？……」—— 在「恢复」下方单独淡入
        why_text = ctext("为什么不能在别的状态里一直循环？", 32)
        why_text.next_to(count_label, DOWN, buff=0.32)
        self.fix(why_text)
        self.play(FadeIn(why_text, shift=UP * 0.06), run_time=0.55)
        self.wait(2.28)

        # 「这段视频，我们要引入 group……」
        group_title = ctext("群 Group", 62, color=YELLOW)
        group_title.move_to(UP * 0.2)
        group_proof = ctext("严格证明：固定公式重复必复原", 34)
        group_proof.next_to(group_title, DOWN, buff=0.35)
        self.fix(group_title, group_proof)
        self.play(
            FadeOut(VGroup(sequence, count_label, why_text)),
            FadeOut(demo_cube),
            FadeIn(group_title, shift=DOWN * 0.15),
            run_time=0.7,
        )
        self.play(FadeIn(group_proof), run_time=0.55)
        self.wait(0.8)

        # 「我们会看到一些常见动作……」—— 标题上移，下方三行 order 预览
        header = VGroup(group_title, group_proof)
        row_ys = (0.05, -1.15, -2.35)
        preview_rows: list[tuple[RubiksCube, VGroup, Text]] = []

        for (moves, count), y in zip(OPENING_ORDER_EXAMPLES, row_ys, strict=True):
            cube = RubiksCube(total_size=0.68)
            cube.do_moves(moves)
            cube.move_to(self.screen_point(-4.88, y))
            depth_sort_cube(cube, self.camera)

            badge = move_sequence_badge(moves, font_size=36)
            badge.move_to(RIGHT * 0.05 + UP * y)

            count_text = f"最大：{count}次" if count == 1260 else f"{count}次"
            count_label = ctext(count_text, 34, color=BLUE)
            count_label.move_to(RIGHT * 4.95 + UP * y)

            self.fix(badge, count_label)
            preview_rows.append((cube, badge, count_label))

        self.play(header.animate.shift(UP * 2.88), run_time=0.65)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(cube, scale=0.92),
                        FadeIn(badge, shift=LEFT * 0.1),
                        FadeIn(count_label, shift=RIGHT * 0.1),
                    )
                    for cube, badge, count_label in preview_rows
                ],
                lag_ratio=0.22,
            ),
            run_time=1.35,
        )
        self.wait(1.2)

        for _, badge, _ in preview_rows:
            self.play(
                Indicate(badge, color=YELLOW, scale_factor=1.1),
                run_time=0.55,
            )
            self.wait(0.35)


# ---------------------------------------------------------------------------
# Definition 1: Group
# ---------------------------------------------------------------------------


class GroupAxiomsScene(RubiksCubeScene):
    """Definition 1：群的定义与四条公理。"""

    TITLE_Y = 2.95

    def construct(self) -> None:
        background = paper_background("kraft_paper_white_002.png")
        self.add_fixed_in_frame_mobjects(background)

        # --- 第一段：定义标题 → 中央虚线集合 → 台球跳入 ---
        title_body = "群是一些元素的集合"
        title2_body = "群是一些元素的集合  +  一个二元运算"
        title3_body = "群是一些元素的集合  +  一个二元运算  +  满足四条公理"

        title = def_heading(title_body, y=self.TITLE_Y)
        self.fix(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)

        boundary_width = 6.2
        boundary_height = 4.55
        reference_center_y = -0.15
        reference_height = 4.2
        boundary_top_y = reference_center_y + reference_height / 2
        boundary_center = np.array([0.0, boundary_top_y - boundary_height / 2, 0.0])
        cluster_center = boundary_center + UP * 0.28

        boundary = DashedVMobject(
            Ellipse(width=boundary_width, height=boundary_height, color=BLUE, stroke_width=8.8),
            num_dashes=46,
        )
        boundary.move_to(boundary_center)
        self.fix(boundary)
        self.play(Create(boundary), run_time=0.75)

        # 1 + 2 + 3：白 0；中排 8、7；下排 14、黄 -3、15
        member_specs = ("0", "8", "7", "14", "-3", "15")
        members, balls, member_targets = pool_ball_cluster(
            member_specs,
            cluster_center,
            radius=0.44,
        )
        self.fix(members)
        pool_balls_enter_from_left(self, balls, member_targets)
        self.wait(0.55)

        # --- 标题延长：「+ 一个二元运算」---
        title = grow_def_heading(
            self,
            title,
            title2_body,
            old_body=title_body,
            y=self.TITLE_Y,
        )

        # --- 集合左移，右侧先出现一般记号，再出现台球加法例 ---
        left_center = LEFT * 3.65 + UP * boundary_center[1]
        shift_vec = left_center - boundary_center

        right_x = RIGHT * 3.45
        operation = formula(
            r"\ast",
            r":",
            r"G\times G\longrightarrow G",
            font_size=58,
            color=CHARCOAL,
        )
        operation.move_to(right_x + UP * 0.95)
        operation_example = formula(
            r"(a,b)",
            r"\longmapsto",
            r"a\ast b",
            font_size=48,
            color=CHARCOAL,
        )
        operation_example.move_to(right_x + UP * 0.2)

        addition_row = pool_ball_equation("2", "+", "6", "=", "8")
        addition_row.move_to(right_x + DOWN * 0.95)

        self.fix(operation, operation_example)
        self.play(
            boundary.animate.shift(shift_vec),
            members.animate.shift(shift_vec),
            run_time=0.85,
        )
        self.play(
            Write(operation),
            FadeIn(operation_example, shift=UP * 0.08),
            run_time=0.9,
        )
        self.wait(0.35)
        self.play(
            operation[0].animate.set_color(YELLOW),
            operation[1].animate.set_color(YELLOW),
            run_time=0.3,
        )
        self.wait(0.4)
        for index, part in enumerate(operation_example):
            self.play(part.animate.set_color(YELLOW), run_time=0.28)
            if index < len(operation_example) - 1:
                self.wait(0.38)
        self.wait(1.5)
        self.fix(addition_row)
        play_pool_ball_equation_enter(self, addition_row)
        self.wait(1.5)

        # --- 标题再延长：「+ 四条公理」---
        title = grow_def_heading(
            self,
            title,
            title3_body,
            old_body=title2_body,
            y=self.TITLE_Y,
        )
        self.wait(1.0)

        intro = VGroup(
            title,
            boundary,
            members,
            addition_row,
            operation,
            operation_example,
        )

        chapters = (
            (
                "封闭性",
                (r"\forall a,b\in G,\qquad a\ast b\in G",),
                (),
                (),
                r"7+(-3)=4\in\mathbb{Z}",
            ),
            (
                "结合律",
                (
                    r"\forall a,\,b,\,c\in G,\qquad",
                    r"(a\ast b)",
                    r"\ast c",
                    r"=",
                    r"a\ast",
                    r"(b\ast c)",
                ),
                (0, 1, 5),
                (),
                r"(1+2)+3=1+(2+3)=6",
                (3,),
            ),
            (
                "单位元",
                (
                    r"\exists e\in G,",
                    r"\forall a\in G,\qquad",
                    r"e\ast a=a\ast e=a",
                ),
                (0, 1),
                (2,),
                r"0+7=7+0=7",
            ),
            (
                "逆元",
                (
                    r"\forall a\in G,",
                    r"\exists a^{-1}\in G,\qquad",
                    r"a\ast a^{-1}=a^{-1}\ast a=e",
                ),
                (0, 1),
                (2,),
                r"7+(-7)=(-7)+7=0",
            ),
        )

        green_bg = image_background("kraft_paper_green_003.png", opacity=0.92)
        green_bg.scale(1.25).shift(UP * 10.2)
        self.add_fixed_in_frame_mobjects(green_bg)
        self.play(FadeOut(intro), run_time=0.35)
        play_paper_drop(self, green_bg)
        self.remove(background)
        background = green_bg

        previous_content = VGroup()
        row_chips = VGroup()
        for index, chapter in enumerate(chapters):
            _, definition_parts, highlight_indices, indicate_indices, integer_tex = chapter[:5]
            delayed_highlight_indices = chapter[5] if len(chapter) > 5 else ()
            hero_chip = axiom_chip(index, large=True, active=True)
            hero_chip.move_to(UP * AXIOM_CHIP_Y_HERO)
            hero_chip.to_edge(LEFT, buff=AXIOM_CHIP_LEFT_BUFF)

            body, examples = axiom_body(definition_parts, integer_tex)
            self.fix(hero_chip, body, examples)

            if index == 0:
                self.play(FadeIn(hero_chip, shift=DOWN * 0.1), FadeIn(body, shift=DOWN * 0.08), run_time=0.65)
            else:
                self.play(
                    FadeOut(previous_content),
                    FadeIn(hero_chip, shift=DOWN * 0.1),
                    FadeIn(body, shift=DOWN * 0.08),
                    run_time=0.65,
                )
            self.wait(0.55)
            if index == 0:
                closure_demo = play_closure_pool_demo(self, body[0])
                self.play(FadeOut(closure_demo), run_time=0.3)
                self.play(FadeIn(examples, shift=UP * 0.12), run_time=0.35)
            elif index in (2, 3):
                for part_index in highlight_indices:
                    self.play(body[0][part_index].animate.set_color(YELLOW), run_time=0.35)
                    if part_index != highlight_indices[-1]:
                        self.wait(0.45)

                formula_part = body[0][indicate_indices[0]]
                if index == 2:
                    axiom_demo = play_axiom_pool_demo(
                        self,
                        formula_part,
                        left_value="7",
                        right_value="0",
                        result_value="7",
                        final_wait=0.15,
                        initial_wait=0.3,
                    )
                else:
                    self.play(Indicate(formula_part, color=YELLOW, scale_factor=1.04), run_time=0.75)
                    self.play(formula_part.animate.set_color(CHARCOAL), run_time=0.25)
                    self.wait(0.45)
                    axiom_demo = play_axiom_pool_demo(
                        self,
                        formula_part,
                        left_value="-7",
                        right_value="7",
                        result_value="0",
                        final_wait=0.95,
                        highlight_formula=False,
                    )
                self.play(FadeOut(axiom_demo), run_time=0.3)
                self.play(FadeIn(examples, shift=UP * 0.12), run_time=0.35)
            else:
                play_definition_highlight(
                    self,
                    body[0],
                    highlight_indices,
                    indicate_indices=indicate_indices,
                    delayed_highlight_indices=delayed_highlight_indices,
                )
                self.play(FadeIn(examples, shift=UP * 0.12), run_time=0.65)
            self.wait(0.85)

            slot_chip = axiom_chip(index, large=False, active=False)
            slot_chip.move_to(axiom_row_slot_center(index))
            self.play(Transform(hero_chip, slot_chip), run_time=0.55)
            row_chips.add(hero_chip)

            previous_content = VGroup(body, examples)

        previous_content_for_summary = previous_content

        # 「可以看到，对于整数与加法运算，符合上面的定理，所以这是一个群结构，我们叫整数加法群。」
        summary_background = paper_background("kraft_paper_pink_003.png")
        summary_title = ctext("四条公理，缺一不可", 48, color=YELLOW)
        summary_title.move_to(UP * 3.05)
        summary_formula = formula(r"(\mathbb{Z},+)", font_size=68, color=PAPER)
        summary_formula[0].set_color(YELLOW)
        summary_label = ctext("是一个群", 48, color=PAPER)
        summary = VGroup(summary_formula, summary_label).arrange(RIGHT, buff=0.35)
        summary.move_to(UP * 0.75)
        checks = VGroup(
            ctext("封闭性", 30),
            ctext("结合律", 30),
            ctext("单位元：0", 30),
            ctext("逆元：-a", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        checks.move_to(LEFT * 0.95 + DOWN * 1.35)
        check_mark = ImageMobject(str(PICS_DIR / "对号.png"))
        check_mark.set_height(2.6)
        check_mark.move_to(RIGHT * 3.85 + DOWN * 0.15)
        check_mark.set_z_index(22)
        self.fix(summary_background, summary_title, summary, checks, check_mark)

        self.play(
            FadeOut(background),
            FadeIn(summary_background),
            FadeOut(previous_content_for_summary),
            *[FadeOut(chip) for chip in row_chips],
            FadeIn(summary_title, shift=DOWN * 0.12),
            run_time=0.65,
        )
        self.remove_fixed_in_frame_mobjects(*row_chips)
        self.play(Write(summary), run_time=0.85)
        self.play(*[FadeIn(check, shift=RIGHT * 0.12) for check in checks], run_time=0.8)
        self.play(GrowFromCenter(check_mark), run_time=0.3)
        self.play(Wiggle(check_mark, rotation_angle=4 * DEGREES, scale_value=1.05), run_time=0.3)
        self.wait(0.75)

        # 「但对于整数与乘法运算，就不符合一个群结构，你能说出来哪里不符合么？」
        mult_title = ctext("整数 × 乘法 是群吗？", 42, color=YELLOW)
        mult_title.move_to(UP * 3.05)
        cross_mark = ImageMobject(str(PICS_DIR / "叉号.png"))
        cross_mark.set_height(3.35)
        cross_mark.move_to(DOWN * 0.15)
        cross_mark.set_z_index(22)
        self.fix(mult_title, cross_mark)
        self.play(
            FadeOut(summary_title),
            FadeOut(summary),
            FadeOut(checks),
            FadeOut(check_mark),
            FadeIn(mult_title),
            run_time=0.55,
        )
        self.play(GrowFromCenter(cross_mark), run_time=0.3)
        self.play(Wiggle(cross_mark, rotation_angle=5 * DEGREES, scale_value=1.06), run_time=0.48)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# Cube notation
# ---------------------------------------------------------------------------


class CubeNotationScene(RubiksCubeScene):
    """Cube notation：方块、面记号、转动记号、执行顺序。"""

    def construct(self) -> None:
        background = paper_background("kraft_paper_blue_003.png")
        self.add_fixed_in_frame_mobjects(background)

        # 「群结构是一个非常有力的工具，可以帮我们理解世界上的很多事情，包括魔方。」
        bridge = ctext("群论 · 理解魔方", 52, color=YELLOW)
        bridge.move_to(UP * 2.85)
        self.fix(bridge)
        cube = self.add_cube(RubiksCube(total_size=2.0).move_to(self.screen_point(-3.5, 1.88)))
        self.play(FadeIn(bridge), FadeIn(cube), run_time=0.65)
        self.wait(0.55)

        # 「在严谨定义魔方群之前，我们先统一这套课程使用的记号。」
        notation_title = ctext("魔方记号约定", 52, color=YELLOW)
        notation_title.move_to(UP * 2.85)
        self.fix(notation_title)
        self.play(ReplacementTransform(bridge, notation_title), run_time=0.55)
        self.wait(0.45)

        # 「一个三阶魔方可以看成由许多小块组成。这些小块称为 方块 cubies。」
        cubie_label = ctext("27 cubies · 方块", 34)
        cubie_label.move_to(RIGHT * 3.2 + UP * 1.28)
        counts = VGroup(
            ctext("8 corner cubies · 角块", 34),
            ctext("12 edge cubies · 棱块", 34),
            ctext("6 center cubies · 中心块", 34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        counts.next_to(cubie_label, DOWN, aligned_edge=LEFT, buff=0.38)
        self.fix(cubie_label, counts)
        visible_cubies = cube.corner_cubies() + cube.edge_cubies() + cube.center_cubies()
        self.play(FadeIn(cubie_label), run_time=0.45)
        self.play(*[cube.pop_out(cubie) for cubie in visible_cubies], run_time=0.7)
        self.play(
            Rotate(
                cube.body,
                angle=45 * DEGREES,
                axis=OUT,
                about_point=cube.get_cube_center(),
            ),
            run_time=0.65,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(
            Rotate(
                cube.body,
                angle=-45 * DEGREES,
                axis=OUT,
                about_point=cube.get_cube_center(),
            ),
            run_time=0.65,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(*[cube.pop_in(cubie) for cubie in visible_cubies], run_time=0.7)
        self.wait(0.25)

        # 「其中有 8 个 corner cubies……12 个 edge cubies……以及 6 个 center cubies……」
        for cubies, count in zip(
            (cube.corner_cubies(), cube.edge_cubies(), cube.center_cubies()),
            counts,
        ):
            self.play(FadeIn(count), *[cube.pop_out(cubie) for cubie in cubies], run_time=0.62)
            self.wait(0.42)
            self.play(*[cube.pop_in(cubie) for cubie in cubies], run_time=0.58)
        self.wait(0.3)

        # 「我们固定各中心块的朝向，并用大写字母表示魔方的六个面： U D L R F B」
        center_note = ctext("固定各中心块朝向", 34, color=YELLOW)
        center_note.move_to(RIGHT * 3.2 + UP * 1.28)
        self.fix(center_note)
        self.play(
            FadeOut(cubie_label),
            FadeOut(counts),
            FadeIn(center_note),
            cube.focus(cube.center_cubies()),
            run_time=0.65,
        )
        self.wait(0.65)
        self.play(cube.reset_look(), FadeOut(center_note), run_time=0.5)

        face_top = ctext("U  up · 上面", 34)
        face_top.move_to(RIGHT * 2.2 + UP * 1.28)
        face_panel = VGroup(face_top)
        for text in ("D  down · 下面", "L  left · 左面", "R  right · 右面", "F  front · 前面", "B  back · 后面"):
            face_panel.add(
                ctext(text, 34).next_to(face_panel[-1], DOWN, aligned_edge=LEFT, buff=0.28)
            )
        self.fix(face_panel)
        self.play(FadeIn(face_panel, lag_ratio=0.12), run_time=0.65)
        for index, face in enumerate("UDLRFB"):
            if index:
                self.play(
                    cube.reset_look(),
                    face_panel[index - 1].animate.set_color(PAPER),
                    run_time=0.24,
                )
            self.play(
                cube.focus(cube.layer(face)),
                face_panel[index].animate.set_color(YELLOW),
                run_time=0.28,
            )
            # self.wait(0.28)
        self.play(
            cube.reset_look(),
            face_panel[-1].animate.set_color(PAPER),
            run_time=0.35,
        )
        self.wait(0.25)

        # 「小写字母用来标记具体的 方块 cubies。例如 urf …… ur ……」
        urf_corner = cube.cubie(0, 0, 2)
        ur_edge = cube.cubie(1, 0, 2)
        urf_label = ctext("u r f : 位于 U R F 三面的 角块", 34)
        urf_label.move_to(RIGHT * 3.2 + UP * 1.28)
        ur_label = ctext("u r : 位于 U R 两面的 棱块", 34)
        ur_label.next_to(urf_label, DOWN, aligned_edge=LEFT, buff=0.88)
        lowercase = VGroup(urf_label, ur_label)
        self.fix(lowercase)

        self.play(FadeOut(face_panel), run_time=0.35)
        self.play(cube.focus([urf_corner]), FadeIn(urf_label), run_time=0.8)
        self.wait(0.35)
        for index, face in enumerate("URF"):
            if index:
                self.play(cube.reset_look(), run_time=0.1)
            self.play(cube.focus(cube.layer(face)), run_time=0.42)
            self.wait(0.28)
        self.play(cube.reset_look(), run_time=0.35)
        self.play(cube.focus([ur_edge]), FadeIn(ur_label), run_time=0.55)
        self.wait(0.35)
        for index, face in enumerate("UR"):
            if index:
                self.play(cube.reset_look(), run_time=0.1)
            self.play(cube.focus(cube.layer(face)), run_time=0.42)
            self.wait(0.28)
        self.play(cube.reset_look(), run_time=0.35)

        # 「我们也用大写字母表示转动动作。比如 R 表示把右面顺时针旋转 90 度。」
        self.play(
            FadeOut(lowercase),
            run_time=0.55,
        )
        r_note = VGroup(
            formula(r"R", font_size=52),
            ctext("右面顺时针 90°", 34),
        ).arrange(RIGHT, buff=0.28)
        r_note.move_to(RIGHT * 3.2 + UP * 1.28)
        self.fix(r_note)
        self.play(FadeIn(r_note), run_time=0.45)
        self.wait(0.35)
        self.play(CubeMove(cube, "R"), run_time=0.75)
        self.wait(0.5)

        # 「逆时针旋转记作 R^(-1) …… 我们也经常写作 R'.」
        rprime = VGroup(
            formula(r"R^{-1}/R'", font_size=52),
            ctext("右面逆时针旋转 90°", 34),
        ).arrange(RIGHT, buff=0.28)
        rprime.move_to(RIGHT * 3.2 + UP * 0.35)
        self.fix(rprime)
        self.play(FadeIn(rprime), run_time=0.45)
        self.wait(0.35)
        self.play(CubeMove(cube, "R'"), run_time=0.65)
        self.wait(0.5)

        # 「旋转一个面两次，即 180 度记作 R^2。」
        r2 = VGroup(
            formula(r"R^2", font_size=52),
            ctext("右面顺时针 180°", 34),
        ).arrange(RIGHT, buff=0.28)
        r2.move_to(RIGHT * 3.2 + DOWN * 0.75)
        self.fix(r2)
        self.play(FadeIn(r2), run_time=0.45)
        self.wait(0.35)
        self.play(CubeMove(cube, "R2"), run_time=0.65)
        self.wait(0.5)

        # 「在整个课程中，我们按照从左到右的顺序执行动作。例如 U D F ……」
        rotation_notes = VGroup(r_note, rprime, r2)
        self.play(FadeOut(rotation_notes), cube.reset_look(), run_time=0.55)
        cube.do_moves("R2")

        seq_title = ctext("从左到右执行", 34)
        seq_title.move_to(RIGHT * 3.2 + UP * 1.28)
        seq = move_sequence_badge("U D F", font_size=44)
        seq.next_to(seq_title, DOWN, aligned_edge=LEFT, buff=1.0)
        self.fix(seq_title, seq)
        self.play(FadeIn(seq_title), FadeIn(seq), run_time=0.45)
        for index, move in enumerate(("U", "D", "F")):
            self.play(
                Indicate(seq[1][2 * index], color=YELLOW, scale_factor=1.08),
                CubeMove(cube, move),
                run_time=0.48,
            )
            self.wait(0.5)
        cube.do_moves(invert_move_sequence("U D F"))

        # 「这个约定很重要，因为魔方动作通常不满足交换律。 R U != U R。」
        seq_block = VGroup(seq_title, seq)

        # Final comparison layout. Cube positions are 3D screen points, while
        # badge positions are fixed 2D coordinates using the same x values.
        split_scale = 0.72
        split_size = 2.0 * split_scale
        left_column_x = -2.1
        right_column_x = 2.1
        cube_row_y = 0.75
        badge_row_y = -1.15
        left_cube_pos = self.screen_point(left_column_x, cube_row_y)
        right_cube_pos = self.screen_point(right_column_x, cube_row_y)

        self.play(
            FadeOut(seq_block),
            cube.animate.scale(split_scale).move_to(left_cube_pos),
            run_time=0.55,
        )

        cube_b = RubiksCube(total_size=split_size)
        cube_b.move_to(right_cube_pos)
        self.add_cube(cube_b)
        self.remove(cube_b)

        ru_badge = move_sequence_badge("R U", font_size=44)
        ur_badge = move_sequence_badge("U R", font_size=44)
        ru_badge.move_to(np.array([left_column_x, badge_row_y, 0.0]))
        ur_badge.move_to(np.array([right_column_x, badge_row_y, 0.0]))
        self.fix(ru_badge, ur_badge)

        self.play(FadeIn(cube_b), run_time=0.55)
        self.play(FadeIn(ru_badge), FadeIn(ur_badge), run_time=0.45)
        self.wait(0.5)
        self.play(Indicate(ru_badge, color=YELLOW, scale_factor=1.06), run_time=0.65)
        self.play(CubeMove(cube, "R"), run_time=0.42)
        self.play(CubeMove(cube, "U"), run_time=0.42)
        self.wait(0.5)
        self.play(Indicate(ur_badge, color=YELLOW, scale_factor=1.06), run_time=0.65)
        self.play(CubeMove(cube_b, "U"), run_time=0.42)
        self.play(CubeMove(cube_b, "R"), run_time=0.42)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# Definition 2: Rubik's Cube Group
# ---------------------------------------------------------------------------


class RubiksCubeGroupScene(RubiksCubeScene):
    """Definition 2：魔方群的严格定义与四条公理验证。"""

    def construct(self) -> None:
        background = image_background("kraft_paper_green_003.png")
        background.scale(1.08)
        self.add_fixed_in_frame_mobjects(background)

        # 「现在我们严格定义三阶魔方群。」
        title = ctext("定义三阶魔方群", 54, color=YELLOW)
        title.move_to(UP * 3.2)
        self.fix(title)
        self.play(FadeIn(title), run_time=0.55)

        # 「由六个基本面旋转动作 U, D, L, R, F, B 以及它们的逆动作……」
        generators = formula(r"U\ ,D\ ,L\ ,R\ ,F\ ,B\ ", font_size=50, color=CHARCOAL)
        inverse_generators = formula(r"U',D',L',R',F',B'", font_size=50, color=CHARCOAL)
        generators.move_to(np.array([0.0, 1.55, 0.0]))
        inverse_generators.move_to(np.array([0.0, 0.62, 0.0]))

        # Use the existing definition badge, then append the move sequence as
        # MathTex so primes and powers retain proper mathematical typography.
        sequence_definition = def_heading("动作序列", y=-0.2, font_size=34, height=0.9)
        sequence_formula = formula(r"U\ F\ D'\ L^2\ B", font_size=38)
        sequence_content = VGroup(sequence_definition[1], sequence_formula).arrange(RIGHT, buff=0.38)
        sequence_definition[0].stretch_to_fit_width(sequence_content.width + 0.86)
        sequence_content.move_to(sequence_definition[0].get_center())
        sequence_definition = VGroup(sequence_definition[0], sequence_content)

        self.fix(generators, inverse_generators, sequence_definition)
        self.play(FadeIn(generators, shift=DOWN * 0.08), run_time=0.5)
        self.play(FadeIn(inverse_generators, shift=DOWN * 0.08), run_time=0.5)
        self.play(
            FadeOut(title),
            generators.animate.move_to(np.array([0.0, 2.35, 0.0])),
            inverse_generators.animate.move_to(np.array([0.0, 1.4, 0.0])),
            run_time=0.55,
        )
        self.play(FadeIn(sequence_definition, shift=DOWN * 0.08), run_time=0.55)
        self.wait(0.55)
        self.play(
            FadeOut(generators),
            FadeOut(inverse_generators),
            FadeOut(sequence_definition),
            run_time=0.5,
        )

        # Compare two equivalent move sequences. Cubes are 3D objects, so
        # their layout uses screen_point(); fixed badges use ordinary 2D
        # coordinates and therefore stay aligned below the projected cubes.
        cube_size = 2.0
        left_column_x = -2.2
        right_column_x = 2.2
        cube_row_y = 1.15
        badge_row_y = -1.25

        left_cube = RubiksCube(total_size=cube_size)
        right_cube = RubiksCube(total_size=cube_size)
        left_cube.move_to(self.screen_point(left_column_x, cube_row_y))
        right_cube.move_to(self.screen_point(right_column_x, cube_row_y))
        self.add_cube(left_cube)
        self.add_cube(right_cube)
        self.remove(left_cube, right_cube)

        left_badge = move_sequence_badge("R'", font_size=44)
        right_badge = move_sequence_badge(r"R^3", font_size=44)
        left_badge.move_to(np.array([left_column_x, badge_row_y, 0.0]))
        right_badge.move_to(np.array([right_column_x, badge_row_y, 0.0]))
        self.fix(left_badge, right_badge)

        self.play(
            FadeIn(left_cube),
            FadeIn(right_cube),
            FadeIn(left_badge),
            FadeIn(right_badge),
            run_time=0.6,
        )
        self.play(
            Indicate(left_badge[0], color=YELLOW, scale_factor=1.06),
            Indicate(right_badge[0], color=YELLOW, scale_factor=1.06),
            AnimationGroup(
                CubeMove(left_cube, "R'", run_time=1.2),
                Succession(
                    CubeMove(right_cube, "R", run_time=0.4),
                    CubeMove(right_cube, "R", run_time=0.4),
                    CubeMove(right_cube, "R", run_time=0.4),
                ),
                lag_ratio=0,
            ),
            run_time=1.2,
        )
        self.wait(0.65)

        # R restores both cubes because each currently represents R'. Then
        # replace the badges and compare two commuting opposite-face turns.
        next_left_badge = move_sequence_badge("L R", font_size=44)
        next_right_badge = move_sequence_badge("R L", font_size=44)
        next_left_badge.move_to(left_badge)
        next_right_badge.move_to(right_badge)
        self.fix(next_left_badge, next_right_badge)
        # Badge tex lengths differ (R' / R^3 → L R / R L); morph transforms
        # scramble glyphs, so swap with FadeOut / FadeIn instead.
        self.play(
            CubeMove(left_cube, "R"),
            CubeMove(right_cube, "R"),
            FadeOut(left_badge),
            FadeOut(right_badge),
            FadeIn(next_left_badge),
            FadeIn(next_right_badge),
            run_time=0.65,
        )
        left_badge = next_left_badge
        right_badge = next_right_badge
        self.play(
            Indicate(left_badge[0], color=YELLOW, scale_factor=1.06),
            Indicate(right_badge[0], color=YELLOW, scale_factor=1.06),
            AnimationGroup(
                Succession(
                    CubeMove(left_cube, "L", run_time=0.48),
                    CubeMove(left_cube, "R", run_time=0.48),
                ),
                Succession(
                    CubeMove(right_cube, "R", run_time=0.48),
                    CubeMove(right_cube, "L", run_time=0.48),
                ),
                lag_ratio=0,
            ),
            run_time=0.96,
        )
        self.wait(0.65)

        self.play(
            FadeOut(left_cube),
            FadeOut(right_cube),
            FadeOut(left_badge),
            FadeOut(right_badge),
            run_time=0.5,
        )
        self.remove_cube(left_cube)
        self.remove_cube(right_cube)

        # Different strings can represent the same element of the cube group.
        equivalent_formulas = VGroup(
            formula(r"R'=R^3", font_size=56, color=CHARCOAL),
            formula(r"LR=RL", font_size=56, color=CHARCOAL),
        ).arrange(DOWN, buff=0.48)
        equivalent_formulas.move_to(np.array([0.0, 0.35, 0.0]))
        self.fix(equivalent_formulas)
        self.play(LaggedStart(*[Write(line) for line in equivalent_formulas], lag_ratio=0.25), run_time=1.0)
        self.wait(0.65)
        self.play(FadeOut(equivalent_formulas), run_time=0.45)

        # Define the set and its operation. The highlighted badge makes
        # “动作序列” read as the object being defined, not ordinary prose.
        # Chinese in the badge; (G, \ast) as MathTex so * matches earlier scenes.
        cube_group_heading = def_heading("三阶魔方群", y=2.05, font_size=34, height=0.88)
        group_notation = formula(r"(G,", r"\ast", r")", font_size=48)
        heading_content = VGroup(cube_group_heading[1], group_notation).arrange(RIGHT, buff=0.28)
        cube_group_heading[0].stretch_to_fit_width(heading_content.width + 0.86)
        heading_content.move_to(cube_group_heading[0].get_center())
        cube_group_heading = VGroup(cube_group_heading[0], heading_content)

        group_symbol = formula(r"G:", font_size=48, color=CHARCOAL)
        brace_left = formula(r"\{", font_size=48, color=CHARCOAL)
        equiv_word = ctext("等价的", 34, color=CHARCOAL)
        sequence_set = course_badge("动作序列", preset="definition", font_size=34, height=0.82)
        brace_right = formula(r"\}", font_size=48, color=CHARCOAL)
        # Match GroupAxiomsScene: LaTeX \ast, not ASCII *
        star_colon = formula(r"\ast", r":", font_size=48, color=CHARCOAL)
        operation_text = ctext("自然结合两个动作序列", 34, color=CHARCOAL)
        set_part = VGroup(
            group_symbol,
            brace_left,
            equiv_word,
            sequence_set,
            brace_right,
        ).arrange(RIGHT, buff=0.22)
        op_part = VGroup(star_colon, operation_text).arrange(RIGHT, buff=0.18)
        group_definition = VGroup(set_part, op_part).arrange(RIGHT, buff=0.55)
        group_definition.move_to(np.array([0.0, 0.55, 0.0]))

        compose = formula(r"UF", r"\ast", r"LB", r"=", r"UFLB", font_size=50, color=CHARCOAL)
        # compose[1].set_color(YELLOW)
        compose.move_to(np.array([0.0, -1.2, 0.0]))
        self.fix(cube_group_heading, group_definition, compose)

        self.play(FadeIn(cube_group_heading, shift=DOWN * 0.08), run_time=0.55)
        self.play(FadeIn(group_definition, shift=DOWN * 0.08), run_time=0.65)
        self.wait(0.55)
        self.play(Write(compose), run_time=0.75)
        self.wait(0.65)

        # 「下面我们验证它符合群的四条公理。」
        self.play(
            FadeOut(cube_group_heading),
            FadeOut(group_definition),
            FadeOut(compose),
            run_time=0.5,
        )

        # Use one shared blue paper for all four axioms. It drops over the
        # green definition background, matching the transition used earlier.
        axiom_background = image_background("kraft_paper_blue_003.png")
        axiom_background.scale(1.08).shift(UP * 10)
        self.add_fixed_in_frame_mobjects(axiom_background)
        play_paper_drop(self, axiom_background, drop=10.0)
        self.remove(background)
        background = axiom_background

        # Progress chips: same Chinese labels as GroupAxiomsScene, slightly taller / lower.
        def cube_axiom_progress(active_index: int) -> VGroup:
            chips = VGroup()
            for index, name in enumerate(AXIOM_NAMES):
                active = index == active_index
                text = Text(
                    f"公理{index + 1}  {name}",
                    font=FONT,
                    font_size=32,
                    color=CHARCOAL if active else PAPER,
                    weight=BOLD if active else NORMAL,
                )
                box = RoundedRectangle(
                    width=max(3.45, text.width + 0.48),
                    height=0.88,
                    corner_radius=0.1,
                    fill_color=YELLOW if active else CHARCOAL,
                    fill_opacity=0.96 if active else 0.48,
                    stroke_color=PAPER,
                    stroke_width=1.4,
                )
                text.move_to(box.get_center())
                chips.add(VGroup(box, text))
            chips.arrange(RIGHT, buff=0.18)
            chips.move_to(UP * 3.25)
            return chips

        def slash_mark(token: MathTex) -> Line:
            return Line(
                token.get_corner(DOWN + LEFT) + UP * 0.08 + RIGHT * 0.06,
                token.get_corner(UP + RIGHT) + DOWN * 0.08 + LEFT * 0.06,
                color=BLACK,
                stroke_width=4.5,
            )

        def move_row(tokens: tuple[str, ...], *, font_size: int = 52) -> MathTex:
            # One MathTex gives every token the same TeX baseline. Add spacing
            # inside the first arguments so each token remains independently
            # addressable for highlighting, swapping, and cancellation.
            parts = [
                moves_to_latex(token) + (r"\quad" if index < len(tokens) - 1 else "")
                for index, token in enumerate(tokens)
            ]
            return formula(*parts, font_size=font_size, color=CHARCOAL)

        previous: VGroup | None = None

        # --- 公理一：封闭性 ---
        progress0 = cube_axiom_progress(0)
        closure = formula(r"UF", r"\ast", r"LB", r"=", r"UFLB", font_size=50, color=CHARCOAL)
        # closure[1].set_color(YELLOW)
        closure.move_to(ORIGIN + UP * 0.2)
        panel0 = VGroup(progress0, closure)
        self.fix(panel0)
        self.play(FadeIn(panel0), run_time=0.55)
        self.wait(0.85)
        previous = panel0

        # --- 公理二：结合律 ---
        progress1 = cube_axiom_progress(1)
        assoc_left = formula(
            r"(RD\ast L'F)\ast F^2L=RD\ast(L'F\ast F^2L)",
            font_size=50,
            color=CHARCOAL,
        )
        assoc_left.move_to(UP * 0.25)
        panel1 = VGroup(progress1, assoc_left)
        self.fix(panel1)
        self.play(
            FadeOut(previous),
            FadeIn(panel1),
            run_time=0.55,
        )
        self.wait(0.7)
        assoc_right = formula(r"=RDL'F^3L", font_size=50, color=CHARCOAL)
        assoc_target = assoc_left.copy().shift(LEFT * 1.35)
        assoc_right.next_to(assoc_target, RIGHT, buff=0.22)
        assoc_right.set_y(assoc_left.get_y())
        self.fix(assoc_right)
        self.play(
            assoc_left.animate.move_to(assoc_target),
            FadeIn(assoc_right, shift=LEFT * 0.12),
            run_time=0.75,
        )
        self.wait(0.85)
        previous = VGroup(progress1, assoc_left, assoc_right)

        # --- 公理三：单位元 ---
        progress2 = cube_axiom_progress(2)
        identity_e = formula(r"e", font_size=56, color=CHARCOAL)
        identity_e.move_to(UP * 0.25)
        panel2 = VGroup(progress2, identity_e)
        self.fix(panel2)
        self.play(
            FadeOut(previous),
            FadeIn(panel2),
            run_time=0.55,
        )
        self.wait(0.45)

        identity_pair_target = formula(r"e", r"=R^4", font_size=56, color=CHARCOAL)
        identity_pair_target.move_to(UP * 0.25)
        identity_r4 = identity_pair_target[1]
        self.fix(identity_r4)
        self.play(
            identity_e.animate.move_to(identity_pair_target[0]),
            FadeIn(identity_r4, shift=LEFT * 0.1),
            run_time=0.55,
        )
        self.wait(0.55)

        identity_full_target = formula(r"e", r"=R^4", r"=RR'", font_size=56, color=CHARCOAL)
        identity_full_target.move_to(UP * 0.25)
        identity_rr = identity_full_target[2]
        self.fix(identity_rr)
        self.play(
            identity_e.animate.move_to(identity_full_target[0]),
            identity_r4.animate.move_to(identity_full_target[1]),
            FadeIn(identity_rr, shift=LEFT * 0.1),
            run_time=0.55,
        )
        self.wait(0.85)
        previous = VGroup(progress2, identity_e, identity_r4, identity_rr)

        # --- 公理四：逆元 ---
        progress3 = cube_axiom_progress(3)
        top_row = move_row(("F", "D'", "R"))
        top_row.move_to(UP * 0.85)
        panel3 = VGroup(progress3, top_row)
        self.fix(panel3)
        self.play(
            FadeOut(previous),
            FadeIn(panel3),
            run_time=0.55,
        )
        self.wait(0.45)

        # Copies of fixed-in-frame formulas are not fixed automatically. Keep
        # every object in this derivation on the 2D overlay plane so the 3D
        # camera cannot flatten or skew the letters.
        bottom_row = top_row.copy()
        self.fix(bottom_row)
        self.add(bottom_row)
        self.play(bottom_row.animate.shift(DOWN * 1.55), run_time=0.55)
        self.wait(0.3)

        # Each letter → its inverse (same order): F D' R → F' D R'
        inverted_bottom = move_row(("F'", "D", "R'"))
        inverted_bottom.move_to(bottom_row)
        self.fix(inverted_bottom)
        source_tokens = list(bottom_row)
        target_tokens = list(inverted_bottom)
        for source, target in zip(source_tokens, target_tokens, strict=True):
            self.play(Indicate(source, color=YELLOW, scale_factor=1.08), run_time=0.42)
            self.play(FadeOut(source), FadeIn(target), run_time=0.16)
            bottom_row.remove(source)
            self.remove(source)

        self.remove(bottom_row)
        self.remove(*target_tokens)
        bottom_row = inverted_bottom
        self.add(bottom_row)
        self.wait(0.35)

        # Reverse order: F' D R' → R' D F'
        left_token, middle_token, right_token = bottom_row
        left_target = np.array(right_token.get_center())
        right_target = np.array(left_token.get_center())
        self.play(
            left_token.animate(path_arc=-PI / 2).move_to(left_target),
            right_token.animate(path_arc=PI / 2).move_to(right_target),
            run_time=0.7,
        )
        bottom_row = VGroup(right_token, middle_token, left_token)
        self.fix(bottom_row)
        self.add(bottom_row)
        self.wait(0.45)

        # Cross-append with *: top = FD'R * R'DF' , bottom = R'DF' * FD'R
        star_top = formula(r"\ast", font_size=52, color=CHARCOAL)
        star_bot = formula(r"\ast", font_size=52, color=CHARCOAL)
        top_right = bottom_row.copy()
        bot_right = top_row.copy()
        top_assembled = VGroup(top_row.copy(), star_top.copy(), bottom_row.copy())
        top_assembled.arrange(RIGHT, buff=0.32).move_to(UP * 0.85)
        bot_assembled = VGroup(bottom_row.copy(), star_bot.copy(), top_row.copy())
        bot_assembled.arrange(RIGHT, buff=0.32).move_to(DOWN * 0.7)
        self.fix(star_top, star_bot, top_right, bot_right)
        self.add(star_top, star_bot, top_right, bot_right)
        star_top.move_to(top_row.get_right() + RIGHT * 0.5)
        star_bot.move_to(bottom_row.get_right() + RIGHT * 0.5)
        top_right.move_to(bottom_row.get_center())
        bot_right.move_to(top_row.get_center())
        self.play(
            top_row.animate.move_to(top_assembled[0].get_center()),
            star_top.animate.move_to(top_assembled[1].get_center()),
            top_right.animate.move_to(top_assembled[2].get_center()),
            bottom_row.animate.move_to(bot_assembled[0].get_center()),
            star_bot.animate.move_to(bot_assembled[1].get_center()),
            bot_right.animate.move_to(bot_assembled[2].get_center()),
            run_time=0.85,
        )
        self.wait(0.45)

        top_left, top_right_side = top_row, top_right
        bot_left, bot_right_side = bottom_row, bot_right

        # Cancel nearest-to-* pairs three times on both rows together
        for step in range(3):
            tl_tok = top_left[-1]
            tr_tok = top_right_side[0]
            bl_tok = bot_left[-1]
            br_tok = bot_right_side[0]
            slashes = VGroup(
                slash_mark(tl_tok),
                slash_mark(tr_tok),
                slash_mark(bl_tok),
                slash_mark(br_tok),
            )
            self.fix(slashes)
            self.play(*[Create(mark) for mark in slashes], run_time=0.4)
            self.play(
                FadeOut(tl_tok),
                FadeOut(tr_tok),
                FadeOut(bl_tok),
                FadeOut(br_tok),
                FadeOut(slashes),
                run_time=0.45,
            )
            top_left.remove(tl_tok)
            top_right_side.remove(tr_tok)
            bot_left.remove(bl_tok)
            bot_right_side.remove(br_tok)
            self.remove(tl_tok, tr_tok, bl_tok, br_tok)

            if step < 2:
                # Shift only along x. This preserves the common TeX baseline
                # established by move_row() while closing the cancelled gap.
                top_left_dx = star_top.get_left()[0] - 0.32 - top_left.get_right()[0]
                top_right_dx = star_top.get_right()[0] + 0.32 - top_right_side.get_left()[0]
                bot_left_dx = star_bot.get_left()[0] - 0.32 - bot_left.get_right()[0]
                bot_right_dx = star_bot.get_right()[0] + 0.32 - bot_right_side.get_left()[0]
                self.play(
                    *[token.animate.shift(RIGHT * top_left_dx) for token in top_left],
                    *[token.animate.shift(RIGHT * top_right_dx) for token in top_right_side],
                    *[token.animate.shift(RIGHT * bot_left_dx) for token in bot_left],
                    *[token.animate.shift(RIGHT * bot_right_dx) for token in bot_right_side],
                    run_time=0.4,
                )
            else:
                eq_top = formula(r"=e", font_size=56, color=CHARCOAL)
                eq_bot = formula(r"=e", font_size=56, color=CHARCOAL)
                eq_top.move_to(star_top)
                eq_bot.move_to(star_bot)
                self.fix(eq_top, eq_bot)
                self.play(
                    FadeOut(star_top),
                    FadeOut(star_bot),
                    FadeIn(eq_top),
                    FadeIn(eq_bot),
                    run_time=0.5,
                )
                previous = VGroup(progress3, eq_top, eq_bot)

        self.wait(0.85)

        # 「所以三阶魔方群确实符合一个群结构。可以看到，三阶魔方群中的元素与魔方状态是一一对应的。」
        # Reuse the earlier definition layout (badge + G / * lines), then the correspondence.
        conclusion_heading = def_heading("三阶魔方群", y=2.15, font_size=34, height=0.88)
        conclusion_notation = formula(r"(G,", r"\ast", r")", font_size=48)
        conclusion_heading_content = VGroup(
            conclusion_heading[1],
            conclusion_notation,
        ).arrange(RIGHT, buff=0.28)
        conclusion_heading[0].stretch_to_fit_width(conclusion_heading_content.width + 0.86)
        conclusion_heading_content.move_to(conclusion_heading[0].get_center())
        conclusion_heading = VGroup(conclusion_heading[0], conclusion_heading_content)

        conclusion_set = VGroup(
            formula(r"G:", font_size=48, color=CHARCOAL),
            formula(r"\{", font_size=48, color=CHARCOAL),
            ctext("等价的", 34, color=CHARCOAL),
            course_badge("动作序列", preset="definition", font_size=34, height=0.82),
            formula(r"\}", font_size=48, color=CHARCOAL),
        ).arrange(RIGHT, buff=0.22)
        conclusion_op = VGroup(
            formula(r"\ast", r":", font_size=48, color=CHARCOAL),
            ctext("自然结合两个动作序列", 34, color=CHARCOAL),
        ).arrange(RIGHT, buff=0.18)
        conclusion_definition = VGroup(conclusion_set, conclusion_op).arrange(RIGHT, buff=0.55)
        conclusion_definition.move_to(UP * 0.75)
        correspondence = ctext("群元素 ↔ 合法魔方状态", 36, color=YELLOW)
        correspondence.move_to(DOWN * 1.0)
        definition_block = VGroup(conclusion_heading, conclusion_definition)
        self.fix(definition_block, correspondence)
        self.play(FadeOut(previous), FadeIn(definition_block), run_time=0.65)
        self.wait(0.7)
        self.play(FadeIn(correspondence, shift=UP * 0.08), run_time=0.55)
        self.wait(0.8)


# ---------------------------------------------------------------------------
# Theorem: repetition in a finite group
# ---------------------------------------------------------------------------


class FiniteGroupTheoremScene(RubiksCubeScene):
    """Theorem + Proof：有限群中 g^n = e。"""

    def construct(self) -> None:
        background = image_background("kraft_paper_002.png")
        background.scale(1.04)
        self.add_fixed_in_frame_mobjects(background)

        theorem_accent = MAGENTA

        # Compose a full multi-line theorem, then let the shared badge helper
        # provide the purple frame and padding.
        theorem_prefix = ctext("定理 1：", 32, color=YELLOW)
        theorem_first_sentence = VGroup(
            ctext("设", 31, color=PAPER),
            formula(r"(G,\ast)", font_size=43, color=PAPER),
            ctext("是一个有限群，且", 31, color=PAPER),
            formula(r"g\in G", font_size=43, color=PAPER),
            ctext("。", 31, color=PAPER),
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        theorem_line_one = VGroup(theorem_prefix, theorem_first_sentence).arrange(
            RIGHT,
            buff=0.22,
            aligned_edge=DOWN,
        )
        theorem_line_two = VGroup(
            ctext("那么存在一个正整数", 31, color=PAPER),
            formula(r"n", font_size=43, color=PAPER),
            ctext("，使得", 31, color=PAPER),
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        theorem_line_three = VGroup(
            formula(r"g^n=e", font_size=52, color=PAPER),
            ctext("。", 31, color=PAPER),
        ).arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
        theorem_content = VGroup(
            theorem_line_one,
            theorem_line_two,
            theorem_line_three,
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        theorem_line_three.set_x(theorem_content.get_center()[0])
        theorem_block = course_badge(
            theorem_content,
            preset="theorem",
            h_padding=0.62,
            v_padding=0.42,
        )
        theorem_block.move_to(UP * 0.55)
        theorem_box = theorem_block[0]
        self.fix(
            theorem_box,
            theorem_prefix,
            theorem_first_sentence,
            theorem_line_two,
            theorem_line_three,
        )

        self.play(FadeIn(theorem_box), Write(theorem_prefix), run_time=0.55)
        self.play(Write(theorem_first_sentence), run_time=0.9)
        self.play(Write(theorem_line_two), run_time=0.75)
        self.play(Write(theorem_line_three), run_time=0.55)
        self.wait(1.0)

        proof_badge = proof_heading(
            None,
            y=3.15,
            font_size=34,
            height=0.78,
        )
        proof_badge.to_edge(LEFT, buff=0.92)

        def proof_row(content, y: float) -> VGroup:
            marker = Circle(
                radius=0.065,
                fill_color=theorem_accent,
                fill_opacity=1,
                stroke_width=0,
            )
            row = VGroup(marker, content).arrange(RIGHT, buff=0.34)
            row.to_edge(LEFT, buff=1.15)
            row.set_y(y)
            return row

        size_content = formula(r"|G|=N", font_size=48, color=CHARCOAL)
        size_row = proof_row(size_content, 2.10)
        notation_content = VGroup(
            formula(r"|G|", font_size=42, color=YELLOW),
            ctext("代表群中元素的数量", 30, color=PAPER),
        ).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        notation = course_badge(
            notation_content,
            preset="notation",
            height=0.66,
        )
        notation.move_to(UP * 2.10 + RIGHT * 1.85)

        terms_note = VGroup(
            ctext("共", 28, color=CHARCOAL),
            formula(r"N+1", font_size=38, color=CHARCOAL),
            ctext("个元素", 28, color=CHARCOAL),
        ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
        powers_content = VGroup(
            ctext("考虑", 30, color=CHARCOAL),
            formula(r"\{e,\ g,\ g^2,\ldots,\ g^N\}", font_size=43, color=CHARCOAL),
            terms_note,
        ).arrange(RIGHT, buff=0.32, aligned_edge=DOWN)
        powers_row = proof_row(powers_content, 1.15)
        powers_row[0].shift(DOWN * 0.09)

        repeated_inequality = formula(r"N+1>|G|", font_size=39, color=CHARCOAL)
        repeated_indices = formula(r"0\le i<j\le N", font_size=39, color=CHARCOAL)
        repeated_equality = formula(r"g^i", r"=", r"g^j", font_size=39, color=CHARCOAL)
        repeated_content = VGroup(
            ctext("因为", 30, color=CHARCOAL),
            repeated_inequality,
            ctext("，所以存在", 30, color=CHARCOAL),
            repeated_indices,
            ctext("，使得", 30, color=CHARCOAL),
            repeated_equality,
        ).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        repeated_row = proof_row(repeated_content, 0.15)

        copied_equality = formula(r"g^i", r"=", r"g^j", font_size=39, color=CHARCOAL)
        multiplied_expression = formula(
            r"g^{-i}\ast",
            r"g^i",
            r"=",
            r"g^{-i}\ast",
            r"g^j",
            r"\Longrightarrow",
            r"e=g^{j-i}",
            font_size=40,
            color=CHARCOAL,
        )
        left_multiplier = multiplied_expression[0]
        target_left_power = multiplied_expression[1]
        target_equals = multiplied_expression[2]
        right_multiplier = multiplied_expression[3]
        target_right_power = multiplied_expression[4]
        deduction_arrow = multiplied_expression[5]
        simplified_expression = multiplied_expression[6]
        multiplied_row = proof_row(multiplied_expression, -0.90)
        multiplied_row[0].shift(DOWN * 0.09)

        product_expression = VGroup(*multiplied_expression[:5])
        copied_target = copied_equality.copy()
        copied_target.move_to(product_expression)
        copied_target.align_to(product_expression, LEFT)
        copied_equality.move_to(repeated_equality)

        final_content = VGroup(
            ctext("因为", 29, color=CHARCOAL),
            formula(r"j-i>0", font_size=42, color=CHARCOAL),
            ctext("，令", 29, color=CHARCOAL),
            formula(r"n=j-i", font_size=42, color=CHARCOAL),
            ctext("，则有", 29, color=CHARCOAL),
            formula(r"g^n=e", font_size=48, color=theorem_accent),
        ).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
        final_row = proof_row(final_content, -2.05)

        self.fix(
            proof_badge,
            size_row,
            notation,
            powers_row,
            repeated_row,
            multiplied_row[0],
            copied_equality,
            left_multiplier,
            right_multiplier,
            deduction_arrow,
            simplified_expression,
            final_row,
        )

        self.play(
            FadeOut(theorem_box),
            FadeOut(theorem_prefix),
            FadeOut(theorem_first_sentence),
            FadeOut(theorem_line_two),
            FadeOut(theorem_line_three),
            FadeIn(proof_badge, shift=RIGHT * 0.08),
            run_time=0.6,
        )
        self.play(Write(size_row), run_time=0.65)
        self.wait(0.4)
        self.play(FadeIn(notation, shift=LEFT * 0.08), run_time=0.55)
        self.wait(0.85)
        self.play(FadeOut(notation), run_time=0.3)
        self.wait(0.15)
        self.play(Write(powers_row), run_time=0.8)
        self.wait(0.4)
        self.play(Write(repeated_row), run_time=1.05)
        self.wait(0.4)

        # Peel a copy of g^i=g^j away from the third row and place it on the
        # next line. Keeping its left edge fixed makes the equals sign move
        # right when the two multipliers appear.
        self.add_fixed_in_frame_mobjects(copied_equality)
        self.play(
            Write(multiplied_row[0]),
            copied_equality.animate.move_to(copied_target),
            run_time=0.75,
        )
        self.wait(0.25)
        self.play(
            FadeIn(left_multiplier),
            copied_equality[0].animate.move_to(target_left_power),
            copied_equality[1].animate.move_to(target_equals),
            FadeIn(right_multiplier),
            copied_equality[2].animate.move_to(target_right_power),
            run_time=0.8,
        )
        self.wait(0.25)
        self.play(
            FadeIn(deduction_arrow, shift=LEFT * 0.05),
            FadeIn(simplified_expression, shift=LEFT * 0.08),
            run_time=0.6,
        )
        self.wait(0.4)
        self.play(Write(final_row), run_time=0.85)

        # Place the standard hollow proof box close to the final conclusion.
        qed_box = RoundedRectangle(
            width=0.34,
            height=0.34,
            corner_radius=0.015,
            fill_opacity=0,
            stroke_color=CHARCOAL,
            stroke_width=3.2,
        )
        qed_box.next_to(final_content[-1], DOWN, buff=0.30, aligned_edge=RIGHT)
        qed_box.shift(RIGHT * 1.05)
        qed_box.shift(RIGHT * (4 * qed_box.width))
        self.fix(qed_box)
        self.play(GrowFromCenter(qed_box), run_time=0.45)
        self.wait(1.0)

        # Return to |G|=N, then replace the proof with a concrete upper-bound
        # count: 8 corner positions/orientations and 12 edge positions/flips.
        self.play(Indicate(size_row, color=YELLOW, scale_factor=1.08), run_time=0.8)
        self.wait(0.55)
        proof_page = (
            proof_badge,
            size_row,
            powers_row,
            repeated_row,
            multiplied_row[0],
            copied_equality,
            left_multiplier,
            right_multiplier,
            deduction_arrow,
            simplified_expression,
            final_row,
            qed_box,
        )
        self.play(*[FadeOut(mobject) for mobject in proof_page], run_time=0.7)

        # 3D objects use screen_point() so they land at the intended projected
        # screen position under the RubiksCubeScene camera.


        # cube = self.add_cube(RubiksCube(total_size=2.0).move_to(self.screen_point(-3.5, 1.88)))
        # self.play(FadeIn(bridge), FadeIn(cube), run_time=0.65)
        # self.wait(0.55)


        cube = RubiksCube(total_size=2.5)
        cube.move_to(self.screen_point(-4.0, 0.5))
        self.add_cube(cube)
        self.remove(cube)
        self.play(FadeIn(cube), run_time=0.7)
        self.wait(0.55)

        # Build the entire expression on one LaTeX baseline, then reveal one
        # factor at a time. This keeps the left edge fixed without morphing
        # unrelated glyphs through the 3D camera.
        formula_left_x = 0.55
        formula_y = 1.02
        count_formula = formula(
            r"8!",
            r"\times 3^8",
            r"\times 12!",
            r"\times 2^{12}",
            font_size=56,
            color=CHARCOAL,
        )
        count_formula.set_x(formula_left_x + count_formula.width / 2)
        count_formula.set_y(formula_y)
        corner_permutation, corner_orientation, edge_permutation, edge_orientation = count_formula
        self.fix(count_formula)

        # The URF corner has three orientations. Three 120-degree turns about
        # its own outward diagonal return it exactly to its starting pose.
        urf_corner = cube.cubie(0, 0, 2)
        self.play(cube.pop_out(urf_corner), run_time=0.7)
        self.wait(0.4)
        self.play(FadeIn(corner_permutation, shift=RIGHT * 0.08), run_time=0.5)
        cubie_size = cube.current_cubie_size()
        corner_arrow = self.twist_arrow(
            cube,
            urf_corner,
            clockwise=True,
            radius=0.48 * cubie_size,
            lift=0.50 * cubie_size,
            color=MAGENTA,
            stroke_width=4.0,
            tip_length=0.16,
        )
        self.play(Create(corner_arrow), run_time=0.5)
        self.wait(0.25)
        corner_axis = normalize(urf_corner.get_center() - cube.get_cube_center())
        for _ in range(3):
            self.play(
                Rotate(
                    urf_corner,
                    angle=-2 * PI / 3,
                    axis=corner_axis,
                    about_point=urf_corner.get_center(),
                ),
                run_time=0.8,
                rate_func=rate_functions.ease_in_out_sine,
            )
        self.play(FadeIn(corner_orientation, shift=LEFT * 0.08), run_time=0.65)
        self.wait(0.35)
        self.play(FadeOut(corner_arrow), cube.pop_in(urf_corner), run_time=0.65)
        self.wait(0.35)

        # The UR edge has two orientations. A half-turn about its outward
        # diagonal exchanges its two stickers; repeating the half-turn restores it.
        ur_edge = cube.cubie(1, 0, 2)
        self.play(
            cube.pop_out(ur_edge),
            FadeIn(edge_permutation, shift=LEFT * 0.08),
            run_time=0.7,
        )
        self.wait(0.35)
        edge_arrows = self.flip_arrows(cube, ur_edge, colors=(MAGENTA, MAGENTA))
        self.play(
            *[Create(part) for pair in edge_arrows for part in pair],
            run_time=0.5,
        )
        self.wait(0.2)
        edge_axis = normalize(ur_edge.get_center() - cube.get_cube_center())
        for _ in range(2):
            self.play(
                Rotate(
                    ur_edge,
                    angle=PI,
                    axis=edge_axis,
                    about_point=ur_edge.get_center(),
                ),
                run_time=0.8,
                rate_func=rate_functions.ease_in_out_sine,
            )
        self.play(FadeIn(edge_orientation, shift=LEFT * 0.08), run_time=0.65)
        self.wait(0.35)
        self.play(FadeOut(edge_arrows), cube.pop_in(ur_edge), run_time=0.65)
        self.wait(0.8)

        # Reachable states satisfy three independent constraints: corner
        # orientation (/3), edge orientation (/2), and matching permutation
        # parity (/2). Turn the naive count into a fraction, then evaluate it.
        numerator = VGroup(
            corner_permutation,
            corner_orientation,
            edge_permutation,
            edge_orientation,
        )
        fraction_bar = Line(
            LEFT * (numerator.width + 0.28) / 2,
            RIGHT * (numerator.width + 0.28) / 2,
            color=CHARCOAL,
            stroke_width=3.0,
        )
        fraction_bar.move_to(np.array([numerator.get_center()[0], formula_y + 0.02, 0.0]))
        denominator = formula(r"3\times 2\times 2", font_size=56, color=CHARCOAL)
        denominator.next_to(fraction_bar, DOWN, buff=0.16)

        self.fix(fraction_bar, denominator)

        self.play(numerator.animate.shift(UP * 0.58), run_time=0.5)
        self.play(Create(fraction_bar), run_time=0.4)
        self.play(FadeIn(denominator, shift=UP * 0.06), run_time=0.5)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# Definition 3: Order + cube examples
# ---------------------------------------------------------------------------


class CubeElementOrderScene(RubiksCubeScene):
    """Definition 3：元素的 order，及魔方/整数例子。"""

    def construct(self) -> None:
        background = image_background("kraft_paper_002.png")
        background.scale(1.04)
        self.add_fixed_in_frame_mobjects(background)

        # 「设 (G, *) 是一个群，g ∈ G……则称 g 具有 infinite order。」
        definition_prefix = ctext("定义 元素的 order：", 32, color=YELLOW)
        definition_line_one = VGroup(
            ctext("设", 30, color=PAPER),
            formula(r"(G,\ast)", font_size=42, color=PAPER),
            ctext("是一个群，且", 30, color=PAPER),
            formula(r"g\in G", font_size=42, color=PAPER),
            ctext("。", 30, color=PAPER),
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        definition_line_two = VGroup(
            ctext("如果存在正整数", 30, color=PAPER),
            formula(r"n", font_size=42, color=PAPER),
            ctext("，使得", 30, color=PAPER),
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        definition_equation = formula(r"g^n=e,", font_size=52, color=PAPER)
        definition_line_three = ctext(
            "那么所有满足这个等式的正整数中，最小的一个",
            29,
            color=PAPER,
        )
        definition_line_four = VGroup(
            ctext("称为", 29, color=PAPER),
            formula(r"g", font_size=41, color=PAPER),
            ctext("的 order，记作：", 29, color=PAPER),
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        definition_notation = formula(r"\operatorname{ord}(g).", font_size=52, color=PAPER)
        infinite_order_line = VGroup(
            ctext("如果不存在这样的正整数，则称", 28, color=PAPER),
            formula(r"g", font_size=40, color=PAPER),
            ctext("具有 infinite order。", 28, color=PAPER),
        ).arrange(RIGHT, buff=0.11, aligned_edge=DOWN)

        definition_content = VGroup(
            definition_prefix,
            definition_line_one,
            definition_line_two,
            definition_equation,
            definition_line_three,
            definition_line_four,
            definition_notation,
            infinite_order_line,
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        definition_equation.set_x(definition_content.get_center()[0])
        definition_notation.set_x(definition_content.get_center()[0])
        definition_block = course_badge(
            definition_content,
            preset="definition",
            h_padding=0.62,
            v_padding=0.42,
        )
        definition_block.move_to(UP * 0.66)
        definition_box = definition_block[0]
        definition_page = (
            definition_box,
            definition_prefix,
            definition_line_one,
            definition_line_two,
            definition_equation,
            definition_line_three,
            definition_line_four,
            definition_notation,
            infinite_order_line,
        )
        self.fix(*definition_page)

        self.play(FadeIn(definition_box), Write(definition_prefix), run_time=0.55)
        self.play(Write(definition_line_one), run_time=0.8)
        self.play(Write(definition_line_two), run_time=0.65)
        self.play(Write(definition_equation), run_time=0.55)
        self.play(Write(definition_line_three), run_time=0.8)
        self.play(Write(definition_line_four), run_time=0.65)
        self.play(Write(definition_notation), run_time=0.55)
        self.play(Write(infinite_order_line), run_time=0.8)
        self.wait(1.0)

        # Two spoken examples bridge the formal definition and the cube-order
        # table. Keep them as MathTex so the baselines stay visually stable.
        r_first = formula(r"e=R^4", font_size=56, color=CHARCOAL)
        r_first.move_to(UP * 0.72)
        r_extension = formula(r"=R^8=R^{12}", font_size=56, color=CHARCOAL)
        r_full_target = VGroup(r_first.copy(), r_extension)
        r_full_target.arrange(RIGHT, buff=0.08).move_to(UP * 0.72)
        r_order = formula(r"\operatorname{ord}(R)=4", font_size=56, color=CHARCOAL)
        r_order.move_to(UP * 0.72)

        integer_group = formula(r"(\mathbb{Z},+)", font_size=52, color=CHARCOAL)
        integer_group.move_to(DOWN * 0.72)
        integer_order = formula(
            r"3\text{ has infinite order}",
            font_size=46,
            color=CHARCOAL,
        )
        integer_row_target = VGroup(integer_group.copy(), integer_order)
        integer_row_target.arrange(RIGHT, buff=0.95).move_to(DOWN * 0.72)

        self.fix(r_first, r_extension, r_order, integer_group, integer_order)
        self.play(*[FadeOut(mobject) for mobject in definition_page], run_time=0.6)
        self.play(Write(r_first), run_time=0.55)
        self.wait(0.45)
        self.play(
            Transform(r_first, r_full_target[0]),
            FadeIn(r_extension, shift=LEFT * 0.08),
            run_time=0.65,
        )
        self.wait(0.55)
        self.play(
            FadeOut(r_first),
            FadeOut(r_extension),
            FadeIn(r_order),
            run_time=0.55,
        )
        self.wait(0.45)
        self.play(Write(integer_group), run_time=0.5)
        self.wait(0.4)
        self.play(
            Transform(integer_group, integer_row_target[0]),
            FadeIn(integer_order, shift=LEFT * 0.08),
            run_time=0.65,
        )
        self.wait(0.7)

        # Revisit the three order examples from the opening scene. The first
        # pass deliberately keeps the original "n 次" wording.
        row_ys = (1.25, 0.0, -1.25)
        preview_rows = []
        for (moves, count), y in zip(OPENING_ORDER_EXAMPLES, row_ys, strict=True):
            cube = RubiksCube(total_size=0.68)
            cube.do_moves(moves)
            cube.move_to(self.screen_point(-4.88, y))
            depth_sort_cube(cube, self.camera)

            badge = move_sequence_badge(moves, font_size=36)
            badge.move_to(RIGHT * 0.05 + UP * y)

            count_text = f"最大：{count}次" if count == 1260 else f"{count}次"
            count_label = ctext(count_text, 34, color=BLUE)
            count_label.move_to(RIGHT * 4.95 + UP * y)

            order_label = formula(
                rf"\operatorname{{ord}}\!\left({moves_to_latex(moves)}\right)",
                "=",
                str(count),
                font_size=34,
                color=CHARCOAL,
            )
            order_label[2].set_color(BLUE)
            order_label.move_to(RIGHT * 4.95 + UP * y)

            self.fix(badge, count_label, order_label)
            preview_rows.append((cube, badge, count_label, order_label, y))

        self.play(FadeOut(r_order), FadeOut(integer_group), FadeOut(integer_order), run_time=0.6)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(cube, scale=0.92),
                        FadeIn(badge, shift=LEFT * 0.1),
                        FadeIn(count_label, shift=RIGHT * 0.1),
                    )
                    for cube, badge, count_label, _, _ in preview_rows
                ],
                lag_ratio=0.22,
            ),
            run_time=1.35,
        )
        self.wait(1.0)

        # Text-to-LaTeX shape morphs are hard to read, so use a short crossfade
        # while preserving each value's exact column anchor.
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(FadeOut(count_label), FadeIn(order_label))
                    for _, _, count_label, order_label, _ in preview_rows
                ],
                lag_ratio=0.14,
            ),
            run_time=0.9,
        )
        self.wait(0.65)

        new_moves = "R U R' U'"
        new_count = 6
        new_y = 2.5
        new_cube = RubiksCube(total_size=0.68)
        new_cube.do_moves(new_moves)
        new_cube.move_to(self.screen_point(-4.88, new_y))
        depth_sort_cube(new_cube, self.camera)

        new_badge = move_sequence_badge(new_moves, font_size=36)
        new_badge.move_to(RIGHT * 0.05 + UP * new_y)
        new_order_label = formula(
            rf"\operatorname{{ord}}\!\left({moves_to_latex(new_moves)}\right)",
            "=",
            str(new_count),
            font_size=34,
            color=CHARCOAL,
        )
        new_order_label[2].set_color(BLUE)
        new_order_label.move_to(RIGHT * 4.95 + UP * new_y)
        self.fix(new_badge, new_order_label)

        self.play(
            FadeIn(new_cube, scale=0.92),
            FadeIn(new_badge, shift=LEFT * 0.1),
            FadeIn(new_order_label, shift=RIGHT * 0.1),
            run_time=0.75,
        )
        self.wait(0.65)

        # Keep the move badge's frame and replace only its label. Use MathTex
        # so the English matches the badge's Computer Modern, not PingFang SC.
        sexy_move_label = formula(r"Sexy\,\,Move", font_size=36, color=YELLOW)
        sexy_move_label.move_to(new_badge[1])
        self.fix(sexy_move_label)
        self.play(FadeOut(new_badge[1]), FadeIn(sexy_move_label), run_time=0.5)
        self.wait(1.0)

        # Closing teaser: every element order divides |G|. Use \mid for
        # "divides" and \lvert...\rvert for cardinality so the bars don't collide.
        outro_fade = [
            *(
                mobject
                for cube, badge, _, order_label, _ in preview_rows
                for mobject in (cube, badge, order_label)
            ),
            new_cube,
            new_badge[0],
            sexy_move_label,
            new_order_label,
        ]
        self.play(*[FadeOut(mobject) for mobject in outro_fade], run_time=0.65)

        divides_lhs = formula(
            r"\operatorname{ord}(g)",
            r"\bigm|",
            r"\lvert G\rvert",
            font_size=56,
            color=CHARCOAL,
        )
        divides_lhs.move_to(UP * 0.55)

        group_order_rhs = formula(
            r"=",
            r"\dfrac{8!\times 3^{8}\times 12!\times 2^{12}}{3\times 2\times 2}",
            font_size=48,
            color=CHARCOAL,
        )
        divides_full_target = VGroup(divides_lhs.copy(), group_order_rhs)
        divides_full_target.arrange(RIGHT, buff=0.22).move_to(UP * 0.55)

        self.fix(divides_lhs, group_order_rhs)
        self.play(Write(divides_lhs), run_time=0.75)
        self.wait(1.0)
        self.play(
            Transform(divides_lhs, divides_full_target[0]),
            FadeIn(group_order_rhs, shift=LEFT * 0.08),
            run_time=0.7,
        )
        self.wait(1.0)
