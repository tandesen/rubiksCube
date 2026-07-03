# Center Turn Demo

This folder contains two standalone implementations for the same short cube-video beat:

1. `code/route_a_css3d.html` - a self-contained CSS 3D style cube inspired by iamthecu.be.
2. `code/route_a_course_theme.html` - a course-facing wrapper for Route A with a light TED-like background and no captions.
3. `code/route_d_iamthecube_api.html` - a local page that loads the cached Cuber framework from `research/iamthecube/` and drives it through `cube`, `ERNO.Group`, CSS center highlighting, and `cube.twist(...)`.

Both videos show:

- the three visible face centers holding a highlight for 1.5 seconds for "保持各面中心不动";
- three continuous turns: front, right, up, without per-move text labels.
- Route A dims surrounding cubelets during the center highlight.
- Route A fades sticker backs toward black plastic during twists to reduce CSS 3D black-flash gaps.
- Route A Course uses the same cube animation with `theme=course&captions=0`.
- Route A Transparent uses the same cube animation plus a black/white mask pass, then encodes ProRes 4444 alpha for editing.
- Route D keeps surrounding cubelets normal and makes Cuber's internal introverted faces transparent to avoid black flashes during twists.

Edit workflow:

- Change visual style, captions, camera angle, highlight timing, or turn sequence in the HTML files.
- Change output resolution, fps, duration, frame folders, or mp4 filenames in `code/render_with_chrome.mjs`.
- Route A is a hand-written CSS 3D cube with a small built-in cube state model.
- Route D calls the cached Cuber/iamthecu.be API and drives turns with `cube.twist(...)`.

Render both videos:

```sh
node experiments/center-turn-demo/code/render_with_chrome.mjs both
```

Render the light course-theme Route A video:

```sh
node experiments/center-turn-demo/code/render_with_chrome.mjs route_a_course
```

Render the transparent/alpha Route A video:

```sh
node experiments/center-turn-demo/code/render_with_chrome.mjs route_a_transparent
```

Outputs:

- `videos/route_a_css3d_center_turns.mp4`
- `videos/route_a_course_theme_center_turns.mp4`
- `videos/route_a_transparent_center_turns.mov`
- `videos/route_d_iamthecube_api_center_turns.mp4`

Frames are written under `frames/` and can be deleted/regenerated.

Editing notes:

- Use `route_a_course_theme_center_turns.mp4` when the cube clip should already include a TED-like light cartoon background.
- Use `route_a_transparent_center_turns.mov` when the cube should sit on top of a Manim scene or a Jianying background layer. If Jianying does not read the ProRes alpha channel on your machine, use the course-theme MP4 as a full-screen cutaway, or render a separate chroma-key version by changing the transparent theme background to a key color.
- For a full-screen cutaway, exact background matching is less important. For overlaying the cube over Manim, alpha/chroma-key is more reliable than trying to make two independently rendered backgrounds identical.
