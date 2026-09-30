#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
echo '网站预览：http://127.0.0.1:4173'
echo '按 Ctrl+C 停止预览。'
exec python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
