# iamthecu.be 魔方技术与视觉分析

分析对象：<https://iamthecu.be/>  
本地缓存：`research/iamthecube/`  
分析日期：2026-07-03

## 0. 工具与环境说明

`codex` 命令确实没有在当前 zsh 的 `PATH` 中。我已在 `~/.zshrc` 追加：

```sh
export PATH="/Applications/Codex.app/Contents/Resources:$PATH"
```

新终端会直接生效；已打开的终端需要运行 `source ~/.zshrc`。

同时已执行：

```sh
codex mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

`codex mcp list` 已显示 `chrome-devtools` 为 enabled。重启 Codex 后，当前会话已经可以调用 `mcp__chrome_devtools`，并成功打开真实页面 `https://iamthecu.be/`。本报告结论已用 DevTools 的 Network、Console、Snapshot、Runtime evaluate 做过复查。

DevTools 实测补充：

- 页面请求总数 37 个。
- 运行时没有 `<canvas>`，`.cubelet` 为 27 个，`.cubelet > .face` 为 162 个，`.sticker` 为 54 个。
- 运行时暴露 `cube`、`ERNO`、`THREE`、`TWEEN`、`_`、`help`。
- `cube.twistDuration` 为 1000，`ERNO.Cube.prototype.twistDuration` 为 700。
- `cube.camera.position.z` 为 2800，`cube.camera.fov` 为 25。

## 1. 主要 JS/CSS 文件

HTML 入口在 `research/iamthecube/index.html`。主要资源如下：

| 类型 | 文件 | 作用 |
| --- | --- | --- |
| CSS | `styles/cube.css` | 魔方 DOM 结构样式：`.cube`、`.cubelet`、`.face`、`.sticker`、`.wireframe`、贴纸圆角和基础颜色。 |
| CSS | `styles/explorer.css` | 页面布局、背景、导航、文字板、站点级贴纸颜色覆盖、玻璃模式颜色覆盖。 |
| JS | `scripts/bowser.min.js` | 浏览器检测。 |
| JS | `scripts/cuber.min.js` | Cuber 核心框架，内含旧版 `THREE`、`TWEEN`、`CSS3DRenderer`、`Cube`、`Cubelet`、`Slice`、`Queue`、`Twist`。 |
| JS | `scripts/patches.js` | 对 Cuber 的补丁，包括 `inspect()`、`showLogo()`、`hideLogo()`、默认动画时长修正、`shuffle()`、`undo()`。 |
| JS | `scripts/buttons.js` | 底部交互按钮：Grid、Glass、Cubelets 高亮、Labels、Rotate、Realign、Shuffle、Undo、Demo。 |
| JS | `scripts/demos.js` | 自动演示脚本和分镜任务队列。 |
| JS | `scripts/explorer.js` | 页面启动入口，创建 `window.cube`，调整相机，入场动画，控制台 help，键盘/鼠标交互。 |
| 外部 JS | `https://www.google-analytics.com/analytics.js` | Google Analytics。 |
| 字体 | `media/fonts/Rubik.otf`、`media/fonts/RubikExtended.otf` | 标题、面标签、文字板字体。 |
| 图片 | `media/buttons/*.png`、`media/share/*.png`、`media/badges/*.png`、`media/rubiksLogoClassic.png` | 底部按钮、分享按钮、Chrome Cube Lab 标识、白色中心 logo 贴纸。 |

证据位置：

- `index.html` 第 13-22 行列出 CSS/JS。
- `index.html` 第 23-30 行加载 Google Analytics。
- DevTools Network 复查显示 `styleGrid.png`、`styleGlass.png`、`highlightCenters.png` 等按钮图标也会在页面加载后请求。
- 本地文件大小：`cuber.min.js` 约 120 KB，是核心文件。

## 2. 魔方实现方式

结论：这是 Three.js 对象模型加 CSS 3D DOM 渲染，不是 Canvas，也不是 WebGL。

关键证据：

- `cuber.min.js` 定义 `THREE.CSS3DObject` 和 `THREE.CSS3DRenderer`，通过 DOM 元素和 CSS `matrix3d(...)` 渲染，见 `cuber.min.js` 第 262-267 行。
- Cuber 默认 renderer 是 `ERNO.renderers.CSS3D`，见 `cuber.min.js` 第 340 行。
- renderer 会创建 `THREE.CSS3DRenderer`，把 cube、camera 和 face labels 放进 CSS3D scene，见 `cuber.min.js` 第 328-330 行。
- 每个 cubelet 被渲染为一个 DOM `div.cubelet` 和 6 个 DOM face，见 `cuber.min.js` 第 331-334 行。
- 搜索本地源码没有发现 `<canvas>`、`WebGLRenderer`、`CanvasRenderer`、`getContext()`。

