"""Reusable course labels and framed statement blocks for Manim scenes.

``course_badge`` is the core builder. It can frame either plain text or an
already-composed Manim mobject, and all visual presets remain overridable per
call. Convenience helpers provide the usual mathematical headings.
"""

from __future__ import annotations

from manim import DOWN, LEFT, RIGHT, FadeIn, Mobject, RoundedRectangle, Text, VGroup


FONT = "PingFang SC"
CHARCOAL = "#232323"
PAPER = "#F8F6EF"
YELLOW = "#F3D34A"
MAGENTA = "#C23A82"
CYAN = "#36B8A6"
DARKBLUE = "#045496" # "#264674"


class BadgeStyle:
    """Visual settings shared by a family of course badges."""

    __slots__ = (
        "fill_color",
        "fill_opacity",
        "stroke_color",
        "stroke_width",
        "text_color",
        "font_size",
        "corner_radius",
        "height",
        "h_padding",
    )

    def __init__(
        self,
        *,
        fill_color: str,
        fill_opacity: float,
        stroke_color: str,
        stroke_width: float,
        text_color: str,
        font_size: int,
        corner_radius: float,
        height: float,
        h_padding: float,
    ) -> None:
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.text_color = text_color
        self.font_size = font_size
        self.corner_radius = corner_radius
        self.height = height
        self.h_padding = h_padding

    def merged(self, **overrides) -> "BadgeStyle":
        data = {slot: getattr(self, slot) for slot in self.__slots__}
        data.update(overrides)
        return BadgeStyle(**data)


BADGE_PRESETS: dict[str, BadgeStyle] = {
    "move": BadgeStyle(
        fill_color=CHARCOAL,
        fill_opacity=0.82,
        stroke_color=YELLOW,
        stroke_width=2.0,
        text_color=PAPER,
        font_size=52,
        corner_radius=0.16,
        height=0.92,
        h_padding=0.55,
    ),
    "definition": BadgeStyle(
        fill_color=DARKBLUE,
        fill_opacity=0.94,
        stroke_color=YELLOW,
        stroke_width=2.4,
        text_color=PAPER,
        font_size=34,
        corner_radius=0.14,
        height=0.82,
        h_padding=0.42,
    ),
    "theorem": BadgeStyle(
        fill_color="#4A2E3F",
        fill_opacity=0.94,
        stroke_color=MAGENTA,
        stroke_width=2.4,
        text_color=PAPER,
        font_size=34,
        corner_radius=0.14,
        height=0.82,
        h_padding=0.42,
    ),
    "proof": BadgeStyle(
        fill_color="#4A2E3F",
        fill_opacity=0.94,
        stroke_color=MAGENTA,
        stroke_width=2.4,
        text_color=PAPER,
        font_size=34,
        corner_radius=0.14,
        height=0.82,
        h_padding=0.42,
    ),
    "axiom": BadgeStyle(
        fill_color="#5B5128",
        fill_opacity=0.94,
        stroke_color=YELLOW,
        stroke_width=2.4,
        text_color=PAPER,
        font_size=34,
        corner_radius=0.14,
        height=0.82,
        h_padding=0.42,
    ),
    "proposition": BadgeStyle(
        fill_color="#304A57",
        fill_opacity=0.94,
        stroke_color=CYAN,
        stroke_width=2.4,
        text_color=PAPER,
        font_size=34,
        corner_radius=0.14,
        height=0.82,
        h_padding=0.42,
    ),
    "notation": BadgeStyle(
        fill_color=DARKBLUE,
        fill_opacity=0.88,
        stroke_color=CYAN,
        stroke_width=1.6,
        text_color=PAPER,
        font_size=24,
        corner_radius=0.10,
        height=0.52,
        h_padding=0.28,
    ),
}


BADGE_TITLES: dict[str, str] = {
    "definition": "定义",
    "theorem": "定理",
    "proof": "证明",
    "axiom": "公理",
    "proposition": "命题",
    "notation": "记号",
}

BADGE_PREFIX_COLORS: dict[str, str] = {
    "definition": YELLOW,
    "theorem": YELLOW,
    "proof": YELLOW,
    "axiom": YELLOW,
    "proposition": YELLOW,
    "notation": CYAN,
}


def _course_text(text: str, font_size: int, color: str) -> Text:
    value = Text(text, font=FONT, font_size=font_size, color=color)
    value.set_stroke(CHARCOAL, width=1.8, opacity=0.75, background=True)
    return value


