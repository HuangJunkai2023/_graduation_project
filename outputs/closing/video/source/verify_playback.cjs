const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const runtime = process.env.OCS_DEMO_RUNTIME;
const { chromium } = require(path.join(runtime, 'node/node_modules/playwright'));
const videoPath = path.resolve(process.argv[2]);
const outputPath = path.resolve(process.argv[3]);

async function main() {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  });
  try {
    const page = await browser.newPage();
    await page.route('http://demo.local/video.mp4', route => route.fulfill({
      contentType: 'video/mp4', body: fs.readFileSync(videoPath),
    }));
    await page.setContent('<video id="demo" muted playsinline src="http://demo.local/video.mp4"></video>');
    await page.evaluate(async () => {
      const video = document.getElementById('demo');
      video.playbackRate = 16;
      await video.play();
    });
    await page.waitForFunction(() => document.getElementById('demo').ended, { timeout: 45000 });
    const result = await page.evaluate(() => {
      const video = document.getElementById('demo');
      return { ended: video.ended, duration: video.duration, width: video.videoWidth,
        height: video.videoHeight, mediaError: video.error?.message ?? null, playbackRate: 16 };
    });
    result.video_sha256 = crypto.createHash('sha256').update(fs.readFileSync(videoPath)).digest('hex');
    result.checked_at = new Date().toISOString();
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + '\n');
    if (!result.ended || result.mediaError) throw new Error('Video did not play to completion');
    console.log(JSON.stringify(result));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