所以更准确的分类是：

```text
Three.js scene graph
+ THREE.CSS3DRenderer
+ DOM div faces
+ CSS transform-style: preserve-3d
+ TWEEN.js animation
```

## 3. cubelets 的 DOM/对象结构

### 对象结构

`window.cube = new ERNO.Cube()` 在 `explorer.js` 第 44 行创建。

`ERNO.Cube` 内部结构：

- `cube.cubelets`：27 个 `ERNO.Cubelet`，包括不可见/可隐藏的 core。
- `cube.core`、`cube.centers`、`cube.edges`、`cube.corners`、`cube.crosses`：按类型分组。
- `cube.front`、`cube.up`、`cube.right`、`cube.down`、`cube.left`、`cube.back`：6 个面 slice。
- `cube.left/middle/right`、`cube.up/equator/down`、`cube.front/standing/back`：9 个实体 slice。
- `cube.slicesDictionary`：把 `f/s/b/u/e/d/r/m/l/x/y/z` 映射到 slice 或整 cube rotation slice。

证据：`cuber.min.js` 第 341-349 行。

`ERNO.Cubelet`：

- 继承 `THREE.Object3D`。
- `id` 为 0-26。
- `addressX/Y/Z` 表示当前格位地址；转动后会随 slice mapping 更新。
- `id` 和 DOM class `cubeletId-N` 是 cubelet 身份，`cube.cubelets[index]` 的 index 更接近当前位置映射。DevTools 运行时复查时，页面 demo 已经转动过，`cube.cubelets[0].id` 不一定是 0，这验证了“身份”和“位置”要分开理解。
- `faces` 长度为 6，顺序是 `front, up, right, down, left, back`。
- `type` 根据外露颜色数计算：`core`、`center`、`edge`、`corner`。
- `front/up/right/down/left/back` 是 `faces[0..5]` 的别名。

证据：`cuber.min.js` 第 291-294 行。

### DOM 结构

每个 cubelet 的 DOM 大致为：

```html
<div class="cubelet cubeletId-0">
  <div class="face axisZ faceFront faceExtroverted">
    <div class="wireframe"></div>
    <div class="id"><span class="underline">0</span></div>
    <div class="sticker white stickerLogo"></div>
    <div class="text">0</div>
  </div>
  <div class="face axisY faceUp faceExtroverted">...</div>
  <div class="face axisX faceRight faceIntroverted">...</div>
  <div class="face axisY faceDown faceIntroverted">...</div>
  <div class="face axisX faceLeft faceExtroverted">...</div>
  <div class="face axisZ faceBack faceIntroverted">...</div>
</div>
```

实际是否 `faceExtroverted` 取决于该 cubelet 这一面有没有颜色。没有颜色的内面是 `faceIntroverted`，背景黑色。每个 face 都先创建 `.wireframe` 和 `.id`，外露面再创建 `.sticker` 和 `.text`。

证据：`cuber.min.js` 第 331-334 行，`cube.css` 第 68-78、96-135、167-212、223-275 行。

每个 face 的 CSS 3D 方向由 inline transform 控制：

| Face | transform 逻辑 |
| --- | --- |
| front | `rotateX(0deg) translateZ(size/2)` |
| up | `rotateX(90deg) translateZ(size/2)` |
| right | `rotateY(90deg) translateZ(size/2)` |
| down | `rotateX(-90deg) translateZ(size/2) rotateZ(90deg)` |
| left | `rotateY(-90deg) translateZ(size/2) rotateZ(-90deg)` |
| back | `rotateY(180deg) translateZ(size/2) rotateZ(-90deg)` |

证据：`cuber.min.js` 第 331-333 行。

## 4. 旋转动画：缓动、时长、触发方式

### 默认和页面修正时长

Cuber 核心默认 `twistDuration` 是 500ms，见 `cuber.min.js` 第 341 行。`patches.js` 又把 prototype 默认改为：

```js
ERNO.Cube.prototype.opacityTweenDuration = 200
ERNO.Cube.prototype.radiusTweenDuration = 100
ERNO.Cube.prototype.twistDuration = 700
```

见 `patches.js` 第 452-454 行。

页面启动时又对实例设置：

```js
cube.twistDuration = 1000
```

