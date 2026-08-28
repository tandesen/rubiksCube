#!/usr/bin/env python3
"""Generate normalized UV artwork and a manufacturer-facing concept board.

The SVG is the source of truth. PNG files are presentation previews only;
the selected cube supplier must still provide the final model-specific dieline.
"""

from __future__ import annotations

import csv
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "assets" / "lettered_cube_uv"

COLORS = {
    "U": "#2C74C9",
    "R": "#D64235",
    "F": "#F3D34A",
    "D": "#31B56A",
    "L": "#F08A33",
    "B": "#F8F6EF",
}
CHARCOAL = "#25231F"
PAPER = "#F8F3E7"
MAGENTA = "#C23A82"
YELLOW = "#F3D34A"
BLUE = "#2C74C9"

FACELETS = {
    "U": [["E0", "P0", "G0"], ["O0", "U", "M0"], ["C0", "N0", "A0"]],
    "R": [["A1", "M1", "G2"], ["W0", "R", "Z0"], ["H2", "Q1", "K1"]],
    "F": [["C1", "N1", "A2"], ["X1", "F", "W1"], ["I2", "S1", "H1"]],
    "D": [["I0", "S0", "H0"], ["T0", "D", "Q0"], ["J0", "V0", "K0"]],
    "L": [["E1", "O1", "C2"], ["Y0", "L", "X0"], ["J2", "T1", "I1"]],
    "B": [["G1", "P1", "E2"], ["Z1", "B", "Y1"], ["K2", "V1", "J1"]],
}

FACE_POSITIONS = {
    "U": (1, 0),
    "L": (0, 1),
    "F": (1, 1),
    "R": (2, 1),
    "B": (3, 1),
    "D": (1, 2),
}

PIECE_NAMES = {
    "A": "URF corner",
    "C": "UFL corner",
    "E": "ULB corner",
    "G": "UBR corner",
    "H": "DFR corner",
    "I": "DLF corner",
    "J": "DBL corner",
    "K": "DRB corner",
    "M": "UR edge",
    "N": "UF edge",
    "O": "UL edge",
    "P": "UB edge",
    "Q": "DR edge",
    "S": "DF edge",
    "T": "DL edge",
    "V": "DB edge",
    "W": "FR edge",
    "X": "FL edge",
    "Y": "BL edge",
    "Z": "BR edge",
}


def text_color(face: str) -> str:
    return PAPER if face in {"U", "R", "D"} else CHARCOAL


def svg_element(tag: str, **attrs) -> ET.Element:
    return ET.Element(tag, {key.replace("_", "-"): str(value) for key, value in attrs.items()})


def add_svg_text(
    parent,
    x,
    y,
    text,
    *,
    size,
    color,
    weight="700",
    anchor="middle",
    family="Arial, Helvetica, sans-serif",
):
    node = ET.SubElement(
        parent,
        "text",
        {
            "x": str(x),
            "y": str(y),
            "font-family": family,
            "font-size": str(size),
            "font-weight": weight,
            "fill": color,
            "text-anchor": anchor,
            "dominant-baseline": "middle",
        },
    )
    node.text = text
    return node


def add_svg_facelet_label(parent, x, y, label, face, *, size):
    if len(label) == 1:
        add_svg_text(parent, x, y, label, size=size * 1.12, color=text_color(face))
        return
    letter, suffix = label
    node = add_svg_text(parent, x, y, "", size=size, color=text_color(face))
    main = ET.SubElement(node, "tspan")
    main.text = letter
    sub = ET.SubElement(
        node,
        "tspan",
        {
            "font-size": str(size * 0.58),
            "baseline-shift": "sub",
            "dx": str(size * 0.03),
        },
    )
    sub.text = suffix


def add_svg_face(parent, face: str, x: float, y: float, cell: float, gap: float):
    face_group = ET.SubElement(parent, "g", {"id": f"face-{face}"})
    for row in range(3):
        for col in range(3):
            px = x + col * cell + gap / 2
            py = y + row * cell + gap / 2
            ET.SubElement(
                face_group,
                "rect",
                {
                    "x": str(px),
                    "y": str(py),
                    "width": str(cell - gap),
                    "height": str(cell - gap),
                    "rx": str(cell * 0.08),
                    "fill": COLORS[face],
                    "stroke": CHARCOAL,
                    "stroke-width": "1.4",
                },
            )
            add_svg_facelet_label(
                face_group,
                px + (cell - gap) / 2,
                py + (cell - gap) / 2,
                FACELETS[face][row][col],
                face,
                size=cell * 0.31,
            )


