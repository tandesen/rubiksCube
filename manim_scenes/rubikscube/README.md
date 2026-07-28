# rubikscube — Manim 魔方工具包

给「群论与魔方」系列视频用的本地魔方工具包。前身是对已停止维护的
`manim-rubikscube` 插件的重写,现在整理成一套可以长期复用的小工具箱,
支持 2 阶与 3 阶魔方。

## 模块一览

| 模块 | 内容 |
| --- | --- |
| `cube.py` | `RubiksCube`(通用 2/3 阶)、`RubiksCube2x2`(便捷子类) |
| `cubie.py` | `Cubie`(单个小方块)、`CubieFace`(单张贴纸/底板) |
| `style.py` | `CubeStyle` 外观设置,`cartoon` / `classic` / `realistic` 三个预设 |
| `cube_animations.py` | `CubeMove` 转层动画(自动适配魔方当前朝向) |
| `depth.py` | `depth_sort_cube` 深度排序(解决 3D 遮挡/不透出内部黑色) |
| `highlights.py` | 三种高亮模式 + `reset_look` 一键还原 |
| `arrows.py` | 交换箭头、角块旋转箭头、棱块翻面箭头(真 3D 锚定) |
| `scenes.py` | `RubiksCubeScene` 场景基类(自动深度排序等样板代码) |
| `examples.py` | 四个演示场景,同时充当冒烟测试 |
| `cube_utils.py` | 记号解析、几何常量等底层工具 |

## 快速开始

```python
from manim import *
from rubikscube import RubiksCube, RubiksCubeScene


class MyScene(RubiksCubeScene):          # 已自动设置好 hero 相机角度
    def construct(self):
        cube = RubiksCube().scale(0.8).move_to(LEFT * 2)
        self.add_cube(cube)              # 加入场景 + 每帧自动深度排序
        self.turn(cube, "R U R' U'")     # 依次转动四步
        self.play(cube.animate.scale(0.6).move_to(self.screen_point(-5, -2)))
        self.move_camera(phi=45 * DEGREES)   # 深度排序会自动跟上
```

渲染示例场景(也是冒烟测试):

```bash
.venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py StyleTour
.venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py HighlightTour
.venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py PopAndArrowTour
.venv/bin/manim -ql --media_dir media manim_scenes/rubikscube/examples.py PocketCubeTour
```

## 外观:CubeStyle

```python
from rubikscube import RubiksCube, CubeStyle

RubiksCube()                       # 默认 = cartoon 预设(课程视频的现有样式)
RubiksCube(style="realistic")      # 仿真实速拧:深色塑料、内缩圆角贴纸、光泽
RubiksCube(style="classic")        # 原插件样式:标准 BOY 配色、无阴影

# 在预设基础上微调:
style = CubeStyle.cartoon().with_(
    seam_color="#000000",    # 缝隙颜色
    seam_width=2.2,          # 缝隙宽窄(注意:manim 的描边宽度不随 scale 缩放)
    corner_radius=0.15,      # 贴纸圆角(0 = 直角)
    sticker_inset=0.05,      # >0 时贴纸内缩、露出塑料底板(写实感)
    shadow=False,            # 地面阴影开关(阴影是 cube 的子物件,会跟随移动/缩放)
)
RubiksCube(style=style)

# 只换配色(URFDLB 顺序),仍然兼容旧写法:
RubiksCube(colors=[BLUE, RED, YELLOW, GREEN, ORANGE, WHITE])
```

大小与位置:`cubie_side=`(单块边长)或 `total_size=`(整体边长),
之后用普通 manim 链式调用摆放:`RubiksCube().scale(0.8).move_to(RIGHT * 3)`。

## 视角与深度排序

推荐用 `RubiksCubeScene`(继承 `ThreeDScene`):相机负责 3D 视角,
`add_cube()` 会每帧重新做深度排序,转层、移动相机(`self.move_camera`)、
缩放搬移魔方都不会把内部黑色透出来。

- 静态快照(复制出来不再转动的魔方)用 `self.add_cube(copy, track=False)`,
  省去每帧排序的开销;
- 不用基类时,手动 `self.add_updater(lambda dt: depth_sort_cube(cube, self.camera))`;
- 旧的 2D 烘焙视角写法仍然支持:`RubiksCube(orientation=matrix)`,
  此时 `CubeMove` 会根据魔方当前几何自动算出正确转轴
  (`OrientedCubeMove` 不再需要,但旧代码不受影响)。