见 `explorer.js` 第 92 行。

demo 中会临时调节：

- 复原用 `twistDuration = 50`，见 `demos.js` 第 47-49 行。
- 中心演示用 `1000` 后改回 `500`，见 `demos.js` 第 401-408 行。
- 统计演示用 `300`，见 `demos.js` 第 542-543 行。

### 单次 twist 动画

`cube.twist(...)` 只把动作放进 `twistQueue`。真正执行发生在 `loop()` 中，等 cube ready 且没有 tween 后调用 `immediateTwist()`。

`immediateTwist()` 核心逻辑：

- 找到对应 slice：`this.slicesDictionary[a.command.toLowerCase()]`。
- 把目标角度转成弧度。
- 动画时长按角度比例计算：`abs(targetRotation - currentRotation) / (0.5 * PI) * twistDuration`。
- 对 slice 自身做 `new TWEEN.Tween(slice).to({ rotation }, duration)`。
- 缓动：`TWEEN.Easing.Quartic.Out`。
- 完成后更新 cubelet 矩阵和 slice/group mapping，触发 `onTwistComplete`。

证据：`cuber.min.js` 第 352-357 行。

### 入场动画

页面开场不是简单显示魔方，而是做“反向爆炸组合”：

- 整体位置：`y = -2000` 到 `y = 90`，2 秒，`Quartic.Out`。
- 整体旋转：`(120, 420, 20)` 度到 `(20, -30, 0)` 度，4 秒，`Quartic.Out`。
- 每个 cubelet 从 `addressX/Y/Z * 1000` 的爆炸位置回到原位，持续 1 秒，`Quintic.Out`。
- cubelet 延迟按类型错开：core 0ms，center 200-500ms，edge 800-1000ms，corner 1100-1500ms。

证据：`explorer.js` 第 62-92、98-158 行。

### 触发方式

触发入口：

- 控制台：`cube.twist('rdRD')` 或 `cube.twist('rdRD'.multiply(6))`。
- 键盘：`XxRrMmLlYyUuEeDdZzFfSsBb` 直接触发 twist，见 `cuber.min.js` 第 349-350 行。
- 方向键：左/右/上/下映射到 `Y/y/X/x`，见 `explorer.js` 第 413-416 行。
- 鼠标/触摸拖拽：`ERNO.Interaction` 用 ray/plane 交点判断被拖动的 cubelet 和 slice，然后调用 `cube.twist(new ERNO.Twist(...))`，见 `cuber.min.js` 第 317-323 行。
- 页面按钮：`buttons.js` 控制 rotate、realign、shuffle、undo、demo，见 `buttons.js` 第 296-335 行。

## 5. 颜色、贴纸、玻璃、阴影、相机视角

### 背景与页面

背景是黑色径向渐变：

```css
radial-gradient(ellipse at center, #444 0%, #000 90%)
```

证据：`explorer.css` 第 18-27 行。

底部 footer 是深灰线性渐变，分享按钮默认 `opacity: 0.1`，hover 变 1，见 `explorer.css` 第 541-600 行。

### 贴纸颜色

`cube.css` 有一套基础颜色，但站点实际覆盖为：

| 颜色 | CSS |
| --- | --- |
| red | `#C00` |
| white | `#EEE` |
| blue | `#25D` |
| green | `#092` |
| orange | `#E60` |
| yellow | `#FC0` |

证据：`explorer.css` 第 95-102 行。

贴纸本身：

- `.sticker` 宽高 100%。
- `border-radius: 0.1em`。
- face 有 `padding: 0.05em`，所以能看到黑色塑料边框。

证据：`cube.css` 第 96-107、193-199 行。

### 玻璃效果

Glass 模式不是 shader，也不是真正的 WebGL 透明材质。它给所有 `.cubelet` 加 `.purty`：

```js
document.querySelectorAll('.cubelet').forEach(e => e.classList.add('purty'))
```

见 `buttons.js` 第 157-164 行。

`.purty` 的效果：

- `.purty .face { opacity: 0.5; }`
- face 背景直接变成六面颜色。
- `.purty .sticker { background-color: transparent !important; }`

基础定义见 `cube.css` 第 141-148 行；站点覆盖面色见 `explorer.css` 第 105-112 行。

预览图 `research/iamthecube/media/cubeExplorer.jpg` 显示的就是这种玻璃风格：半透明彩色面片互相叠色，边缘没有真实光照阴影，视觉上靠 CSS opacity 和面片重叠形成“玻璃”感。

