const config = window.SITE_CONFIG;
const dialog = document.querySelector('#wechat-dialog');
const toast = document.querySelector('#toast');
let toastTimer;

function notify(message) {
  if (dialog.open) {
    document.querySelector('#wechat-note').textContent = message;
    return;
  }
  toast.textContent = message;
  toast.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3000);
}

async function copyText(value) {
  try {
    await navigator.clipboard.writeText(value);
    notify('已复制：' + value);
  } catch {
    notify('请长按或选中复制：' + value);
  }
}

document.querySelector('#year').textContent = new Date().getFullYear();
for (const platform of ['bilibili', 'xiaohongshu']) {
  const url = config[platform + 'Url'];
  if (!url) continue;
  for (const link of document.querySelectorAll(`[data-platform="${platform}"]`)) {
    link.href = url;
    if (link.classList.contains('platform-link')) link.textContent = '前往 B 站主页 ↗';
  }
  document.querySelector(`[data-platform-label="${platform}"]`).textContent = '关注「' + config.accountName + '」';
}

for (const [name, selector] of [['jdShopUrl', '#jd-shop'], ['xiaohongshuShopUrl', '#xiaohongshu-shop']]) {
  if (!config[name]) continue;
  const link = document.querySelector(selector);
  link.href = config[name];
  link.hidden = false;
}
if (config.jdShopUrl || config.xiaohongshuShopUrl) {
  document.querySelector('#shop-status').hidden = true;
}

document.querySelector('[data-open-wechat]').addEventListener('click', () => dialog.showModal());
document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  const bounds = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
});

if (config.wechatId) {
  const button = document.querySelector('#copy-wechat');
  button.hidden = false;
  button.textContent = '复制微信号：' + config.wechatId;
  button.addEventListener('click', () => copyText(config.wechatId));
  document.querySelector('#wechat-note').textContent = '添加时请备注「魔方群论」。';
  document.querySelector('#qr-area').hidden = true;
}

if (config.wechatQrImage) {
  const area = document.querySelector('#qr-area');
  const image = document.createElement('img');
  image.alt = '德森的微信联系二维码，可使用微信扫码添加';
  image.className = 'wechat-qr';
  image.addEventListener('error', () => {
    area.replaceChildren();
    area.textContent = '二维码暂时无法加载，请通过下方微信号或社交账号联系。';
  });
  image.src = config.wechatQrImage;
  area.replaceChildren(image);
  area.hidden = false;
  document.querySelector('#wechat-note').textContent = '微信扫码添加；手机上可保存图片后在微信中识别。';
}