## 转动

```python
self.turn(cube, "R U R' U'")            # 场景基类的便捷写法
self.play(CubeMove(cube, "R"), run_time=0.5)   # 单步,可与其他动画并行
cube.do_moves("F2 R B' U")              # 瞬间完成(用来摆打乱状态)
cube.set_state("UUUUUUUUU...")           # kociemba 54 字符贴纸串(仅 3 阶)
```

## 高亮(三种模式,均可用 `cube.reset_look()` 还原)

```python
# 1. focus:选中的方块保持亮色,其余全部变暗(开场铺垫、superflip 棱块)
self.play(cube.focus(cube.edge_cubies()))

# 2. blink:blingbling 闪一下(「上左下右」那种提示)
self.play(cube.blink(cube.layer("U")))

# 3. mark:选中方块整体涂色 + 缝隙变黑,其余缝隙变白(「交换两个方块」)
a, b = cube.cubie(0, 0, 2), cube.cubie(0, 2, 2)
self.play(cube.mark([(a, "#C23A82"), (b, "#36B8A6")]))

self.play(cube.reset_look())            # 任何组合都能一键还原
```

注意:`focus` / `mark` 不要叠加使用(变暗是在当前颜色基础上计算的),
切换模式前先 `reset_look()`。`highlights.face_rings(faces)` 可以做贴纸
描边圈(开场里中心块的白圈/黄色高亮就是它)。

## 方块弹出 / 收回

```python
corner = cube.cubie(0, 0, 2)
self.play(cube.pop_out(corner))          # 沿它自己的对角线方向滑出
# ……弹出状态下做任何演示,例如角块原地拧转:
axis = normalize(corner.get_center() - cube.get_cube_center())
self.play(Rotate(corner, angle=-2 * PI / 3, axis=axis,
                 about_point=corner.get_center()))
self.play(cube.pop_in(corner))           # 滑回原位
```

弹出方向按当前几何计算(角块=体对角线、棱块=面对角线、中心块=法线),
魔方转过、缩放过都没关系。**弹出状态下不要转动它所在的层。**
「角块三种朝向」这类具体演示保留在场景代码里写(如上),没有做成固定接口。

## 箭头

三种箭头都锚定在方块的真实 3D 坐标上,尖端会自动落在模块中心
(旧版先投影到屏幕再反变换,始终差一点,现在不需要手动修位置了):

```python
# 1. 交换两个模块(默认两条循环弧线;style="double" 为单条双头箭头)
arrows = self.swap_arrows(cube, cubie_a, cubie_b)
self.play(*[Create(part) for pair in arrows for part in pair])

# 2. 角块原地旋转指示(围绕它自己的对角线的圆弧箭头)
ring = self.twist_arrow(cube, corner, clockwise=True)

# 3. 棱块自身翻面(跨过棱线的弧线,superflip 讲解用)
flips = self.flip_arrows(cube, cube.cubie(0, 1, 2))
```

已知限制:Cairo 渲染器按 `z_index` 整体绘制,一支箭头只能整体在魔方
前面(默认)或整体在后面,做不到「半截被魔方挡住」。需要遮挡感时,
可以把 `z_index` 调低让整支箭头藏到魔方后面,或拆成两支箭头分别设置。

## 2 阶魔方

`RubiksCube2x2()` 等价于 `RubiksCube(dim=2)`,上述全部功能通用
(`set_state` 除外,贴纸串是 3 阶专用)。阶数请读 `cube.order`
(不要用 `cube.dim`,那是 manim 内部的空间维度,恒为 3)。

## 写包的几点约定(为什么这样设计)

- **动画都是「返回值」**:`cube.focus(...)`、`pop_out(...)` 等都返回
  Animation,由场景自己 `self.play(...)`,方便控制 `run_time`、并行组合。
- **样式有记忆**:每张贴纸记着自己的 `base_fill` / `base_stroke`
  (`set_state` 会更新它),所以 `reset_look()` 永远能还原,场景代码
  不用再手动保存原色列表。
- **几何自适应**:转轴、弹出方向、箭头锚点都从当前世界坐标现算,
  不依赖「魔方没被转过/摆正」的假设。
- **examples.py 就是回归测试**:改包之后把四个示例场景渲染一遍,
  能出片就说明公共 API 没被改坏。