![iamthecu.be preview](research/iamthecube/media/cubeExplorer.jpg)

### Grid 和高亮

Grid 模式：

- `cube.showWireframes().hidePlastics().hideStickers()`
- wireframe 是 2px 半透明白边，背景 `rgba(255,255,255,0.05)`。

证据：`buttons.js` 第 140-153 行，`cube.css` 第 167-181 行。

Cubelets 高亮：

- included group 维持 `opacity = 1`。
- excluded group 设为 `opacity = 0.15`。

证据：`buttons.js` 第 205-214 行。

### 阴影

魔方块面本身没有传统 `box-shadow`。视觉深度主要来自：

- CSS 3D perspective。
- 黑色 introverted/internal faces。
- 透明面片重叠。
- 文字 label 和 board 的 `text-shadow`。

Face label 的阴影见 `cube.css` 第 47-55 行；board 文字阴影见 `explorer.css` 第 117-137 行。

### 相机视角

Cuber 默认：

- `PerspectiveCamera(35, window.innerWidth / window.innerHeight, 1, 6000)`。
- `camera.position.z = 4 * cube.size`。
- 初始 cube rotation：x 25 deg，y -30 deg，z 0。

证据：`cuber.min.js` 第 341-342 行。

Explorer 页面覆盖：

- `camera.position.z = 2800`。
- `camera.fov = 25`。
- 入场后最终 rotation：x 20 deg，y -30 deg，z 0。

证据：`explorer.js` 第 52-85 行。

默认 `textureSize = 120`，所以 `size = 360`，`cubeletSize = 120`，renderer DOM 的 `fontSize` 也是 `120px`，见 `cuber.min.js` 第 340-348 行。

## 6. 暴露的 console API

页面在 `window` 暴露：

- `window.cube`
- `window.ERNO`
- `window._`
- `window.TWEEN`
- `window.THREE`
- `window.help`

证据：`explorer.js` 第 313-332 行，`cuber.min.js` 第 361-364 行。

页面 help 和 HTML 文案明确鼓励在控制台使用：

```js
cube.twist('rdRD'.multiply(6))
cube.inspect()
cube.front.inspect()
cube.front.northEast.inspect()
cube.front.northWest.up.color.name
cube.standing.setOpacity(0.5)
cube.corners.setRadius(90)
cube.hasColors(ERNO.RED, ERNO.BLUE).showIds()
cube.showIds().setOpacity(0.1).core.setOpacity()
cube.hasAddress(0).setOpacity()
cube.hasAddress(26).setOpacity()
```

证据：`index.html` 第 115-134 行，`explorer.js` 第 313-329 行。

补丁 API：

- `ERNO.Cubelet.prototype.inspect(face)`：输出 cubelet 的 ID、type、address、engaged/tweening 状态和各面颜色，见 `patches.js` 第 138-190 行。
- `ERNO.Group.prototype.inspect(face)`：遍历 group 内 cubelets，见 `patches.js` 第 270-277 行。
- `ERNO.Slice.prototype.inspect(compact, side)`：输出 3x3 slice 的彩色 ASCII 图，见 `patches.js` 第 289-360 行。
- `ERNO.Cube.prototype.inspect(compact, side)`：依次 inspect 六个面，见 `patches.js` 第 459-469 行。
- `ERNO.Cube.prototype.showLogo()` / `hideLogo()`：控制白色中心贴纸 logo，见 `patches.js` 第 564-575 行。

常用对象/组 API：

- `cube.twist(...)`、`cube.shuffle()`、`cube.undo()`、`cube.redo()`、`cube.isSolved()`。
- `cube.showIds()`、`hideIds()`、`showTexts()`、`hideTexts()`、`showWireframes()`、`hideWireframes()`、`showPlastics()`、`hidePlastics()`、`showStickers()`、`hideStickers()`。
- `cube.setOpacity(value)`、`cube.setRadius(value)`。
- `cube.hasColor(color)`、`cube.hasColors(...)`、`cube.hasAddress(n)`、`cube.hasType(type)`。
- Slice/group selectors such as `cube.front.northEast`、`cube.front.east`、`cube.centers`、`cube.edges`、`cube.corners`、`cube.standing`。

## 7. 本地复刻或录制路线

### 路线 A：复刻同风格 CSS 3D demo

最接近原站的做法是 Three.js `CSS3DRenderer`。

建议结构：