def course_badge(
    body: str | Mobject | None,
    *,
    preset: str = "definition",
    title: str | None = None,
    label: str = "",
    prefix: str | None = None,
    prefix_color: str | None = None,
    body_color: str | None = None,
    y: float | None = None,
    v_padding: float = 0.24,
    **style_overrides,
) -> VGroup:
    """Frame course text or a custom mobject using a named visual preset.

    ``title`` and ``label`` build a prefix such as ``定理 1.1：``. When
    ``label`` is supplied without ``title``, the title associated with the
    preset is used. ``prefix`` remains available for fully custom wording.

    Examples::

        course_badge("有限群元素", preset="theorem", title="定理", label="1.1")
        course_badge("群元素数量", preset="notation", title="记号")
        course_badge(custom_vgroup, preset="theorem")
    """
    style = BADGE_PRESETS[preset].merged(**style_overrides)
    resolved_body_color = body_color or style.text_color
    resolved_prefix_color = prefix_color or BADGE_PREFIX_COLORS.get(preset, resolved_body_color)

    if prefix is None:
        resolved_title = title
        if resolved_title is None and label:
            resolved_title = BADGE_TITLES.get(preset)
        if resolved_title:
            prefix = f"{resolved_title} {label}：" if label else f"{resolved_title}："

    prefix_mobject = _course_text(prefix, style.font_size, resolved_prefix_color) if prefix else None
    if isinstance(body, str):
        body_mobject = _course_text(body, style.font_size, resolved_body_color) if body else None
    else:
        body_mobject = body

    parts = [part for part in (prefix_mobject, body_mobject) if part is not None]
    if not parts:
        raise ValueError("course_badge requires body text/mobject or a title/prefix")
    if len(parts) == 1:
        content = parts[0]
    else:
        content = VGroup(*parts).arrange(RIGHT, buff=0.28, aligned_edge=DOWN)

    box = RoundedRectangle(
        width=max(2.4, content.width + 2 * style.h_padding),
        height=max(style.height, content.height + 2 * v_padding),
        corner_radius=style.corner_radius,
        fill_color=style.fill_color,
        fill_opacity=style.fill_opacity,
        stroke_color=style.stroke_color,
        stroke_width=style.stroke_width,
    )
    content.move_to(box)
    badge = VGroup(box, content)
    if y is not None:
        badge.set_y(y)
    return badge


def def_heading(body: str | Mobject, *, label: str = "", y: float = 2.95, **style) -> VGroup:
    return course_badge(body, preset="definition", title="定义", label=label, y=y, **style)


def theorem_heading(body: str | Mobject, *, label: str = "", y: float = 2.95, **style) -> VGroup:
    return course_badge(body, preset="theorem", title="定理", label=label, y=y, **style)


def axiom_heading(body: str | Mobject, *, label: str = "", y: float = 2.95, **style) -> VGroup:
    return course_badge(body, preset="axiom", title="公理", label=label, y=y, **style)


def proposition_heading(body: str | Mobject, *, label: str = "", y: float = 2.95, **style) -> VGroup:
    """A proposition is a formally stated mathematical “命题”."""
    return course_badge(body, preset="proposition", title="命题", label=label, y=y, **style)


def proof_heading(body: str | Mobject | None = None, *, label: str = "", y: float = 2.95, **style) -> VGroup:
    return course_badge(body, preset="proof", title="证明", label=label, y=y, **style)


def notation_tag(text: str, *, include_title: bool = False, label: str = "", **style) -> VGroup:
    title = "记号" if include_title else None
    return course_badge(text, preset="notation", title=title, label=label, **style)


def grow_def_heading(
    scene,
    badge: VGroup,
    new_body: str,
    *,
    old_body: str,
    label: str = "",
    y: float = 2.95,
    run_time: float = 0.65,
    prefix_color: str = YELLOW,
    body_color: str | None = None,
    **style,
) -> VGroup:
    """Extend an inline definition badge while keeping its center fixed."""
    suffix_text = new_body[len(old_body) :]
    if not suffix_text:
        return badge

    target = def_heading(
        new_body,
        label=label,
        y=y,
        prefix_color=prefix_color,
        body_color=body_color,
        **style,
    )
    target.move_to(badge)

    style_obj = BADGE_PRESETS["definition"].merged(**style)
    resolved_body_color = body_color or style_obj.text_color
    label_target = badge[1].copy().align_to(target[1], LEFT)
    suffix = _course_text(suffix_text, style_obj.font_size, resolved_body_color)
    suffix.next_to(label_target, RIGHT, buff=0.04, aligned_edge=DOWN)

    scene.fix(suffix)
    scene.play(
        badge[0].animate.stretch_to_fit_width(target[0].width),
        badge[1].animate.move_to(label_target),
        FadeIn(suffix, shift=LEFT * 0.06),
        run_time=run_time,
    )
    scene.remove(suffix)
    scene.fix(target)
    scene.remove(badge)
    scene.add(target)
    return target


__all__ = [
    "BADGE_PRESETS",
    "BADGE_PREFIX_COLORS",
    "BADGE_TITLES",
    "BadgeStyle",
    "axiom_heading",
    "course_badge",
    "def_heading",
    "grow_def_heading",
    "notation_tag",
    "proof_heading",
    "proposition_heading",
    "theorem_heading",
]
