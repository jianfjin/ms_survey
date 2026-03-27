"""HTML template renderer for single-file static dashboard."""

from __future__ import annotations

import json
from typing import Any


def render_dashboard_html(*, encoded_payload: str, export_report: dict[str, Any]) -> str:
    """Render full static dashboard HTML."""
    report_json = json.dumps(export_report, ensure_ascii=False, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CANDLE NCDN Static Dashboard</title>
  <style>{build_css_tokens_and_layout()}</style>
</head>
<body>
  <main id="app-root" aria-live="polite"></main>
  <script>
window.__DATA_B64_GZ__ = "{encoded_payload}";
window.__EXPORT_REPORT__ = {report_json};
  </script>
  <script>{build_client_js()}</script>
</body>
</html>"""


def build_css_tokens_and_layout() -> str:
    """Return CSS used in exported dashboard."""
    return """
:root{--p:#3B82F6;--s:#60A5FA;--a:#F97316;--bg:#F8FAFC;--tx:#1E293B;--bd:#D5E1EE;--mut:#475569;--focus:0 0 0 3px rgba(59,130,246,.45)}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:var(--bg);color:var(--tx);font-family:"Fira Sans","Segoe UI",sans-serif;line-height:1.55}
#app-root{min-height:100vh}.shell{display:grid;grid-template-columns:280px 1fr;gap:16px;padding:16px}
.side,.card{background:#fff;border:1px solid var(--bd);border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.06)}
.side{padding:12px;position:sticky;top:10px;height:fit-content}.main{display:grid;gap:16px}.panel{padding:14px 16px}
.title{margin:0;font-size:1.15rem;font-weight:700}.sub{margin:4px 0 0;color:var(--mut);font-size:.9rem}.warn{margin-top:10px;padding:10px;border:1px solid #F9C89B;border-radius:8px;background:#FFF7EE;color:#7C2D12;font-size:.85rem}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;padding:14px 16px}.k{border:1px solid var(--bd);border-radius:8px;padding:10px;background:#FCFEFF}.k .l{color:var(--mut);font-size:.8rem}.k .v{font-weight:700;font-size:1.2rem}
.tabs{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 16px}.tab{border:1px solid var(--bd);border-radius:999px;padding:8px 12px;background:#F1F5F9;font-size:.85rem;font-weight:600;cursor:pointer}
.tab[aria-pressed=true]{background:#DBEAFE;border-color:var(--p)}.tab:hover{background:#E2E8F0}
label{display:block;margin-bottom:6px;color:var(--mut);font-size:.82rem;font-weight:600}
.checks{max-height:180px;overflow:auto;border:1px solid var(--bd);border-radius:8px;padding:8px}.checks label{display:flex;align-items:center;gap:8px;margin:0;padding:4px 0;color:var(--tx);font-size:.85rem;cursor:pointer}
button,select,input[type=checkbox]{font-family:inherit;min-height:44px}button,select{width:100%;border:1px solid var(--bd);border-radius:8px;padding:8px 10px;background:#fff;color:var(--tx)}
.empty{border:1px dashed var(--bd);border-radius:8px;padding:14px;color:var(--mut)}.small{color:var(--mut);font-size:.8rem}
.tbl{overflow:auto}.tbl table{width:100%;border-collapse:collapse}.tbl th,.tbl td{border:1px solid var(--bd);padding:8px;text-align:left;font-size:.84rem;vertical-align:top}.tbl th{background:#F1F5F9}
.heat{border-collapse:collapse;min-width:560px}.heat th,.heat td{border:1px solid var(--bd);padding:6px 8px;text-align:center;font-size:.8rem}.heat th{background:#F1F5F9}
.bars{display:grid;gap:8px}.br{display:grid;grid-template-columns:200px 1fr 60px;gap:8px;align-items:center}.bl{font-size:.82rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.bt{height:14px;background:#E2E8F0;border-radius:999px;overflow:hidden}.bf{height:14px;background:linear-gradient(90deg,var(--s),var(--p))}.bv{text-align:right;font-size:.8rem;font-family:"Fira Code","Consolas",monospace}
:focus-visible{outline:none;box-shadow:var(--focus)}
@media(max-width:1024px){.shell{grid-template-columns:1fr}.side{position:static}.kpis{grid-template-columns:repeat(2,minmax(120px,1fr))}.br{grid-template-columns:1fr}}
@media(max-width:600px){.kpis{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
"""


def build_client_js() -> str:
    """Return compact JS runtime for exported dashboard."""
    return """
(()=>{'use strict';
const APP={raw:null,filters:{countries:[],roles:[],sections:[],questionTypes:[],aggregateOnly:false},view:'heat'};
const VIEWS=[['heat','Section Heatmap'],['section','Section Summary'],['question','Question Analysis'],['compare','Country Comparison']];
const U=(a)=>Array.from(new Set((a||[]).filter(v=>v!==null&&v!==undefined&&String(v).trim()!==''))).sort();
const E=(t,c,tx)=>{const el=document.createElement(t);if(c)el.className=c;if(tx!==undefined)el.textContent=tx;return el};
const decode=()=>{if(!window.__DATA_B64_GZ__)throw new Error('Missing embedded payload');const rep=window.__EXPORT_REPORT__||{};if(String(rep.encoding||'').includes('gzip'))throw new Error('Unsupported encoding: '+rep.encoding);const b=atob(window.__DATA_B64_GZ__);const bytes=Uint8Array.from(b,ch=>ch.charCodeAt(0));return JSON.parse(new TextDecoder('utf-8').decode(bytes));};
const fAnswers=()=> (APP.raw.answers||[]).filter(r=>(
 (!APP.filters.countries.length||APP.filters.countries.includes(r.country_iso))&&
 (!APP.filters.roles.length||APP.filters.roles.includes(r.role))&&
 (!APP.filters.sections.length||APP.filters.sections.includes(r.section_id))&&
 (!APP.filters.questionTypes.length||APP.filters.questionTypes.includes(r.question_type))
));
const fItems=()=>{const s=new Set(fAnswers().map(r=>r.respondent_id+'|'+r.question_id));return (APP.raw.answer_items||[]).filter(r=>s.has(r.respondent_id+'|'+r.question_id));};
function applyFilters(rows){return (rows||[]).filter(r=>(
 (!APP.filters.countries.length||APP.filters.countries.includes(r.country_iso))&&
 (!APP.filters.roles.length||APP.filters.roles.includes(r.role))&&
 (!APP.filters.sections.length||APP.filters.sections.includes(r.section_id))&&
 (!APP.filters.questionTypes.length||APP.filters.questionTypes.includes(r.question_type))
));}
const heat=()=>{const m=new Map();for(const r of fAnswers()){const k=r.section_id+'|'+r.country_iso;if(!m.has(k))m.set(k,{section_id:r.section_id,country_iso:r.country_iso,t:0,a:0});const c=m.get(k);c.t++;if(r.answer_state==='answered')c.a++;}return [...m.values()].map(v=>({section_id:v.section_id,country_iso:v.country_iso,answered_pct:v.t?Math.round(v.a/v.t*10000)/100:0,answered_count:v.a,total_count:v.t})).sort((a,b)=>(a.section_id+a.country_iso).localeCompare(b.section_id+b.country_iso));};
function computeSectionHeatmap(){return heat();}
const sectionRows=()=>{const m=new Map();for(const r of fAnswers()){if(!m.has(r.question_id))m.set(r.question_id,{question_id:r.question_id,question_prompt:r.question_prompt,section_id:r.section_id,question_type:r.question_type,t:0,a:0,c:new Set()});const x=m.get(r.question_id);x.t++;if(r.answer_state==='answered'){x.a++;x.c.add(r.country_iso);}}return [...m.values()].map(v=>({question_id:v.question_id,question_prompt:v.question_prompt,section_id:v.section_id,question_type:v.question_type,countries_answered:v.c.size,country_iso_list:[...v.c].sort().join(', '),answered_pct:v.t?Math.round(v.a/v.t*10000)/100:0})).sort((a,b)=>a.question_id.localeCompare(b.question_id));};
const qDist=(qid)=>{const rows=fAnswers().filter(r=>r.question_id===qid&&r.answer_state==='answered');if(!rows.length)return[];const t=rows[0].question_type;const m=new Map();if(t==='multi_select'||t==='ranking'){for(const r of fItems().filter(x=>x.question_id===qid)){const k=r.country_iso+'|'+r.item_value;if(!m.has(k))m.set(k,{country_iso:r.country_iso,answer_value:r.item_value,s:new Set()});m.get(k).s.add(r.respondent_id);}}else{for(const r of rows){const v=String(r.answer_value_masked||'').trim();if(!v)continue;const k=r.country_iso+'|'+v;if(!m.has(k))m.set(k,{country_iso:r.country_iso,answer_value:v,s:new Set()});m.get(k).s.add(r.respondent_id);}}const tot=new Map();for(const r of rows){if(!tot.has(r.country_iso))tot.set(r.country_iso,new Set());tot.get(r.country_iso).add(r.respondent_id);}return [...m.values()].map(v=>{const c=v.s.size;const total=(tot.get(v.country_iso)||new Set()).size;return{country_iso:v.country_iso,answer_value:v.answer_value,respondent_count:c,percentage:total?Math.round(c/total*10000)/100:0};}).sort((a,b)=>a.country_iso===b.country_iso?b.respondent_count-a.respondent_count:a.country_iso.localeCompare(b.country_iso));};
function computeQuestionDistribution(questionId){return qDist(questionId);}
const deltas=(rows,n=10)=>{const m=new Map();for(const r of rows){if(!m.has(r.answer_value))m.set(r.answer_value,[]);m.get(r.answer_value).push(r);}const out=[];for(const [a,rs] of m){let min=1e9,max=-1e9,minc='',maxc='';for(const r of rs){if(r.percentage<min){min=r.percentage;minc=r.country_iso;}if(r.percentage>max){max=r.percentage;maxc=r.country_iso;}}out.push({answer_value:a,delta_pp:Math.round((max-min)*100)/100,max_country:maxc,min_country:minc});}return out.sort((a,b)=>b.delta_pp-a.delta_pp).slice(0,n);};
const themes=(qid)=>{if(APP.filters.aggregateOnly)return[];const stop=new Set(['the','and','for','that','with','from','this','there','have','your','what','which','will','into','their','they','are','was','were','not','but','can','has','had','all','any','our','you','about']);const re=/[a-zA-Z]{3,}/g;const c=new Map();for(const r of fAnswers().filter(x=>x.question_id===qid&&x.question_type==='text'&&x.answer_state==='answered')){for(const t of (String(r.answer_value_masked||'').toLowerCase().match(re)||[])){if(stop.has(t))continue;c.set(t,(c.get(t)||0)+1);}}return [...c.entries()].map(([theme,count])=>({theme,count})).sort((a,b)=>b.count-a.count).slice(0,12);};
const rTable=(c,rows,cols)=>{c.innerHTML='';if(!rows.length){c.appendChild(E('div','empty','No data for the current filters.'));return;}const w=E('div','tbl');const t=E('table');const th=E('thead');const tr=E('tr');for(const col of cols)tr.appendChild(E('th','',col.label));th.appendChild(tr);const tb=E('tbody');for(const row of rows){const r=E('tr');for(const col of cols)r.appendChild(E('td','',row[col.key]!=null?String(row[col.key]):''));tb.appendChild(r);}t.appendChild(th);t.appendChild(tb);w.appendChild(t);c.appendChild(w);};
const rBars=(c,rows,l,v)=>{c.innerHTML='';if(!rows.length){c.appendChild(E('div','empty','No data for chart.'));return;}const max=Math.max(...rows.map(r=>Number(r[v]||0)),0);const list=E('div','bars');for(const row of rows){const br=E('div','br');br.appendChild(E('div','bl',String(row[l])));const bt=E('div','bt');const bf=E('div','bf');bf.style.width=max?((Number(row[v])/max)*100).toFixed(2)+'%':'0%';bt.appendChild(bf);br.appendChild(bt);br.appendChild(E('div','bv',String(row[v])));list.appendChild(br);}c.appendChild(list);};
const rHeat=(c,rows)=>{c.innerHTML='';if(!rows.length){c.appendChild(E('div','empty','No heatmap data for selected filters.'));return;}const ss=U(rows.map(r=>r.section_id)),cs=U(rows.map(r=>r.country_iso));const g=new Map(rows.map(r=>[r.section_id+'|'+r.country_iso,r]));const w=E('div','tbl');const t=E('table','heat');const hd=E('thead');const hr=E('tr');hr.appendChild(E('th','','Section'));for(const cc of cs)hr.appendChild(E('th','',cc));hd.appendChild(hr);const bd=E('tbody');for(const s of ss){const tr=E('tr');tr.appendChild(E('th','',s));for(const cc of cs){const x=g.get(s+'|'+cc);const p=x?x.answered_pct:0;const td=E('td','',String(p));td.style.backgroundColor='hsl(210 75% '+(98-Math.round((p/100)*48))+'%)';td.title=s+' / '+cc+': '+p+'% answered';tr.appendChild(td);}bd.appendChild(tr);}t.appendChild(hd);t.appendChild(bd);w.appendChild(t);c.appendChild(w);};
const kpis=()=>{const r=APP.raw.respondents||[],a=fAnswers();return{respondents:r.length,countries:U(r.map(x=>x.country_iso)).length,questions:(APP.raw.questions||[]).length,answeredRows:a.filter(x=>x.answer_state==='answered').length};};
const side=()=>{const el=E('aside','side');el.appendChild(E('h2','title','Filters'));el.appendChild(E('p','sub','Refine analysis by country, role, section, and question type.'));
const cs=[['countries','Countries (ISO)',U((APP.raw.respondents||[]).map(r=>r.country_iso))],['roles','Roles',U((APP.raw.respondents||[]).map(r=>r.role))],['sections','Sections',U((APP.raw.questions||[]).map(r=>r.section_id))],['questionTypes','Question Types',U((APP.raw.questions||[]).map(r=>r.question_type))]];
for(const [k,l,vals] of cs){const g=E('div','');g.style.marginBottom='12px';g.appendChild(E('label','',l));const b=E('div','checks');for(const v of vals){const id='f-'+k+'-'+String(v).replace(/[^A-Za-z0-9_-]/g,'_');const line=document.createElement('label');line.setAttribute('for',id);const cb=document.createElement('input');cb.type='checkbox';cb.id=id;cb.checked=APP.filters[k].includes(v);cb.addEventListener('change',()=>{if(cb.checked){if(!APP.filters[k].includes(v))APP.filters[k].push(v);}else APP.filters[k]=APP.filters[k].filter(x=>x!==v);render();});line.appendChild(cb);line.appendChild(E('span','',v));b.appendChild(line);}g.appendChild(b);el.appendChild(g);}
const g=E('div','');g.style.marginBottom='12px';g.appendChild(E('label','','Privacy View'));const box=E('div','checks');const line=document.createElement('label');const cb=document.createElement('input');cb.type='checkbox';cb.checked=APP.filters.aggregateOnly;cb.addEventListener('change',()=>{APP.filters.aggregateOnly=cb.checked;render();});line.appendChild(cb);line.appendChild(E('span','','Aggregate-only view'));box.appendChild(line);g.appendChild(box);el.appendChild(g);
const rst=E('button','', 'Reset Filters');rst.addEventListener('click',()=>{APP.filters.countries=[];APP.filters.roles=[];APP.filters.sections=[];APP.filters.questionTypes=[];render();});el.appendChild(rst);
const rep=window.__EXPORT_REPORT__||{};const st=E('div','small','Encoded size: '+String(rep.size_bytes||0)+' bytes'+((rep.warnings||[]).length?' | Warning: '+rep.warnings.join('; '):''));st.style.marginTop='10px';el.appendChild(st);return el;};
const main=()=>{const m=E('section','main');const h=E('div','card panel');h.appendChild(E('h1','title','CANDLE NCDN Biomedical Data Dashboard'));h.appendChild(E('p','sub','Single-file offline analytics for national cancer data node planning.'));h.appendChild(E('div','warn','Data sensitivity notice: respondent-level normalized rows are embedded. Names/emails are excluded and open text is masked.'));m.appendChild(h);
const kc=E('div','card');const kg=E('div','kpis');const kk=kpis();for(const [l,v] of [['Respondents',kk.respondents],['Countries',kk.countries],['Questions',kk.questions],['Answered Rows',kk.answeredRows]]){const k=E('div','k');k.appendChild(E('div','l',l));k.appendChild(E('div','v',String(v)));kg.appendChild(k);}kc.appendChild(kg);m.appendChild(kc);
const tc=E('div','card');const tabs=E('div','tabs');for(const [id,lbl] of VIEWS){const b=E('button','tab',lbl);b.setAttribute('aria-pressed',APP.view===id?'true':'false');b.addEventListener('click',()=>{APP.view=id;render();});tabs.appendChild(b);}tc.appendChild(tabs);m.appendChild(tc);
const vc=E('div','card panel');rView(vc);m.appendChild(vc);return m;};
const rView=(c)=>{if(APP.view==='heat'){c.appendChild(E('h2','','Section Heatmap'));rHeat(c,heat());c.appendChild(E('p','small','Heatmap shows answered percentage by section and country ISO.'));return;}
if(APP.view==='section'){c.appendChild(E('h2','','Section Summary'));rTable(c,sectionRows(),[{key:'question_id',label:'Question ID'},{key:'section_id',label:'Section'},{key:'question_type',label:'Type'},{key:'countries_answered',label:'Countries Answered'},{key:'answered_pct',label:'Answered %'},{key:'country_iso_list',label:'Country List'}]);return;}
if(APP.view==='question'){c.appendChild(E('h2','','Question Analysis'));const qs=APP.raw.questions||[];const g=E('div','');g.style.marginBottom='12px';g.appendChild(E('label','','Question'));const s=document.createElement('select');for(const q of qs){const o=document.createElement('option');o.value=q.question_id;o.textContent=q.question_id+' ['+q.section_id+'] '+String(q.question_prompt||'').slice(0,80);s.appendChild(o);}g.appendChild(s);c.appendChild(g);const box1=E('div',''),box2=E('div',''),box3=E('div','');c.appendChild(box1);c.appendChild(box2);c.appendChild(box3);const rr=()=>{box1.innerHTML='';box2.innerHTML='';box3.innerHTML='';const d=qDist(s.value);rBars(box1,d.slice(0,20),'answer_value','respondent_count');rTable(box2,d,[{key:'country_iso',label:'Country'},{key:'answer_value',label:'Answer'},{key:'respondent_count',label:'Count'},{key:'percentage',label:'%'}]);const qm=(APP.raw.questions||[]).find(x=>x.question_id===s.value);if(qm&&qm.question_type==='text'&&!APP.filters.aggregateOnly){box3.appendChild(E('h2','','Masked Text Themes'));rTable(box3,themes(s.value),[{key:'theme',label:'Theme'},{key:'count',label:'Count'}]);}};s.addEventListener('change',rr);rr();return;}
if(APP.view==='compare'){c.appendChild(E('h2','','Country Comparison'));const qs=APP.raw.questions||[];const g=E('div','');g.style.marginBottom='12px';g.appendChild(E('label','','Question'));const s=document.createElement('select');for(const q of qs){const o=document.createElement('option');o.value=q.question_id;o.textContent=q.question_id+' ['+q.section_id+'] '+String(q.question_prompt||'').slice(0,80);s.appendChild(o);}g.appendChild(s);c.appendChild(g);const d1=E('div',''),d2=E('div','');c.appendChild(d1);c.appendChild(d2);const rr=()=>{const d=qDist(s.value);rTable(d1,d,[{key:'country_iso',label:'Country'},{key:'answer_value',label:'Answer'},{key:'respondent_count',label:'Count'},{key:'percentage',label:'%'}]);d2.innerHTML='';d2.appendChild(E('h2','','Largest Differences (Delta pp)'));rTable(d2,deltas(d,10),[{key:'answer_value',label:'Answer'},{key:'delta_pp',label:'Delta (pp)'},{key:'max_country',label:'Max Country'},{key:'min_country',label:'Min Country'}]);};s.addEventListener('change',rr);rr();return;}
};
const render=()=>{const root=document.getElementById('app-root');root.innerHTML='';const shell=E('div','shell');shell.appendChild(side());shell.appendChild(main());root.appendChild(shell);};
const boot=()=>{const root=document.getElementById('app-root');if(!root)return;try{APP.raw=decode();render();}catch(err){root.innerHTML='';const c=E('div','card panel');c.appendChild(E('h2','','Static Dashboard Error'));c.appendChild(E('p','',String(err&&err.message?err.message:err)));root.appendChild(c);}};
boot();
})();
"""
