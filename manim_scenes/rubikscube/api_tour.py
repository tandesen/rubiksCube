"""rubikscube 包 API 全览 — 单场景逐步演示每个公开方法/工具。

从项目根目录渲染::

    .venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/api_tour.py RubikscubeApiTour
    .venv/bin/manim -qh --media_dir media manim_scenes/rubikscube/api_tour.py RubikscubeApiTour
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (
    DOWN,
    Create,
    FadeIn,
    FadeOut,
    LEFT,
    PI,
    RIGHT,
    RoundedRectangle,
    Text,
    UP,
    VGroup,
    Write,
    config,
)

from rubikscube import (
    CubeMove,
    CubeStyle,
    FACE_ORDER,
    RubiksCube,
    RubiksCube2x2,
    RubiksCubeScene,
    blink_cubies,
    blink_faces,
    dim_color,
    face_rings,
    focus_cubies,
    get_axis_from_face,
    get_faces_of_cubie,
    mark_cubies,
    normalize,
    parse_move,
    reset_look,
)

config.frame_width = 16
config.frame_height = 9
config.background_color = "#7D8C73"

FONT = "PingFang SC"
CHARCOAL = "#232323"
PAPER = "#F8F6EF"
YELLOW = "#F3D34A"

SOLVED_STATE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def caption_box(title: str, body: str) -> VGroup:
    panel = RoundedRectangle(
        width=5.6,
        height=2.35,
        corner_radius=0.18,
        fill_color=CHARCOAL,
        fill_opacity=0.88,
        stroke_color=PAPER,
        stroke_width=2.0,
    )
    title_text = Text(title, font=FONT, font_size=30, color=YELLOW)
    title_text.next_to(panel.get_top(), DOWN, buff=0.28)
    body_text = Text(body, font=FONT, font_size=22, color=PAPER, line_spacing=0.9)
    if body_text.width > 5.0:
        body_text.scale(5.0 / body_text.width)
    body_text.next_to(title_text, DOWN, buff=0.22)
    return VGroup(panel, title_text, body_text)


class RubikscubeApiTour(RubiksCubeScene):
    """逐个演示 rubikscube 公开 API；右侧固定说明面板。"""

    def show_caption(self, title: str, body: str, *, panel: VGroup | None = None) -> VGroup:
        next_panel = caption_box(title, body)
        next_panel.move_to(RIGHT * 3.55 + UP * 0.15)
        self.fix(next_panel)
        if panel is None:
            self.play(FadeIn(next_panel, shift=LEFT * 0.12), run_time=0.45)
            return next_panel
        self.play(FadeOut(panel), FadeIn(next_panel, shift=LEFT * 0.12), run_time=0.4)
        return next_panel

    def construct(self) -> None:
        panel: VGroup | None = None

        # ------------------------------------------------------------------
        # RubiksCubeScene
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "RubiksCubeScene.add_cube",
            "把魔方加入场景并自动深度排序\n（内部调用 depth_sort_cube）",
            panel=panel,
        )
        cube = RubiksCube(total_size=2.2, style="cartoon")
        cube.move_to(self.screen_point(-4.85, 0.05))
        cube = self.add_cube(cube)
        self.wait(0.55)

        panel = self.show_caption(
            "RubiksCubeScene.screen_point",
            "给定屏幕坐标 (x, y)，返回\n对应的世界空间位置，方便布局",
            panel=panel,
        )
        self.play(cube.animate.move_to(self.screen_point(-4.85, 0.35)), run_time=0.55)
        self.wait(0.45)

        panel = self.show_caption(
            "CubeMove  /  RubiksCubeScene.turn",
            "CubeMove：单步转层动画\n"
            "turn：按空格拆分字符串，连续播放多步",
            panel=panel,
        )
        self.play(CubeMove(cube, "R"), run_time=0.5)
        self.turn(cube, "U' F", run_time=0.48, wait=0.08)
        self.wait(0.35)

        panel = self.show_caption(
            "RubiksCube.layer",
            "返回某一面的整层 cubie 列表\n例：layer(\"U\") 为顶层",
            panel=panel,
        )
        self.play(cube.blink(cube.layer("U")), run_time=0.85)
        self.wait(0.3)

        # ------------------------------------------------------------------
        # Highlights (via cube methods + module functions)
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "RubiksCube.focus  /  focus_cubies",
            "选中 cubie 保持亮色，其余贴纸变暗\n"
            "适合突出中心块、棱块等",
            panel=panel,
        )
        self.play(cube.focus(cube.center_cubies()), run_time=0.55)
        self.wait(0.35)

        panel = self.show_caption(
            "face_rings",
            "复制贴纸轮廓做描边 overlay\n"
            "FadeIn/FadeOut，不改原贴纸",
            panel=panel,
        )
        rings = face_rings(cube.visible_center_stickers(), color=PAPER, scale=1.05)
        self.add(rings)
        self.play(FadeIn(rings), run_time=0.4)
        self.wait(0.3)
        self.play(FadeOut(rings), run_time=0.3)

        panel = self.show_caption(
            "RubiksCube.reset_look  /  reset_look",
            "把所有贴纸填充色与边缝\n恢复为 base_fill / base_stroke",
            panel=panel,
        )
        self.play(cube.reset_look(), run_time=0.5)
        self.wait(0.35)

        panel = self.show_caption(
            "RubiksCube.blink  /  blink_cubies",
            "Indicate 脉冲，blingbling 闪一下\n"
            "blink_faces 可对单张贴纸使用",
            panel=panel,
        )
        self.play(blink_cubies(cube, cube.edge_cubies()[:4]), run_time=0.9)
        self.wait(0.25)

        panel = self.show_caption(
            "RubiksCube.mark  /  mark_cubies",
            "指定 cubie 涂马克笔色\n"
            "其余边缝变白，突出「交换」",
            panel=panel,
        )
        corner_a = cube.cubie(0, 0, 2)
        corner_b = cube.cubie(0, 2, 2)
        self.play(
            mark_cubies(cube, [(corner_a, "#C23A82"), (corner_b, "#36B8A6")]),
            run_time=0.55,
        )
        self.wait(0.35)

        panel = self.show_caption(
            "RubiksCubeScene.swap_arrows",
            "两 cubie 之间的循环交换箭头\n"
            "3D 锚定，随相机视角正确",
            panel=panel,
        )
        swap = self.swap_arrows(cube, corner_a, corner_b)
        self.play(*[Create(part) for pair in swap for part in pair], run_time=0.65)
        self.wait(0.35)
        self.play(FadeOut(swap), cube.reset_look(), run_time=0.45)

        panel = self.show_caption(
            "RubiksCube.pop_out  /  pop_in",
            "沿 cubie  outward 方向滑出 / 滑回\n"
            "弹出期间不要转该层",
            panel=panel,
        )
        corner = cube.cubie(0, 0, 2)
        self.play(cube.pop_out(corner), run_time=0.55)
        self.wait(0.25)

        panel = self.show_caption(
            "RubiksCubeScene.twist_arrow",
            "角块原地旋转方向的圆弧箭头",
            panel=panel,
        )
        twist = self.twist_arrow(cube, corner, clockwise=True)
        self.add(twist)
        self.play(Create(twist), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(twist), run_time=0.25)

        panel = self.show_caption(
            "RubiksCubeScene.flip_arrows",
            "棱块翻面指示箭头\n"
            "（superflip 等场景）",
            panel=panel,
        )
        self.play(cube.pop_in(corner), run_time=0.45)
        edge = cube.cubie(0, 1, 2)
        flips = self.flip_arrows(cube, edge)
        self.add(flips)
        self.play(*[Create(part) for pair in flips for part in pair], run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(flips), run_time=0.3)

        # ------------------------------------------------------------------
        # Cubie selectors
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "RubiksCube.cubie",
            "按逻辑数组下标 (x,y,z)\n"
            "取当前在该位置的 cubie",
            panel=panel,
        )
        self.play(cube.mark([(corner_a, YELLOW)]), run_time=0.4)
        self.wait(0.35)
        self.play(cube.reset_look(), run_time=0.4)

        panel = self.show_caption(
            "corner / edge / center_cubies",
            "角块 (8) · 棱块 (12) · 中心块 (6)\n"
            "三类 cubie 选择器",
            panel=panel,
        )
        self.play(cube.focus(cube.corner_cubies()), run_time=0.45)
        self.wait(0.25)
        self.play(focus_cubies(cube, cube.edge_cubies()), run_time=0.45)
        self.wait(0.25)
        self.play(cube.focus(cube.center_cubies()), run_time=0.45)
        self.wait(0.25)
        self.play(cube.reset_look(), run_time=0.4)

        panel = self.show_caption(
            "center_sticker  /  visible_center_stickers",
            "单面中心贴纸 · 默认 F/U/R 三面\n"
            "hero 视角可见的中心块",
            panel=panel,
        )
        self.play(blink_faces(list(cube.visible_center_stickers())), run_time=0.75)
        self.wait(0.3)

        # ------------------------------------------------------------------
        # Moves & state
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "RubiksCube.do_moves",
            "无动画瞬间完成多步转动\n"
            "用于摆打乱态或预计算",
            panel=panel,
        )
        cube.do_moves("R U R' U'")
        self.wait(0.55)

        panel = self.show_caption(
            "RubiksCube.set_state",
            "54 字符 kociemba 贴纸串\n"
            "只改颜色，不改 cubie 位置",
            panel=panel,
        )
        cube.set_state(SOLVED_STATE)
        self.wait(0.55)

        panel = self.show_caption(
            "RubiksCube.apply_move",
            "只更新逻辑 cubies 数组\n"
            "（视觉旋转请用 CubeMove）",
            panel=panel,
        )
        self.play(CubeMove(cube, "R"), run_time=0.45)
        self.wait(0.4)

        panel = self.show_caption(
            "RubiksCube.face_axis  /  get_cube_center",
            "某面外法向转轴 · 魔方体中心\n"
            "几何查询，供自定义动画使用",
            panel=panel,
        )
        _ = cube.face_axis("R")
        _ = cube.get_cube_center()
        self.wait(0.5)

        # ------------------------------------------------------------------
        # cube_utils
        # ------------------------------------------------------------------
        face_list = ", ".join(get_faces_of_cubie((0, 0, 2), 3))
        parsed = parse_move("R'")
        panel = self.show_caption(
            "parse_move  /  get_faces_of_cubie",
            f"parse_move(\"R'\") → {parsed}\n"
            f"urf 角块 faces: {face_list}",
            panel=panel,
        )
        self.wait(0.65)

        axis = get_axis_from_face("U")
        panel = self.show_caption(
            "get_axis_from_face  /  normalize",
            "标准帧下面外法向单位向量\n"
            f"U 轴 ≈ {axis.round(2).tolist()}\n"
            "normalize：向量归一化",
            panel=panel,
        )
        _ = normalize(axis)
        self.wait(0.55)

        panel = self.show_caption(
            "dim_color  /  FACE_ORDER",
            "把颜色向黑色插值变暗\n"
            f"FACE_ORDER = \"{FACE_ORDER}\"",
            panel=panel,
        )
        sample_face = cube.cubie(1, 1, 2).get_face("F")
        self.play(
            sample_face.animate.set_fill(dim_color(sample_face.get_fill_color(), 0.5)),
            run_time=0.4,
        )
        self.play(cube.reset_look(), run_time=0.4)

        # ------------------------------------------------------------------
        # Style & 2x2
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "CubeStyle  /  resolve_style",
            "cartoon · classic · realistic\n"
            "预设外观，可 with_() 微调",
            panel=panel,
        )
        styled = RubiksCube(total_size=0.95, style=CubeStyle.realistic())
        styled.move_to(self.screen_point(-4.85, -1.85))
        styled = self.add_cube(styled)
        self.wait(0.55)
        self.remove_cube(styled)
        self.play(FadeOut(styled), run_time=0.3)

        panel = self.show_caption(
            "RubiksCube2x2",
            "2 阶魔方，API 与 3 阶相同\n"
            "（无 set_state / 中心块）",
            panel=panel,
        )
        pocket = self.add_cube(RubiksCube2x2(total_size=0.85).move_to(self.screen_point(-4.85, -1.85)))
        self.turn(pocket, "R U'", run_time=0.45, wait=0.05)
        self.wait(0.35)
        self.remove_cube(pocket)
        self.play(FadeOut(pocket), run_time=0.3)

        # ------------------------------------------------------------------
        # Scene helpers
        # ------------------------------------------------------------------
        panel = self.show_caption(
            "RubiksCubeScene.fix",
            "注册 fixed-in-frame 2D  overlay\n"
            "（本说明面板即由此固定）",
            panel=panel,
        )
        self.wait(0.55)

        panel = self.show_caption(
            "stop_tracking  /  remove_cube",
            "停止自动深度排序 · 从场景移除\n"
            "静态快照用 track=False 的 add_cube",
            panel=panel,
        )
        snapshot = cube.copy()
        snapshot.scale(0.55).move_to(self.screen_point(-2.2, -1.6))
        self.add_cube(snapshot, track=False)
        self.play(FadeIn(snapshot), run_time=0.4)
        self.wait(0.35)
        self.remove_cube(snapshot)
        self.play(FadeOut(snapshot), run_time=0.35)

        panel = self.show_caption(
            "module_center  /  SWAP_COLORS",
            "箭头锚点：cubie 可见贴纸中心\n"
            "swap_arrows 默认配色常量",
            panel=panel,
        )
        self.wait(0.55)

        panel = self.show_caption(
            "API Tour 完成",
            "详见 rubikscube/README.md\n"
            "与 examples.py 冒烟场景",
            panel=panel,
        )
        self.wait(1.2)
