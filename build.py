import csv, json, re
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def rows(p):
    r = list(csv.DictReader(open('data/' + p, encoding='utf-8-sig')))
    return [{k: (v if v != '' else None) for k, v in x.items()} for x in r]
NOMI = ['atti', 'programma', 'prossimamente', 'catene', 'catene_atti', 'mozioni_seguiti', 'procedure', 'affidamenti', 'mozioni',
        'lavori', 'lavori_in_arrivo', 'mappa_osm', 'mappa_confine', 'avvisi_lavori', 'ordinanze_viabilita', 'tempi_gare', 'calendario']
data = {n: rows(n + '.csv') for n in NOMI}
j = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
d3 = open('src/d3.min.js', encoding='utf-8').read().replace('</script', '<\\/script')
page = open('src/pagina.html', encoding='utf-8').read()
page = page.replace('<li>È una fotografia: non si aggiorna da sola.', '<li>Questa è una copia statica e autonoma della dashboard: i dati sono incorporati nel file e funziona anche senza connessione. Aggiornata al ' + open('data/aggiornato_al.txt', encoding='utf-8').read().strip() + '.</li>\n      <li>È una fotografia: non si aggiorna da sola.', 1)
assert 'copia statica' in page
css = """
:root{color-scheme:light dark;
--color-fg:#1f1e1d;--color-fg-muted:#6b6862;--color-bg:#ffffff;--color-panel:#f6f5f2;--color-border-line:#e2e0da;
--color-ok:#2e7d54;--color-warn:#b7791f;--color-bad:#c0392b;
--cds-chart-muted:#b9b6ae;--cds-chart-grid:#e6e4de;--cds-chart-axis:#cfccc4;--cds-text-secondary:#6b6862;
--cds-surface-popover:#ffffff;--cds-border:#d6d3cc;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.14);
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:12px;--cds-gap-lg:16px;--cds-gap-xl:28px;
--cds-pad-sm:6px;--cds-pad-md:10px;--cds-pad-lg:14px;--cds-radius:8px;
--cds-font-size-caption:12px;--cds-font-size-body:14px;--cds-font-size-heading:18px;--cds-font-size-title:28px;--cds-font-weight-medium:600;
--font-anthropic-sans:system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;--font-anthropic-serif:Georgia,'Times New Roman',serif;
--series-0:#2f6fdb;--series-1:#d9822b;--series-2:#3a9d6a;--series-3:#8a5cc2;--series-4:#c2477a;--series-5:#6b7280}
@media (prefers-color-scheme:dark){:root{
--color-fg:#ecebe8;--color-fg-muted:#a3a09a;--color-bg:#1b1a19;--color-panel:#252422;--color-border-line:#3a3835;
--color-ok:#5bc08a;--color-warn:#e0a84a;--color-bad:#ef6b5c;
--cds-chart-muted:#6a6761;--cds-chart-grid:#33312e;--cds-chart-axis:#4a4844;--cds-text-secondary:#a3a09a;
--cds-surface-popover:#2b2a28;--cds-border:#4a4844;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.5);
--series-0:#6ea0ff;--series-1:#f0a35a;--series-2:#6cc596;--series-3:#b48ae6;--series-4:#e57aa6;--series-5:#9aa1ac}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:var(--cds-font-size-body);line-height:1.4}
#dash-root{padding:var(--cds-gap-xl) var(--cds-gap-lg);max-width:1160px;margin:0 auto}
.dash-select{font:inherit;font-size:var(--cds-font-size-body);color:var(--color-fg);background-color:var(--color-bg);border:1px solid var(--color-border-line);border-radius:var(--cds-radius);padding:6px 28px 6px 10px;appearance:auto}
button{font-family:inherit}
@media print{.rv-nav,.rv-hbtns{display:none}.rv-page[hidden]{display:flex!important}}
"""
shim = r"""
window.dash=(function(){
  const src=window.__DATA, calcs={}, draws={}, cache={};
  const api={
    colors:[0,1,2,3,4,5].map(i=>'var(--series-'+i+')'),
    calc(id,s){calcs[id]=s;},
    loader(){},
    data(id){
      if(src[id]) return {status:'ok',data:src[id]};
      if(calcs[id]){
        if(!(id in cache)){ cache[id]=calcs[id].fn(...calcs[id].inputs.map(i=>api.data(i).data)); }
        return {status:'ok',data:cache[id]};
      }
      return {status:'missing',data:[]};
    },
    draw(n,fn){
      if(fn){draws[n]=fn;return;}
      const f=draws[n]; if(!f) return;
      document.querySelectorAll('[data-draw="'+n+'"]').forEach(el=>{
        if(el.closest('[hidden]')) return;
        try{ f(el); }catch(e){ console.error('draw '+n+': '+e.message); }
      });
    },
    onData(fn){fn();}, refresh(){}, params(){return {};}, setParams(){}, resetParams(){},
    setLink(n){ try{ history.replaceState(null,'','#'+n); }catch(e){} },
    _all(){ for(const n in draws) api.draw(n); }
  };
  return api;
})();
function startDash(){
  dash._all();
  let w=document.getElementById('dash-root').clientWidth, t=null;
  const redraw=()=>{ clearTimeout(t); t=setTimeout(()=>dash._all(),120); };
  new ResizeObserver(()=>{ const nw=document.getElementById('dash-root').clientWidth; if(nw!==w){ w=nw; redraw(); } }).observe(document.getElementById('dash-root'));
  document.addEventListener('click',e=>{ if(e.target.closest('.rv-tab, .rv-hbtn, .rv-story-go, [data-subt], .rv-nav-tog')) setTimeout(()=>dash._all(),0); });
  new MutationObserver(ms=>{ if(ms.some(m=>m.target.matches&&m.target.matches('.rv-page,[data-sub]')&&!m.target.hidden)) redraw(); }).observe(document.getElementById('dash-root'),{subtree:true,attributes:true,attributeFilter:['hidden']});
  window.addEventListener('hashchange',()=>setTimeout(()=>dash._all(),0));
}
"""
html = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A che punto siamo · Comune di Rivoli</title>
<style>{css}</style>
<script>{d3}</script>
<script>window.__DATA={j};</script>
<script>{shim}</script>
</head>
<body>
<div id="dash-root">
{page}
</div>
<script>startDash();</script>
</body>
</html>
"""
open('index.html', 'w', encoding='utf-8').write(html)
print(len(html))
