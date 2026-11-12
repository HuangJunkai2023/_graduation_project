const path = require('path');
const fs = require('fs');
const runtime = 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1105-1297-0_26.1105.1297.0_x64__3k8sg7r9htsxt/dependencies';
const root = path.resolve(__dirname, '../../../..');
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, 'project/qa_system/runtime/tooling/browser-cache');
const { chromium } = require(path.join(runtime, 'node/node_modules/playwright'));
let activeBrowser;

async function main() {
  const recording = process.argv.includes('--record');
  const output = path.resolve(__dirname, '..', recording ? 'recording' : 'assets');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  });
  activeBrowser = browser;
  const options = { viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 };
  if (recording) options.recordVideo = { dir: output, size: { width: 1280, height: 720 } };
  const context = await browser.newContext(options);
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:8501', { waitUntil: 'domcontentloaded' });
  await page.getByRole('heading', { name: '接触网规范问答', exact: true }).waitFor();
  await page.getByLabel('检索方式', { exact: true }).waitFor();
  await page.screenshot({ path: path.join(output, 'system-overview.png') });
  console.log(await page.locator('body').innerText());
  console.log('CONTROLS', await page.locator('input,textarea,select,button').evaluateAll(
    controls => controls.map(control => ({ tag: control.tagName, label: control.getAttribute('aria-label'),
      placeholder: control.getAttribute('placeholder'), text: control.innerText }))));
  if (recording) {
    const start = Date.now();
    const events = [];
    async function holdUntil(seconds) {
      const remaining = seconds * 1000 - (Date.now() - start);
      if (remaining > 0) await page.waitForTimeout(remaining);
    }
    async function capture(name) {
      await page.screenshot({ path: path.join(output, name + '.png') });
      events.push({ name, seconds: (Date.now() - start) / 1000 });
    }
    await holdUntil(10);
    await page.getByRole('tab', { name: '知识库', exact: true }).click();
    await page.getByText('当前模型向量', { exact: true }).waitFor();
    await capture('knowledge-base');
    await holdUntil(35);
    await page.getByRole('tab', { name: '规范问答', exact: true }).click();
    await page.getByLabel('检索方式', { exact: true }).click();
    await page.getByRole('option', { name: '混合检索', exact: true }).click();
    await page.getByLabel('使用 DeepSeek 生成答案', { exact: true }).check({ force: true });
    await holdUntil(55);
    const input = page.getByPlaceholder('输入标准号、年份或具体问题', { exact: true });
    await input.fill('TB/T 2073-2020 对铸件的外观和表面质量有哪些要求？');
    await input.press('Enter');
    await page.getByText(/状态：answered/).waitFor({ timeout: 90000 });
    await capture('answer-with-citations');
    await holdUntil(85);
    const source = page.locator('details').first();
    await source.locator('summary').click();
    await source.getByRole('button', { name: '查看 PDF 原文页' }).click();
    await page.locator('[data-testid="stImage"] img').first().waitFor();
    await page.locator('[data-testid="stImage"] img').first().scrollIntoViewIfNeeded();
    await capture('original-source-page');
    await holdUntil(120);
    await input.fill('那2010年版呢？');
    await input.press('Enter');
    await page.getByText(/状态：missing_edition/).waitFor({ timeout: 30000 });
    await capture('missing-edition');
    await holdUntil(150);
    await page.getByRole('button', { name: '清空本次对话', exact: true }).click();
    await input.fill('请告诉我今天纽约的天气。');
    await input.press('Enter');
    await page.getByText(/状态：insufficient_evidence/).waitFor({ timeout: 90000 });
    await capture('insufficient-evidence');
    await holdUntil(180);
    await page.getByRole('tab', { name: '知识库', exact: true }).click();
    await page.getByText('当前模型向量', { exact: true }).waitFor();
    await capture('corpus-and-source-management');
    await holdUntil(210);
    fs.writeFileSync(path.join(output, 'recording-events.json'), JSON.stringify(events, null, 2));
    const video = page.video();
    await context.close();
    await video.saveAs(path.join(output, 'OCS_Demo_Raw.webm'));
    await browser.close();
    return;
  }
  await context.close();
  await browser.close();
}

main().catch(async error => {
  console.error(error);
  if (activeBrowser) await activeBrowser.close();
  process.exitCode = 1;
});
