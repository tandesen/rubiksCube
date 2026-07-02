#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv/bin/manim" ]; then
  echo "Missing .venv/bin/manim. Install with:"
  echo "  /opt/homebrew/bin/python3.12 -m venv .venv"
  echo "  .venv/bin/python -m pip install --upgrade pip manim"
  exit 1
fi

if [ ! -d "node_modules/cubing" ]; then
  echo "Missing node_modules/cubing. Installing npm dependencies..."
  npm install
fi

mkdir -p renders media assets/generated

npm run cube-assets

.venv/bin/manim -qm --media_dir media manim_scenes/lesson_01_opening.py OpeningScaleScene
.venv/bin/manim -qm --media_dir media manim_scenes/lesson_01_opening.py GroupTheoryBridgeScene

OPENING_SEGMENT="$(find media/videos/lesson_01_opening/720p30 -name 'OpeningScaleScene.mp4' -print -quit)"
BRIDGE_SEGMENT="$(find media/videos/lesson_01_opening/720p30 -name 'GroupTheoryBridgeScene.mp4' -print -quit)"

if [ -z "$OPENING_SEGMENT" ] || [ -z "$BRIDGE_SEGMENT" ]; then
  echo "Could not find rendered Manim segments."
  exit 1
fi

OPENING_SEGMENT="$ROOT_DIR/$OPENING_SEGMENT"
BRIDGE_SEGMENT="$ROOT_DIR/$BRIDGE_SEGMENT"

printf "file '%s'\nfile '%s'\n" "$OPENING_SEGMENT" "$BRIDGE_SEGMENT" > renders/lesson_01_concat.txt

ffmpeg -hide_banner -y \
  -f concat -safe 0 -i renders/lesson_01_concat.txt \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
  renders/lesson_01_opening_demo.mp4

echo "Rendered: renders/lesson_01_opening_demo.mp4"
