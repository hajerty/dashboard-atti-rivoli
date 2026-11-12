// Testo della pagina per l'artifact di prova (limite 262.144 byte):
// riga <meta name="dash-one-writer"> + src/pagina.html con script e stili minificati.
// Uso: node strumenti/minifica.mjs src/pagina.html > pagina_artifact.html
import { readFileSync } from 'node:fs';
import { minify } from 'terser';
import { minify as cssMin } from 'csso';
const src = readFileSync(process.argv[2], 'utf8');
const parti = []; let i = 0;
const re = /<(script|style)(\s[^>]*)?>([\s\S]*?)<\/\1>/g; let m;
while ((m = re.exec(src))) {
  parti.push(src.slice(i, m.index));
  const [tutto, tag, attr = '', corpo] = m;
  if (tag === 'style') parti.push(`<style${attr}>${cssMin(corpo).css}</style>`);
  else if (/\bsrc=|type="(?!text\/javascript)/.test(attr) || !corpo.trim()) parti.push(tutto);
  else {
    const r = await minify(corpo, { compress: { passes: 2 }, mangle: true, format: { inline_script: true, comments: false } });
    parti.push(`<script${attr}>${r.code}</script>`);
  }
  i = m.index + tutto.length;
}
parti.push(src.slice(i));
const out = '<meta name="dash-one-writer">\n' + parti.join('').replace(/\n{2,}/g, '\n');
process.stdout.write(out);
process.stderr.write(`byte: ${Buffer.byteLength(src)} -> ${Buffer.byteLength(out)}\n`);
