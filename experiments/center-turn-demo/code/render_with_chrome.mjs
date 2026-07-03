import { spawn } from 'node:child_process';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import os from 'node:os';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../../..');
const experiment = path.resolve(root, 'experiments/center-turn-demo');
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const width = 1280;
const height = 720;
const fps = 24;
const seconds = 7.5;
const frameCount = Math.round(fps * seconds);

const route = process.argv[2] || 'both';
const routes = route === 'both' ? ['route_a', 'route_d'] : [route];
const routeConfigs = {
  route_a: {
    html: 'route_a_css3d.html',
    frameDir: 'route_a_css3d',
    output: 'route_a_css3d_center_turns.mp4',
    deterministic: true
  },
  route_a_course: {
    html: 'route_a_css3d.html',
    query: '?theme=course&captions=0',
    frameDir: 'route_a_course_theme',
    output: 'route_a_course_theme_center_turns.mp4',
    deterministic: true
  },
  route_a_transparent: {
    html: 'route_a_css3d.html',
    query: '?theme=transparent&captions=0',
    maskQuery: '?theme=mask&captions=0',
    frameDir: 'route_a_transparent',
    output: 'route_a_transparent_center_turns.mov',
    deterministic: true,
    alpha: true
  },
  route_d: {
    html: 'route_d_iamthecube_api.html',
    frameDir: 'route_d_iamthecube_api',
    output: 'route_d_iamthecube_api_center_turns.mp4',
    deterministic: false,
    readyExpression: 'window.__demoReady === true'
  }
};

if (!existsSync(chromePath)) {
  throw new Error(`Chrome not found at ${chromePath}`);
}

for (const item of routes) {
  if (!routeConfigs[item]) {
    throw new Error(`Unknown route: ${item}`);
  }
}

const port = 9300 + Math.floor(Math.random() * 500);
const userDataDir = path.join(os.tmpdir(), `center-turn-demo-${Date.now()}`);
const chrome = spawn(chromePath, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${userDataDir}`,
  `--window-size=${width},${height}`,
  'about:blank'
], { stdio: ['ignore', 'pipe', 'pipe'] });

chrome.stderr.on('data', (chunk) => {
  const text = String(chunk);
  if (!text.includes('DevTools listening')) process.stderr.write(text);
});

try {
  const wsUrl = await waitForWebSocketUrl(port);
  const cdp = await connectCDP(wsUrl);
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');

  for (const item of routes) {
    if (routeConfigs[item].deterministic) {
      await renderDeterministicRoute(cdp, item, routeConfigs[item]);
    } else {
      await renderLiveRoute(cdp, item, routeConfigs[item]);
    }
  }
} finally {
  chrome.kill('SIGTERM');
  await waitForProcessExit(chrome);
  await rm(userDataDir, { recursive: true, force: true }).catch(() => {});
}

async function renderDeterministicRoute(cdp, name, config) {
  const frameDir = path.join(experiment, `frames/${config.frameDir}`);
  await resetDir(frameDir);
  const maskFrameDir = config.alpha ? path.join(experiment, `frames/${config.frameDir}_mask`) : null;
  if (maskFrameDir) await resetDir(maskFrameDir);

  const pageUrl = pathToFileURL(path.join(__dirname, config.html)).href + (config.query || '');
  await setTransparentBackground(cdp, false);
  await navigate(cdp, pageUrl);
  if (config.readyExpression) await waitForExpression(cdp, config.readyExpression);

  for (let frame = 0; frame < frameCount; frame += 1) {
    await cdp.send('Runtime.evaluate', {
      expression: `window.setFrame(${frame}, ${fps})`,
      awaitPromise: true
    });
    await captureFrame(cdp, frameDir, frame);
    progress(name, frame);
  }

  if (config.alpha) {
    const maskUrl = pathToFileURL(path.join(__dirname, config.html)).href + config.maskQuery;
    await navigate(cdp, maskUrl);
    for (let frame = 0; frame < frameCount; frame += 1) {
      await cdp.send('Runtime.evaluate', {
        expression: `window.setFrame(${frame}, ${fps})`,
        awaitPromise: true
      });
      await captureFrame(cdp, maskFrameDir, frame);
      progress(`${name}_mask`, frame);
    }
  }

  await encodeVideo(frameDir, path.join(experiment, `videos/${config.output}`), Boolean(config.alpha), maskFrameDir);
}

async function renderLiveRoute(cdp, name, config) {
  const frameDir = path.join(experiment, `frames/${config.frameDir}`);
  await resetDir(frameDir);

  const pageUrl = pathToFileURL(path.join(__dirname, config.html)).href;
  await setTransparentBackground(cdp, Boolean(config.alpha));
  await navigate(cdp, pageUrl);
  await waitForExpression(cdp, config.readyExpression);
  await cdp.send('Runtime.evaluate', {
    expression: 'window.startDemo()',
    awaitPromise: true
  });

  const started = Date.now();
  for (let frame = 0; frame < frameCount; frame += 1) {
    const target = started + (frame * 1000 / fps);
    const delay = target - Date.now();
    if (delay > 0) await sleep(delay);
    await captureFrame(cdp, frameDir, frame, Boolean(config.alpha));
    progress(name, frame);
  }

  await encodeVideo(frameDir, path.join(experiment, `videos/${config.output}`), Boolean(config.alpha));
}

async function captureFrame(cdp, frameDir, frame, alpha = false) {
  const result = await cdp.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: false,
    omitBackground: alpha
  });
  const file = path.join(frameDir, `${String(frame + 1).padStart(4, '0')}.png`);
  await writeFile(file, Buffer.from(result.data, 'base64'));
}

async function encodeVideo(frameDir, outPath, alpha = false, maskFrameDir = null) {
  await mkdir(path.dirname(outPath), { recursive: true });
  const common = [
    '-hide_banner',
    '-y',
    '-framerate', String(fps),
    '-i', path.join(frameDir, '%04d.png')
  ];
  const args = alpha
    ? [
        ...common,
        '-framerate', String(fps),
        '-i', path.join(maskFrameDir, '%04d.png'),
        '-filter_complex', '[1:v]format=gray[alpha];[0:v][alpha]alphamerge,format=yuva444p10le',
        '-c:v', 'prores_ks',
        '-profile:v', '4',
        '-pix_fmt', 'yuva444p10le',
        outPath
      ]
    : [
        ...common,
        '-vf', 'format=yuv420p',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        outPath
      ];
  await run('ffmpeg', args);
}

async function resetDir(dir) {
  await rm(dir, { recursive: true, force: true });
  await mkdir(dir, { recursive: true });
}

async function navigate(cdp, url) {
  const loaded = cdp.waitFor('Page.loadEventFired');
  await cdp.send('Page.navigate', { url });
  await loaded;
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: false
  });
}

async function setTransparentBackground(cdp, enabled) {
  if (enabled) {
    await cdp.send('Emulation.setDefaultBackgroundColorOverride', {
      color: { r: 0, g: 0, b: 0, a: 0 }
    });
  } else {
    await cdp.send('Emulation.setDefaultBackgroundColorOverride');
  }
}

async function waitForExpression(cdp, expression) {
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    const result = await cdp.send('Runtime.evaluate', {
      expression,
      returnByValue: true
    });
    if (result.result?.value === true) return;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${expression}`);
}