def build_uv_svg() -> Path:
    cell = 100
    gap = 8
    margin = 70
    width = margin * 2 + 12 * cell
    height = margin * 2 + 9 * cell
    root = svg_element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width=width,
        height=height,
        viewBox=f"0 0 {width} {height}",
    )
    root.append(svg_element("rect", x=0, y=0, width=width, height=height, fill="#F4E2BD"))
    add_svg_text(root, margin, 36, "26-LETTER CUBE - NORMALIZED UV NET", size=26, color=CHARCOAL, anchor="start")

    for face, (grid_x, grid_y) in FACE_POSITIONS.items():
        add_svg_face(root, face, margin + grid_x * 3 * cell, margin + grid_y * 3 * cell, cell, gap)

    add_svg_text(
        root,
        margin,
        height - 24,
        "Concept scale only. Final artwork must be placed on the selected cube model's supplier dieline.",
        size=19,
        color=CHARCOAL,
        weight="400",
        anchor="start",
    )
    path = OUTPUT_DIR / "lettered_cube_uv_net.svg"
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def load_font(size: int, *, bold: bool = False):
    filename = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{filename}", size=size)


def load_cn_font(size: int):
    return ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", size=size)


def centered_text(draw, xy, text, font, fill):
    draw.text(xy, text, font=font, fill=fill, anchor="mm")


def draw_face(draw, face, x, y, cell, gap):
    for row in range(3):
        for col in range(3):
            px = x + col * cell + gap / 2
            py = y + row * cell + gap / 2
            bounds = (px, py, px + cell - gap, py + cell - gap)
            draw.rounded_rectangle(bounds, radius=cell * 0.08, fill=COLORS[face], outline=CHARCOAL, width=2)
            label = FACELETS[face][row][col]
            cx = px + (cell - gap) / 2
            cy = py + (cell - gap) / 2
            if len(label) == 1:
                centered_text(draw, (cx, cy), label, load_font(round(cell * 0.34), bold=True), text_color(face))
            else:
                letter, suffix = label
                centered_text(
                    draw,
                    (cx - cell * 0.03, cy - cell * 0.015),
                    letter,
                    load_font(round(cell * 0.30), bold=True),
                    text_color(face),
                )
                centered_text(
                    draw,
                    (cx + cell * 0.13, cy + cell * 0.13),
                    suffix,
                    load_font(round(cell * 0.15), bold=True),
                    text_color(face),
                )


def add_paper_texture(image: Image.Image) -> None:
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            noise = ((x * 17 + y * 29 + x * y * 3) % 19) - 9
            if noise == 0:
                continue
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)),
            )


def build_uv_png() -> Path:
    cell = 88
    gap = 7
    margin = 62
    width = margin * 2 + 12 * cell
    height = margin * 2 + 9 * cell
    image = Image.new("RGB", (width, height), "#F4E2BD")
    add_paper_texture(image)
    draw = ImageDraw.Draw(image)
    draw.text((margin, 20), "26-LETTER CUBE - NORMALIZED UV NET", font=load_font(25, bold=True), fill=CHARCOAL)
    for face, (grid_x, grid_y) in FACE_POSITIONS.items():
        draw_face(draw, face, margin + grid_x * 3 * cell, margin + grid_y * 3 * cell, cell, gap)
    draw.text(
        (margin, height - 36),
        "CONCEPT SCALE ONLY / FINAL SIZE FOLLOWS SUPPLIER DIELINE",
        font=load_font(16, bold=True),
        fill=CHARCOAL,
    )
    path = OUTPUT_DIR / "lettered_cube_uv_net.png"
    image.save(path)
    return path


def polygon_center(points):
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def draw_isometric_face(draw, origin, u, v, face, cell_scale=1.0):
    for row in range(3):
        for col in range(3):
            inset = 0.045
            p0 = (origin[0] + (col + inset) * u[0] + (row + inset) * v[0], origin[1] + (col + inset) * u[1] + (row + inset) * v[1])
            p1 = (origin[0] + (col + 1 - inset) * u[0] + (row + inset) * v[0], origin[1] + (col + 1 - inset) * u[1] + (row + inset) * v[1])
            p2 = (origin[0] + (col + 1 - inset) * u[0] + (row + 1 - inset) * v[0], origin[1] + (col + 1 - inset) * u[1] + (row + 1 - inset) * v[1])
            p3 = (origin[0] + (col + inset) * u[0] + (row + 1 - inset) * v[0], origin[1] + (col + inset) * u[1] + (row + 1 - inset) * v[1])
            draw.polygon([p0, p1, p2, p3], fill=COLORS[face], outline=CHARCOAL)
            # The R face is projected from its far-right edge toward the
            # front-right seam, so its visual column order is reversed.
            label_col = 2 - col if face == "R" else col
            label = FACELETS[face][row][label_col]
            cx, cy = polygon_center([p0, p1, p2, p3])
            color = text_color(face)
            if len(label) == 1:
                centered_text(draw, (cx, cy), label, load_font(25, bold=True), color)
            else:
                centered_text(draw, (cx, cy), label[0], load_font(23, bold=True), color)
                centered_text(draw, (cx + 12, cy + 10), label[1], load_font(12, bold=True), color)


