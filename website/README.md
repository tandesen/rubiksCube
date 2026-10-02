# Math Cuber · 魔方与群论

用于魔方包装扫码后的个人课程介绍页。暂用 Math Cuber 作为站名；没有注册域名，也没有上传到公网。

## 本地运行

在 Finder 中双击 `start.command`，然后打开 <http://127.0.0.1:4173>。
需要 Python 3；当前开发电脑已经安装。如果预览已经运行，不要重复启动。

也可以在项目根目录运行：

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory website/dist
```

这是静态网站，没有 npm 安装或构建步骤，不需要数据库。服务器只公开 `dist/` 中的文件，不公开课程源码。所有图片、样式和脚本都随站点保存，不依赖第三方 CDN 或在线字体。

## 网站内容

- 首页：使用用户提供的 TS 标志与按实物配色绘制的字母编号魔方插画，白色、留白、蓝色强调；「购买课程同款魔方」直达商品卡片并高亮。
- 课程：已制作的前三集介绍，点击卡片可展开；后续主题单独预告。
- 个人介绍：德森大老爷的 B 站与小红书主页直达入口，以及课程配套魔方的店铺入口。
- 学习交流：微信弹窗，支持联系二维码与复制微信号。
- 手机布局、键盘焦点、Escape 关闭弹窗、减少动态效果偏好。

首页与商品卡片使用同一张矢量示意图 `dist/assets/cube-lettered.svg`，按现有实物的蓝顶、黄正、红侧显示字母，不显示数字角标。它不是商品实拍；确定正式照片后可替换图片与相应 alt 文本。

## 更换你的链接与微信二维码

编辑 `dist/config.js`：

```js
window.SITE_CONFIG = {
  accountName: '德森大老爷',
  bilibiliUrl: 'https://space.bilibili.com/698815643',
  xiaohongshuUrl: 'https://www.xiaohongshu.com/user/profile/5fed670f0000000001003c66',
  jdShopUrl: '',
  xiaohongshuShopUrl: '',
  wechatId: '',
  wechatQrImage: 'assets/wechat-contact.png',
};
```

1. 把 B 站、小红书的完整 HTTPS 主页链接填入对应字段。已配置用户提供的主页地址并去掉查询参数，平台可能要求登录。
2. 把要公开的微信联系二维码存到 `dist/assets/wechat-contact.png`，将 `wechatQrImage` 填成 `assets/wechat-contact.png`。
3. 填入 `wechatId` 后显示复制按钮。只填微信号也可以使用；空值不显示按钮。当前已配置个人微信二维码；未提供微信号，因此不显示复制按钮。
4. 刷新网页即可看到更新。账号名也出现在 `index.html` 中，改名时同步修改两处。

京东和小红书店铺未上线时，`jdShopUrl`、`xiaohongshuShopUrl` 保持空值；网站显示“京东 / 小红书购买渠道即将开放”，不会出现无法购买的空按钮。商品页面发布并确认手机端可打开后，将完整的 HTTPS 商品链接分别填入这两个字段，购买按钮会自动出现。只有一款魔方时，优先填**商品详情页**，顾客少走一步；有多款商品时可以改填店铺首页。小红书的账号主页链接与商品购买链接是两回事，不要将账号主页当作购买入口。

当前商品卡使用与首页相同的字母魔方插画，仅作为课程视觉示意；可在 `index.html` 中将该卡的 `assets/cube-lettered.svg` 改为实拍图，并同步修改图片描述。京东/小红书首图建议拍魔方与包装盒的实物组合，用干净浅色背景、均匀光线，让字母编号可以清楚辨认。接下来的图依次展示六面编号细节、包装及盒内物、实测尺寸与手持比例、课程场景。商品参数、材质和随盒内容按最终实物填写；包装盒和魔方已经到货时，实拍比设计效果图更能让买家判断产品。

课程链接现在统一导向已配置的 B 站主页。拿到三节视频的正式链接后，可在 `index.html` 中分别替换 `.platform-link` 的地址，并移除这些链接的 `data-platform` 属性，避免被主页配置覆盖。

## 包装上的二维码建议

包装印一个固定网址的二维码和可读域名，配文可以是「扫码看课程 · 加入学习交流」。二维码指向你自己持有并续费的域名首页。

推荐路径：包装 → 网站 → 课程 / 个人账号 / 微信联系码 → 邀请入群。微信联系码与微信号搭配使用，可通过个人联系确认后邀请进群。想直接放群二维码也可以，但需要关注二维码本身的有效期、入群限制和满群情况，并及时更新网页。第一版按个人联系码设计。

域名注册完成、网站正式上线并实际扫码通过之后，再生成用于印刷的二维码。不要将 localhost 或临时预览地址印在包装上。

## 域名候选（仅命名建议，未确认可注册）

1. `mathcuber.com`：首选。保留 Math Cuber 的方向，省去连字符，适合这套魔方课程。
2. `mathcuber.cn`：如果主要面向中文观众，可以考虑；注册及续费报价以注册商为准。
3. `desenmath.com`：突出德森个人品牌，未来讲其他数学主题也适用。

`math-cuber.com` 可以用，但口头表达时多一个连字符。品牌名 Math Cuber 与网址不必完全一致。搜索不到网站不代表域名可注册；应在阿里云等注册商处实时查询注册状态与续费价格。本次没有购买或注册任何域名。

## 后续部署到阿里云

上传 `dist/` **里面的文件和 assets 文件夹**到 Nginx 的网站目录即可。Nginx 的首页设为 `index.html`。不需要在服务器上运行 Node 或这个 Python 预览服务。

实际顺序：确定并注册域名 → 选择服务器地区 → 完成适用的备案流程 → 上传网站 → 配置 DNS 与 HTTPS → 手机微信扫码验证 → 制作包装二维码。

使用中国内地服务器需要按阿里云接入要求完成 ICP 备案，获得备案号后按要求添加网站底部信息；香港或境外地域的备案要求不同。选定服务后以官方当时的规则为准：

- [阿里云：备案服务器检查](https://help.aliyun.com/zh/icp-filing/basic-icp-service/user-guide/icp-filing-server-access-information-check)
- [阿里云：备案与域名常见问题](https://help.aliyun.com/zh/icp-filing/basic-icp-service/support/for-the-record-domain-faq)

## 文件结构

```text
website/
  start.command         本地启动
  README.md             本说明
  dist/
    index.html          内容与结构
    styles.css          样式与响应式布局
    config.js           个人主页与微信资料
    app.js              微信弹窗、链接配置、复制操作
    assets/             包装原版矢量图与平台图标
```

魔方与平台图标来自项目 `output/pdf/packaging_v3/`。TS 标志和个人微信二维码使用用户在 2026-09-20 提供的 PNG 原文件，未重绘或重新编码；二维码外围使用 CSS 添加白色留边以便识别。网站英文名称使用 `3×3 CUBE & GROUP THEORY`。本次修改仅限 `website/`。
