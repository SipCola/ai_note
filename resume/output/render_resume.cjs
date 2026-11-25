const { readFile, writeFile } = require('node:fs/promises');
const { homedir } = require('node:os');
const { extname, join, resolve } = require('node:path');

const bundledModules = join(homedir(), '.cache', 'codex-runtimes',
  'codex-primary-runtime', 'dependencies', 'node', 'node_modules');

function loadPackage(name) {
  if (process.env.RESUME_NODE_MODULES) {
    return require(join(resolve(process.env.RESUME_NODE_MODULES), name));
  }
  let entry;
  try {
    entry = require.resolve(name);
  } catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
    return require(join(bundledModules, name));
  }
  return require(entry);
}

const diagramDefaults = `
  graph [bgcolor=transparent, pad=0.12, nodesep=0.36, ranksep=0.44];
  node [shape=box, style="rounded,filled", color="#bba798", fillcolor="#fbf5ed",
    fontname="Microsoft YaHei", fontcolor="#392e29", fontsize=14, margin="0.17,0.08"];
  edge [color="#527265", fontcolor="#405c50", fontname="Microsoft YaHei",
    fontsize=12, arrowsize=0.65];
`;

const styles = `
  @page { size: A4; margin: 13mm 14mm; }
  body { margin: 0; background: #fff; color: #302820; font: 10.3pt/1.48
    "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }
  main { max-width: 182mm; margin: 0 auto; }
  h1, h2, h3, h4 { color: #653f30; line-height: 1.3; margin: 1.3em 0 .52em;
    break-after: avoid; }
  h1 { font-size: 25pt; margin-top: 0; }
  h2 { font-size: 16pt; padding-bottom: .19em; border-bottom: 1px solid #d8c8b9; }
  h3 { font-size: 13pt; }
  h4 { font-size: 11pt; }
  p, blockquote, ul, ol { margin: .45em 0 .65em; orphans: 2; widows: 2; }
  ul, ol { padding-left: 1.55em; }
  li { margin: .36em 0; break-inside: avoid; }
  blockquote { padding: .45em .75em; border-left: 2px solid #ac7961; background: #fbf5ed; }
  table { width: 100%; border-collapse: collapse; font-size: .94em; }
  th, td { border-bottom: 1px solid #d8c8b9; padding: .34em .5em; text-align: left; }
  th { background: #fbf5ed; }
  tr { break-inside: avoid; }
  a { color: #653f30; text-decoration-color: #bba798; }
  code { font-family: Consolas, monospace; overflow-wrap: anywhere; }
  figure { margin: .45em 0 .72em; break-inside: avoid; }
  figure svg { display: block; max-width: 100%; height: auto; margin: auto; }
  figure svg text { font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }
  figure svg .node text { font-size: 12px; }
  figure svg .edge text { font-size: 10px; paint-order: stroke; stroke: #fff;
    stroke-width: 2.5px; stroke-linejoin: round; }
  figure svg .node.focus path, figure svg .node.focus polygon { fill: #eed5c1; stroke: #a4674e; }
  figure svg .edge.upgrade path { stroke: #a6582e; }
  figure svg .edge.upgrade polygon { fill: #a6582e; stroke: #a6582e; }
  figure svg .edge.upgrade text { fill: #884621; }
  figure svg .edge.feedback path { stroke: #416e8f; }
  figure svg .edge.feedback polygon { fill: #416e8f; stroke: #416e8f; }
  figure svg .edge.feedback text { fill: #335a76; }
  @media screen { main { padding: 24px 18px; } }
  @media print { body { print-color-adjust: exact; } }
`;

async function renderResume() {
  const [source, htmlPath, pdfPath] = process.argv.slice(2);
  if (!source || !htmlPath || process.argv.length > 5 ||
      extname(source) !== '.md' || extname(htmlPath) !== '.html' ||
      (pdfPath && extname(pdfPath) !== '.pdf')) {
    throw new Error('用法：node render_resume.cjs 简历.md 简历.html [简历.pdf]');
  }

  const markdown = (await readFile(source, 'utf8')).replace(/^\uFEFF/, '');
  const { Marked } = loadPackage('marked');
  const viz = await loadPackage('@viz-js/viz').instance();
  const diagramNames = new Set();
  const parser = new Marked({
    renderer: {
      code({ lang, text }) {
        if (lang !== 'graphviz') return false;
        const declaration = /^digraph\s+(\w+)\s*\{/.exec(text);
        const name = declaration?.[1];
        if (!name || diagramNames.has(name)) {
          throw new Error(`流程图须使用唯一的 digraph 名称：${name ?? text.split('\n')[0]}`);
        }
        diagramNames.add(name);
        const diagram = declaration[0] + diagramDefaults + text.slice(declaration[0].length);
        const svg = viz.renderString(diagram, { format: 'svg' })
          .replace(/^[\s\S]*?(?=<svg\b)/, '')
          .replace(/\sid="([^"]+)"/g, ` id="${name}-$1"`);
        return `<figure id="${name}">${svg}</figure>\n`;
      },
    },
  });
  const body = parser.parse(markdown);
  if (diagramNames.size === 0) throw new Error('Markdown 缺少 graphviz 流程图。');

  const html = `<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 应用开发工程师简历</title>
<style>${styles}</style>
<main>${body}</main>
</html>\n`;
  await writeFile(htmlPath, html, 'utf8');

  if (pdfPath) {
    const { chromium } = loadPackage('playwright');
    const browser = await chromium.launch({ channel: 'msedge', headless: true });
    try {
      const page = await browser.newPage();
      await page.setContent(html);
      await page.evaluate(() => document.fonts.ready);
      await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true });
    } finally {
      await browser.close();
    }
  }
  console.log(`已渲染 ${diagramNames.size} 张流程图。`);
}

renderResume().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