```text
Scene
  Object3D cubeRoot
    Object3D cubelet[27]
      CSS3DObject div.cubelet
        div.face.faceFront
          div.sticker.white
        div.face.faceUp
        div.face.faceRight
        div.face.faceDown
        div.face.faceLeft
        div.face.faceBack
```

关键视觉参数：

```css
body {
  background: radial-gradient(ellipse at center, #444 0%, #000 90%);
}

.cubelet {
  position: absolute;
  width: 1em;
  height: 1em;
}

.face {
  position: absolute;
  width: 1em;
  height: 1em;
  padding: 0.05em;
  background: #000;
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

.sticker {
  width: 100%;
  height: 100%;
  border-radius: 0.1em;
}

.glass .face {
  opacity: 0.5;
}
```

转动实现：

1. 维护 27 个 cubelet 的 logical address。
2. 每次 move 选择 slice cubelets。
3. 把它们临时挂到一个 pivot group。
4. tween pivot rotation 到 90 deg。
5. 动画完成后把 cubelet 世界矩阵 bake 回各自 Object3D，并更新 logical address。

这个路线最适合课程视频，因为 DOM face/sticker 可以直接做文字、编号、半透明、边框、高亮，不需要处理 shader。

### 路线 B：Three.js WebGL demo

如果目标是更稳定的视频渲染、真实阴影、景深和灯光，建议用 WebGL：

- 每个 cubelet 用 `BoxGeometry`。
- 每个可见面使用单独 material。
- 黑色塑料边框可用略大的黑色 cubelet 加彩色贴纸 plane，或用 bevel geometry。
- 玻璃模式用 `transparent: true`、`opacity: 0.45`，再加 `depthWrite: false` 和排序控制。
- 课程渲染可用固定相机 `fov = 25`，rotation 约 x 20 deg、y -30 deg。

WebGL 的优点是录制稳定、像素一致、可以加阴影。缺点是做出原站那种 DOM/贴纸文字/console inspect 风格会更麻烦。

### 路线 C：cubing.js 做状态与算法，Three/CSS 做画面

当前项目已有 `cubing@0.63.3`。本机验证可用导出：

```js
import { Alg, Move } from 'cubing/alg'
import { cube3x3x3 } from 'cubing/puzzles'
import { KPuzzle, KPattern, KTransformation } from 'cubing/kpuzzle'
```

建议分工：

- `cubing/alg`：解析课程脚本中的算法，如 `new Alg("R U R' U'")`。
- `cubing/kpuzzle` 或 puzzle 定义：维护合法状态、验证算法、生成状态。
- 自己的 renderer：只负责把每一步 move 动画出来。

也就是说，`cubing.js` 不负责复刻 iamthecu.be 的视觉，适合作为“魔方状态真相层”。这样课程视频里所有转动、交换子、复原步骤都可验证，不靠手写状态更新猜。

### 路线 D：直接用 iamthecu.be API 录制

可行，但不建议作为长期课程生产主线。

可以在浏览器 console 里驱动：

```js
cube.twistDuration = 900
cube.showIds()
cube.corners.setRadius(90)
cube.hasColors(ERNO.RED, ERNO.BLUE).setOpacity(1)
cube.twist("RUruruUR")
```

录制方式：

1. 用 Chrome DevTools MCP 或 Puppeteer 打开页面。
2. 等待 `window.cube` 存在。
3. 注入脚本设置相机、样式和动作队列。
4. 使用 Chrome screencast 或逐帧 screenshot。
5. 用 `ffmpeg` 合成视频。

示例伪代码：

```js
await page.goto('https://iamthecu.be/')
await page.waitForFunction('window.cube && window.cube.isReady')
await page.evaluate(() => {
  cube.twistDuration = 900
  cube.showIds()
  cube.corners.setRadius(90)
  cube.twist("R U R' U'")
})
```

风险：

- 该站是老项目，依赖旧版 Three/TWEEN 和浏览器 CSS3D 行为。
- 生产视频不应依赖第三方站点可用性。
- 原站资源和代码授权需要单独确认，课程中直接使用应谨慎。

### 推荐

课程视频主线建议用：

```text
cubing.js 负责算法和状态
Three.js WebGL 或 CSS3DRenderer 负责画面
ffmpeg 负责合成
```

如果要复刻 iamthecu.be 的“玻璃、编号、文字板、console 可玩”风格，优先选 CSS3DRenderer。  
如果要追求高质量课程成片和可控光影，优先选 Three.js WebGL。  
如果要做数学/群论内容，`cubing.js` 应作为状态验证层，避免动画和魔方合法性脱节。