async function waitForWebSocketUrl(portNumber) {
  const versionEndpoint = `http://127.0.0.1:${portNumber}/json/version`;
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(versionEndpoint);
      if (response.ok) {
        const target = await createPageTarget(portNumber);
        return target.webSocketDebuggerUrl;
      }
    } catch {
      // Chrome is still starting.
    }
    await sleep(100);
  }
  throw new Error('Timed out waiting for Chrome DevTools endpoint');
}

async function createPageTarget(portNumber) {
  const newEndpoint = `http://127.0.0.1:${portNumber}/json/new?about:blank`;
  const response = await fetch(newEndpoint, { method: 'PUT' });
  if (response.ok) return response.json();

  const listResponse = await fetch(`http://127.0.0.1:${portNumber}/json/list`);
  if (!listResponse.ok) {
    throw new Error(`Unable to create or list Chrome targets on port ${portNumber}`);
  }
  const pages = await listResponse.json();
  const page = pages.find((target) => target.type === 'page' && target.webSocketDebuggerUrl);
  if (!page) throw new Error('Chrome did not expose a page target');
  return page;
}

function connectCDP(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const events = new Map();

  ws.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result || {});
      return;
    }

    const waiters = events.get(message.method);
    if (waiters?.length) {
      const resolve = waiters.shift();
      resolve(message.params || {});
    }
  });

  return new Promise((resolve, reject) => {
    ws.addEventListener('open', () => {
      resolve({
        send(method, params = {}) {
          const requestId = ++id;
          ws.send(JSON.stringify({ id: requestId, method, params }));
          return new Promise((innerResolve, innerReject) => {
            pending.set(requestId, { resolve: innerResolve, reject: innerReject });
          });
        },
        waitFor(method) {
          return new Promise((innerResolve) => {
            if (!events.has(method)) events.set(method, []);
            events.get(method).push(innerResolve);
          });
        }
      });
    });
    ws.addEventListener('error', reject);
  });
}

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: 'inherit' });
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} exited with ${code}`));
    });
  });
}

function waitForProcessExit(child) {
  if (child.exitCode !== null || child.signalCode !== null) return Promise.resolve();
  return Promise.race([
    new Promise((resolve) => child.once('exit', resolve)),
    sleep(1500)
  ]);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function progress(name, frame) {
  if (frame === 0 || frame === frameCount - 1 || frame % 24 === 23) {
    console.log(`${name}: ${frame + 1}/${frameCount}`);
  }
}
