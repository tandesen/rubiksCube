"""Backwards-compatible import location for the pocket cube.

The 2x2 is now just ``RubiksCube(dim=2)``; see :mod:`.cube`.
"""

from .cube import RubiksCube2x2

__all__ = ["RubiksCube2x2"]
