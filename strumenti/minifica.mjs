// Testo della pagina per l'artifact di prova.
// Uso: node strumenti/minifica.mjs src/pagina.html CARTELLA_USCITA
// Scrive CARTELLA/index.html (riga <meta name="dash-one-writer"> + HTML e stili minificati, con un
// <script src="rv-app.js"> al posto degli script) e CARTELLA/rv-app.js (tutti gli script, minificati,
// nello stesso ordine). Nell'artifact vanno in files/index.html e files/rv-app.js (ciascuno ≤ 256 KB).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { minify } from 'terser';
import { minify as cssMin } from 'csso';
const [src, out] = process.argv.slice(2);
const html = readFileSync(src, 'utf8');
const parti = [], js = []; let i = 0, messo = false;
const re = /<(script|style)(\s[^>]*)?>([\s\S]*?)<\/\1>/g; let m;
while ((m = re.exec(html))) {
  parti.push(html.slice(i, m.index));
  const [tutto, tag, attr = '', corpo] = m;
  if (tag === 'style') parti.push(`<style${attr}>${cssMin(corpo).css}</style>`);
  else if (/\bsrc=|type="(?!text\/javascript)/.test(attr) || !corpo.trim()) parti.push(tutto);
  else {
    const r = await minify(corpo, { compress: { passes: 2 }, mangle: true, format: { comments: false } });
    js.push(r.code.replace(/;?$/, ';'));
    if (!messo) { parti.push('<script src="rv-app.js"></script>'); messo = true; }
  }
  i = m.index + tutto.length;
}
parti.push(html.slice(i));
const pagina = '<meta name="dash-one-writer">\n' + parti.join('').replace(/\n{2,}/g, '\n');
mkdirSync(out, { recursive: true });
writeFileSync(out + '/index.html', pagina); writeFileSync(out + '/rv-app.js', js.join('\n'));
process.stderr.write(`index.html ${Buffer.byteLength(pagina)} byte, rv-app.js ${Buffer.byteLength(js.join('\n'))} byte\n`);
