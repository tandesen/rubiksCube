"""Cube appearance settings.

A :class:`CubeStyle` bundles every purely-visual decision about a cube:
sticker palette, seam (gap) color and width, rounded sticker corners,
whether stickers sit inset on a dark plastic plate (the "realistic" look),
3D shading, and the ground shadow.

Use one of the presets and tweak from there::

    style = CubeStyle.cartoon()                       # 当前视频里的默认样式
    style = CubeStyle.realistic()                     # 仿真实速拧魔方
    style = CubeStyle.cartoon().with_(seam_width=2.2) # 在预设上微调

``RubiksCube(style="realistic")`` also accepts the preset name directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .cube_utils import FACE_ORDER

# ---------------------------------------------------------------------------
# Palettes, in kociemba face order: U, R, F, D, L, B.
# ---------------------------------------------------------------------------

#: The illustrative palette used by the lesson videos (德森's brand look).
CARTOON_PALETTE = {
    "U": "#2C74C9",  # blue
    "R": "#D64235",  # red
    "F": "#F3D34A",  # yellow
    "D": "#31B56A",  # green
    "L": "#F08A33",  # orange
    "B": "#F8F6EF",  # white
}

#: Standard western (BOY) color scheme.
CLASSIC_PALETTE = {
    "U": "#FFFFFF",  # white
    "R": "#C41E3A",  # red
    "F": "#009E60",  # green
    "D": "#FFD500",  # yellow
    "L": "#FF5800",  # orange
    "B": "#0051BA",  # blue
}

#: Slightly muted stickers that read well on dark plastic.
REALISTIC_PALETTE = {
    "U": "#E8E9E4",  # off-white
    "R": "#B92F3D",  # red
    "F": "#168A57",  # green
    "D": "#E7C43A",  # yellow
    "L": "#DE702B",  # orange
    "B": "#315FA9",  # blue
}


def _as_color_dict(colors) -> dict[str, str]:
    """Accept either a URFDLB-ordered list/tuple or a face->color dict."""
    if isinstance(colors, dict):
        missing = [f for f in FACE_ORDER if f not in colors]
        if missing:
            raise ValueError(f"colors dict is missing faces: {missing}")
        return {f: colors[f] for f in FACE_ORDER}
    colors = list(colors)
    if len(colors) != 6:
        raise ValueError("colors must contain six entries in URFDLB order")
    return dict(zip(FACE_ORDER, colors))


@dataclass
class CubeStyle:
    """All purely-visual settings of a cube.

    Parameters
    ----------
    face_colors
        Sticker colors keyed by face letter (URFDLB).
    inner_color
        Color of the plastic inside the cube (visible while a layer turns).
    seam_color, seam_width
        Stroke drawn around each facelet; this is what reads as the gap
        between cubies. Note stroke width is *absolute* in Manim: it does not
        change when you ``scale()`` the cube.
    corner_radius
        Sticker corner radius as a fraction of the sticker side
        (0 = sharp square, ~0.2 = friendly rounded sticker).
    sticker_inset
        If > 0, each visible sticker shrinks by this fraction per edge and is
        drawn on top of a plastic plate, like a real speedcube. 0 keeps the
        flat cartoon look.
    shade_in_3d, sheen
        Passed to Manim so the ThreeDCamera lights faces differently and adds
        a soft highlight (only meaningful for the realistic look).
    shadow, shadow_color, shadow_opacity
        Ground shadow settings. The shadow is part of the cube group, so it
        follows the cube when you move or scale it.
    """

    face_colors: dict[str, str] = field(default_factory=lambda: dict(CARTOON_PALETTE))
    inner_color: str = "#1E1E1E"
    seam_color: str = "#232323"
    seam_width: float = 1.4
    corner_radius: float = 0.0
    sticker_inset: float = 0.0
    shade_in_3d: bool = False
    sheen: float = 0.0
    shadow: bool = True
    shadow_color: str = "#000000"
    shadow_opacity: float = 0.16

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------
    @classmethod
    def cartoon(cls, **overrides) -> "CubeStyle":
        """The flat, illustrative look used in the lesson videos (default)."""
        return cls(face_colors=dict(CARTOON_PALETTE)).with_(**overrides)

    @classmethod
    def classic(cls, **overrides) -> "CubeStyle":
        """The original vendored-plugin look: BOY colors, no shadow."""
        return cls(
            face_colors=dict(CLASSIC_PALETTE),
            seam_color="#1E1E1E",
            seam_width=1.5,
            shadow=False,
        ).with_(**overrides)

    @classmethod
    def realistic(cls, **overrides) -> "CubeStyle":
        """A dark-plastic speedcube: inset rounded stickers, shading, sheen."""
        return cls(
            face_colors=dict(REALISTIC_PALETTE),
            inner_color="#090B0D",
            seam_color="#050607",
            seam_width=2.8,
            corner_radius=0.18,
            sticker_inset=0.06,
            shade_in_3d=True,
            sheen=0.10,
            shadow=True,
            shadow_opacity=0.14,
        ).with_(**overrides)

    # ------------------------------------------------------------------
    # Tweaks
    # ------------------------------------------------------------------
    def with_(self, **overrides) -> "CubeStyle":
        """A copy of this style with some fields replaced."""
        if "face_colors" in overrides:
            overrides["face_colors"] = _as_color_dict(overrides["face_colors"])
        return replace(self, **overrides)

    def with_colors(self, colors) -> "CubeStyle":
        """A copy with a new palette (URFDLB list or face->color dict)."""
        return replace(self, face_colors=_as_color_dict(colors))


_PRESETS = {
    "cartoon": CubeStyle.cartoon,
    "classic": CubeStyle.classic,
    "realistic": CubeStyle.realistic,
}


def resolve_style(style) -> CubeStyle:
    """Turn ``None`` / a preset name / a CubeStyle into a fresh CubeStyle."""
    if style is None:
        return CubeStyle.cartoon()
    if isinstance(style, str):
        try:
            return _PRESETS[style.lower()]()
        except KeyError:
            raise ValueError(
                f"Unknown style preset {style!r}; expected one of {sorted(_PRESETS)}"
            ) from None
    if isinstance(style, CubeStyle):
        return style.with_()  # defensive copy so shared presets are not mutated
    raise TypeError(f"style must be None, a preset name, or CubeStyle, got {type(style)}")