def draw_callout(draw, box, title, lines, accent):
    draw.rounded_rectangle(box, radius=14, fill="#FBF4E5", outline=accent, width=3)
    x0, y0, _, _ = box
    draw.text((x0 + 22, y0 + 18), title, font=load_cn_font(25), fill=accent)
    for index, line in enumerate(lines):
        draw.text((x0 + 22, y0 + 58 + index * 30), line, font=load_cn_font(20), fill=CHARCOAL)


def build_concept_board() -> Path:
    width, height = 1920, 1080
    image = Image.new("RGB", (width, height), "#F4E2BD")
    add_paper_texture(image)
    draw = ImageDraw.Draw(image)

    draw.text((76, 50), "26 字母编号教学魔方", font=load_cn_font(52), fill=CHARCOAL)
    draw.text((80, 116), "UV 打样概念板 / cubie 身份与朝向标记", font=load_cn_font(25), fill="#665D50")

    # Hero cube, using the exact U/F/R face maps from the production net.
    apex = (455, 185)
    u_top, v_top = (75, 28), (-75, 28)
    draw_isometric_face(draw, apex, u_top, v_top, "U")
    front_origin = (apex[0] + 3 * v_top[0], apex[1] + 3 * v_top[1])
    draw_isometric_face(draw, front_origin, u_top, (0, 75), "F")
    right_origin = (apex[0] + 3 * u_top[0], apex[1] + 3 * u_top[1])
    draw_isometric_face(draw, right_origin, v_top, (0, 75), "R")

    # Exploded-design callouts: these are identity rules, not production sizes.
    draw.line((675, 310, 955, 250), fill=MAGENTA, width=4)
    draw_callout(
        draw,
        (955, 170, 1425, 350),
        "角块 / A",
        ["A0、A1、A2 属于同一个物理角块", "下标区分这个角块的三个贴面"],
        MAGENTA,
    )
    draw.line((675, 440, 955, 475), fill=BLUE, width=4)
    draw_callout(
        draw,
        (955, 385, 1425, 555),
        "棱块 / M",
        ["M0、M1 属于同一个物理棱块", "两个贴面编号能显示棱块翻转"],
        BLUE,
    )
    draw.line([(455, 270), (900, 365), (1460, 365), (1495, 430)], fill="#8A6F20", width=4)
    draw_callout(
        draw,
        (1495, 385, 1840, 555),
        "中心块 / U R F D L B",
        ["中心字母直接对应六个面名", "面转记号不会再与 cubie 身份混淆"],
        "#8A6F20",
    )

    # Compact six-face UV net at the bottom of the product board.
    cell = 42
    gap = 5
    base_x, base_y = 115, 620
    draw.text((base_x, base_y - 54), "六面展开与贴面方向", font=load_cn_font(27), fill=CHARCOAL)
    for face, (grid_x, grid_y) in FACE_POSITIONS.items():
        draw_face(draw, face, base_x + grid_x * 3 * cell, base_y + grid_y * 3 * cell, cell, gap)

    draw_callout(
        draw,
        (895, 700, 1840, 1010),
        "给厂商的打样要求",
        [
            "1. 先确认三阶基础型号、尺寸和每片可印刷区域。",
            "2. 将这份标准化编号放入厂商提供的矢量刀模。",
            "3. 量产前先做样品，逐格核对全部 54 个贴面。",
            "4. 工艺要求为彩色 UV 直喷，不是透明 UV 涂层。",
            "5. PNG 只用于沟通；生产文件应使用 SVG/PDF/AI。",
        ],
        CHARCOAL,
    )

    path = OUTPUT_DIR / "lettered_cube_uv_concept_board.png"
    image.save(path)
    return path


def build_facelet_csv() -> Path:
    path = OUTPUT_DIR / "lettered_cube_facelet_map.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["face", "row", "column", "print_label", "piece", "piece_type"])
        for face in "URFDLB":
            for row in range(3):
                for col in range(3):
                    label = FACELETS[face][row][col]
                    if len(label) == 1:
                        writer.writerow([face, row + 1, col + 1, label, f"{face} center", "center"])
                    else:
                        piece = label[0]
                        piece_type = "corner" if piece in "ACEGHIJK" else "edge"
                        writer.writerow([face, row + 1, col + 1, label, PIECE_NAMES[piece], piece_type])
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        build_uv_svg(),
        build_uv_png(),
        build_concept_board(),
        build_facelet_csv(),
    ]
    for path in outputs:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
