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
:root{
  --teal-900:#134e4a;--teal-800:#115e59;--teal-700:#0f766e;--teal-600:#0d9488;--teal-500:#14b8a6;--teal-300:#5eead4;
  --slate-900:#0f172a;--slate-700:#334155;--slate-600:#475569;--slate-300:#cbd5e1;--slate-200:#e2e8f0;--slate-100:#f1f5f9;--slate-50:#f8fafc;
  --bg:#f5f9fa;--card:#ffffff;--focus:0 0 0 3px rgba(13,148,136,.35)
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:linear-gradient(180deg,#fbfefe 0%,var(--bg) 100%);color:var(--slate-900);font-family:Arial,Helvetica,sans-serif;line-height:1.5}
#app-root{min-height:100vh}
.shell{display:grid;grid-template-columns:300px 1fr;gap:18px;padding:18px}
.side,.card{background:var(--card);border:1px solid rgba(148,163,184,.32);border-radius:14px}
.side{padding:14px;position:sticky;top:10px;height:fit-content}
.main{display:grid;gap:16px}
.panel{padding:16px 18px}
.title{margin:0;font-size:1.2rem;font-weight:700;letter-spacing:.01em}
.sub{margin:6px 0 0;color:var(--slate-600);font-size:.9rem}
.warn{margin-top:12px;padding:10px 12px;border:1px solid #f9d9ba;border-radius:9px;background:#fff7ef;color:#7c2d12;font-size:.84rem}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;padding:14px 16px}
.k{border:1px solid rgba(148,163,184,.25);border-radius:10px;padding:10px;background:#fcfeff}
.k .l{color:var(--slate-600);font-size:.8rem}
.k .v{font-weight:700;font-size:1.2rem}
.tabs{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 16px}
.tab{border:1px solid var(--slate-300);border-radius:999px;padding:8px 12px;background:#f8fbfc;font-size:.84rem;font-weight:600;cursor:pointer;color:var(--teal-900)}
.tab[aria-pressed=true]{background:#dff7f4;border-color:var(--teal-500)}
.tab:hover{background:#eef8f7}
.chart-tabs{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 14px}
.chip{border:1px solid var(--slate-300);border-radius:999px;padding:7px 11px;background:#fff;font-size:.8rem;font-weight:600;cursor:pointer;color:var(--teal-900)}
.chip[aria-pressed=true]{background:#dff7f4;border-color:var(--teal-500)}
label{display:block;margin-bottom:6px;color:var(--slate-600);font-size:.82rem;font-weight:600}
.checks{max-height:180px;overflow:auto;border:1px solid var(--slate-200);border-radius:8px;padding:8px}
.checks label{display:flex;align-items:center;gap:8px;margin:0;padding:4px 0;color:var(--slate-900);font-size:.85rem;cursor:pointer}
button,select,input[type=checkbox]{font-family:inherit;min-height:42px}
button,select{width:100%;border:1px solid var(--slate-300);border-radius:8px;padding:8px 10px;background:#fff;color:var(--slate-900)}
.empty{border:1px dashed var(--slate-300);border-radius:10px;padding:14px;color:var(--slate-600);background:#fbfdff}
.small{color:var(--slate-600);font-size:.8rem}
.metric{display:flex;gap:8px;align-items:baseline;margin:8px 0 10px}
.metric .label{font-size:.86rem;font-weight:600;color:var(--slate-700)}
.metric .value{font-size:1.1rem;font-weight:700;color:var(--teal-800)}
.tbl{overflow:auto}
.tbl table{width:100%;border-collapse:collapse}
.tbl th,.tbl td{border-bottom:1px solid var(--slate-200);padding:8px;text-align:left;font-size:.84rem;vertical-align:top}
.tbl th{background:#f6fafb;font-weight:700;color:var(--teal-900)}
.tbl tr:nth-child(even) td{background:#fcfeff}
.heat{border-collapse:collapse;min-width:560px}
.heat th,.heat td{border:1px solid var(--slate-200);padding:6px 8px;text-align:center;font-size:.8rem}
.heat th{background:#f6fafb;color:var(--teal-900)}
.hbars{display:grid;gap:8px}
.hrow{display:grid;grid-template-columns:240px 1fr 70px;gap:10px;align-items:center}
.hlabel{font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.htrack{height:14px;background:var(--slate-100);border-radius:999px;overflow:hidden}
.hfill{height:14px;background:linear-gradient(90deg,var(--teal-500),var(--teal-700))}
.hvalue{text-align:right;font-size:.8rem;font-weight:700;color:var(--slate-700)}
.lolis{display:grid;gap:10px}
.lrow{display:grid;grid-template-columns:240px 1fr 70px;gap:10px;align-items:center}
.laxis{position:relative;height:16px;border-bottom:2px solid #d5e3e1}
.ldot{position:absolute;top:-4px;width:10px;height:10px;border-radius:999px;background:var(--teal-700)}
.grad-wrap{overflow:auto}
.grad-svg text{font-family:Arial,Helvetica,sans-serif}
.sa-wrap{overflow:auto;background:#fbfeff;border:1px solid rgba(148,163,184,.24);border-radius:10px;padding:10px}
.sa-svg text{font-family:Arial,Helvetica,sans-serif}
.cloud{border:none;background:#f7fbfb;border-radius:10px;padding:16px 18px;min-height:150px}
.cloud-title{font-size:14px;font-weight:700;color:var(--slate-900);margin-bottom:10px}
.cloud-tokens{display:flex;flex-wrap:wrap;align-items:center}
.cloud-token{display:inline-block;margin:8px 12px;line-height:1.2}
.responses{max-height:480px;overflow:auto;border:1px solid rgba(148,163,184,.32);border-radius:10px}
.responses table{width:100%;border-collapse:collapse}
.responses th,.responses td{border-bottom:1px solid var(--slate-200);padding:8px;text-align:left;font-size:.83rem;vertical-align:top}
.responses th{position:sticky;top:0;background:#f6fafb;color:var(--teal-900)}
:focus-visible{outline:none;box-shadow:var(--focus)}
@media(max-width:1200px){.hrow,.lrow{grid-template-columns:1fr}.shell{grid-template-columns:1fr}.side{position:static}.kpis{grid-template-columns:repeat(2,minmax(120px,1fr))}}
@media(max-width:600px){.kpis{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
"""


def build_client_js() -> str:
    """Return compact JS runtime for exported dashboard."""
    return """
(()=>{'use strict';
const APP={
  raw:null,
  filters:{countries:[],roles:[],sections:[],questionTypes:[],aggregateOnly:false},
  view:'heat',
  questionState:{selectedQuestionId:null,chartMode:'horizontal'}
};
const VIEWS=[['heat','Section Heatmap'],['section','Section Summary'],['question','Question Analysis'],['compare','Country Comparison']];
const CHART_MODES=[['horizontal','Horizontal Bar'],['lollipop','Lollipop'],['gradient','Gradient + Average']];
const STRUCTURED_TYPES=new Set(['single_select','multi_select','ranking','boolean']);
const WORD_COLORS=['#115e59','#0f766e','#0d9488','#14b8a6','#2dd4bf','#5eead4'];
const STOP_WORDS=new Set(['the','and','for','that','with','from','this','there','have','your','what','which','will','into','their','they','are','was','were','not','but','can','has','had','all','any','our','you','about']);
const TOKEN_RE=/[a-zA-Z]{3,}/g;
const U=(a)=>Array.from(new Set((a||[]).filter(v=>v!==null&&v!==undefined&&String(v).trim()!==''))).sort();
const E=(t,c,tx)=>{const el=document.createElement(t);if(c)el.className=c;if(tx!==undefined)el.textContent=tx;return el;};
const escapeHtml=(value)=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');
const round2=(value)=>Math.round(Number(value||0)*100)/100;

const decode=()=>{
  if(!window.__DATA_B64_GZ__)throw new Error('Missing embedded payload');
  const rep=window.__EXPORT_REPORT__||{};
  if(String(rep.encoding||'').includes('gzip'))throw new Error('Unsupported encoding: '+rep.encoding);
  const b=atob(window.__DATA_B64_GZ__);
  const bytes=Uint8Array.from(b,ch=>ch.charCodeAt(0));
  return JSON.parse(new TextDecoder('utf-8').decode(bytes));
};

function applyFilters(rows){
  return (rows||[]).filter(r=>(
    (!APP.filters.countries.length||APP.filters.countries.includes(r.country_iso))&&
    (!APP.filters.roles.length||APP.filters.roles.includes(r.role))&&
    (!APP.filters.sections.length||APP.filters.sections.includes(r.section_id))&&
    (!APP.filters.questionTypes.length||APP.filters.questionTypes.includes(r.question_type))
  ));
}

const filteredAnswers=()=>applyFilters(APP.raw.answers||[]);
const filteredAnswerItems=()=>{
  const keys=new Set(filteredAnswers().map(r=>r.respondent_id+'|'+r.question_id));
  return (APP.raw.answer_items||[]).filter(item=>keys.has(item.respondent_id+'|'+item.question_id));
};
const getOptionProfiles=()=>(((APP.raw||{}).derived||{}).question_option_profiles||{});
const normalizeKey=(value)=>String(value||'').trim().toLowerCase().replace(/\\s+/g,' ');

const canonicalizeValue=(questionId,value)=>{
  const raw=String(value||'').trim();
  if(!raw)return '';
  const profile=getOptionProfiles()[questionId];
  if(!profile)return raw;
  const mapped=(profile.alias_map||{})[normalizeKey(raw)];
  if(mapped)return String(mapped);
  return String(profile.other_label||'Other');
};

function computeSectionHeatmap(){
  const m=new Map();
  for(const row of filteredAnswers()){
    const key=row.section_id+'|'+row.country_iso;
    if(!m.has(key))m.set(key,{section_id:row.section_id,country_iso:row.country_iso,total_count:0,answered_count:0});
    const item=m.get(key);
    item.total_count+=1;
    if(row.answer_state==='answered')item.answered_count+=1;
  }
  return [...m.values()].map(v=>({
    section_id:v.section_id,
    country_iso:v.country_iso,
    total_count:v.total_count,
    answered_count:v.answered_count,
    answered_pct:v.total_count?round2((v.answered_count/v.total_count)*100):0
  })).sort((a,b)=>(String(a.section_id)+String(a.country_iso)).localeCompare(String(b.section_id)+String(b.country_iso)));
}

const sectionRows=()=>{
  const grouped=new Map();
  for(const row of filteredAnswers()){
    if(!grouped.has(row.question_id)){
      grouped.set(row.question_id,{
        question_id:row.question_id,
        question_prompt:row.question_prompt,
        section_id:row.section_id,
        question_type:row.question_type,
        total_count:0,
        answered_count:0,
        countries:new Set()
      });
    }
    const target=grouped.get(row.question_id);
    target.total_count+=1;
    if(row.answer_state==='answered'){
      target.answered_count+=1;
      if(row.country_iso)target.countries.add(row.country_iso);
    }
  }
  return [...grouped.values()].map(v=>({
    question_id:v.question_id,
    question_prompt:v.question_prompt,
    section_id:v.section_id,
    question_type:v.question_type,
    countries_answered:v.countries.size,
    country_iso_list:[...v.countries].sort().join(', '),
    answered_pct:v.total_count?round2((v.answered_count/v.total_count)*100):0
  })).sort((a,b)=>String(a.question_id).localeCompare(String(b.question_id)));
};

const getQuestions=()=>{
  return [...(APP.raw.questions||[])].sort((a,b)=>{
    const ao=Number(a.question_order||0);const bo=Number(b.question_order||0);
    if(ao!==bo)return ao-bo;
    return String(a.question_id).localeCompare(String(b.question_id));
  });
};
const getQuestionMeta=(questionId)=>getQuestions().find(q=>q.question_id===questionId)||null;

const getEffectiveQuestionType=(questionId)=>{
  const rows=filteredAnswers().filter(r=>r.question_id===questionId);
  if(!rows.length){
    const meta=getQuestionMeta(questionId);
    return meta?String(meta.question_type||''):null;
  }
  const counts=new Map();
  for(const row of rows){
    const key=String(row.question_type||'').trim();
    if(!key)continue;
    counts.set(key,(counts.get(key)||0)+1);
  }
  if(!counts.size){
    const meta=getQuestionMeta(questionId);
    return meta?String(meta.question_type||''):null;
  }
  return [...counts.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0][0];
};

const applyProfileOrder=(questionId,rows)=>{
  const profile=getOptionProfiles()[questionId];
  const byValue=new Map();
  for(const row of rows){
    const key=String(row.answer_value||'').trim();
    if(!key)continue;
    if(!byValue.has(key))byValue.set(key,{answer_value:key,response_count:0,respondents:new Set()});
    const item=byValue.get(key);
    item.response_count+=Number(row.response_count||0);
    for(const respondentId of row.respondent_ids||[])item.respondents.add(respondentId);
  }
  const merged=[...byValue.values()].map(v=>({answer_value:v.answer_value,response_count:v.response_count,respondent_count:v.respondents.size}));
  if(!profile){
    return merged.sort((a,b)=>b.response_count-a.response_count||String(a.answer_value).localeCompare(String(b.answer_value)));
  }

  const order=Array.isArray(profile.canonical_order)?profile.canonical_order:[];
  const orderMap=new Map(order.map((label,idx)=>[String(label),idx]));
  const otherLabel=String(profile.other_label||'Other');
  const sourceMap=new Map(merged.map(item=>[String(item.answer_value),{...item}]));
  const ordered=[];

  for(const label of order){
    const key=String(label);
    const item=sourceMap.get(key)||{answer_value:key,response_count:0,respondent_count:0};
    sourceMap.delete(key);
    if(key!==otherLabel&&Number(item.response_count)===0)continue;
    ordered.push(item);
  }

  if(sourceMap.size){
    let otherResponses=0;
    let otherRespondents=0;
    for(const item of sourceMap.values()){
      otherResponses+=Number(item.response_count||0);
      otherRespondents+=Number(item.respondent_count||0);
    }
    const existing=ordered.find(item=>String(item.answer_value)===otherLabel);
    if(existing){
      existing.response_count+=otherResponses;
      existing.respondent_count+=otherRespondents;
    }else{
      ordered.push({answer_value:otherLabel,response_count:otherResponses,respondent_count:otherRespondents});
    }
  }

  return ordered.sort((a,b)=>{
    const ao=orderMap.has(String(a.answer_value))?orderMap.get(String(a.answer_value)):999;
    const bo=orderMap.has(String(b.answer_value))?orderMap.get(String(b.answer_value)):999;
    if(ao!==bo)return ao-bo;
    return String(a.answer_value).localeCompare(String(b.answer_value));
  });
};

const getQuestionAnswerSummary=(questionId)=>{
  const rows=filteredAnswers().filter(r=>r.question_id===questionId);
  if(!rows.length)return [];
  const answered=rows.filter(r=>r.answer_state==='answered'&&r.respondent_id!==null&&r.respondent_id!==undefined&&String(r.respondent_id).trim()!=='');
  const answeredIds=new Set(answered.map(r=>String(r.respondent_id)));
  const answeredTotal=answeredIds.size;
  if(!answeredTotal)return [];

  const questionType=String(getEffectiveQuestionType(questionId)||'');
  const groupedRaw=[];

  if(questionType==='multi_select'||questionType==='ranking'){
    const items=filteredAnswerItems().filter(item=>item.question_id===questionId);
    if(!items.length)return [];
    const grouped=new Map();
    for(const item of items){
      const rawValue=String(item.item_value||'').trim();
      if(!rawValue)continue;
      const answerValue=canonicalizeValue(questionId,rawValue);
      if(!answerValue)continue;
      if(!grouped.has(answerValue))grouped.set(answerValue,{answer_value:answerValue,response_count:0,respondent_ids:[]});
      const target=grouped.get(answerValue);
      target.response_count+=1;
      target.respondent_ids.push(String(item.respondent_id||''));
    }
    for(const value of grouped.values())groupedRaw.push(value);
  }else{
    const grouped=new Map();
    for(const row of answered){
      const rawValue=String(row.answer_value_masked||'').trim();
      if(!rawValue)continue;
      const answerValue=canonicalizeValue(questionId,rawValue);
      if(!answerValue)continue;
      if(!grouped.has(answerValue))grouped.set(answerValue,{answer_value:answerValue,response_count:0,respondent_ids:[]});
      const target=grouped.get(answerValue);
      target.response_count+=1;
      target.respondent_ids.push(String(row.respondent_id||''));
    }
    for(const value of grouped.values())groupedRaw.push(value);
  }

  const ordered=applyProfileOrder(questionId,groupedRaw);
  return ordered.map(row=>({
    answer_value:row.answer_value,
    response_count:Number(row.response_count||0),
    respondent_count:Number(row.respondent_count||0),
    percentage:round2((Number(row.response_count||0)/answeredTotal)*100),
    answered_respondent_total:answeredTotal
  }));
};

function computeQuestionDistribution(questionId){
  return getQuestionAnswerSummary(questionId);
}

const getQuestionCountryDistribution=(questionId)=>{
  const rows=filteredAnswers().filter(r=>r.question_id===questionId&&r.answer_state==='answered');
  if(!rows.length)return [];
  const questionType=String(getEffectiveQuestionType(questionId)||'');
  const grouped=new Map();
  const totals=new Map();
  for(const row of rows){
    const country=String(row.country_iso||'');
    if(!totals.has(country))totals.set(country,new Set());
    totals.get(country).add(String(row.respondent_id||''));
  }

  if(questionType==='multi_select'||questionType==='ranking'){
    for(const item of filteredAnswerItems().filter(value=>value.question_id===questionId)){
      const country=String(item.country_iso||'');
      const value=String(item.item_value||'').trim();
      if(!value)continue;
      const key=country+'|'+value;
      if(!grouped.has(key))grouped.set(key,{country_iso:country,answer_value:value,respondents:new Set()});
      grouped.get(key).respondents.add(String(item.respondent_id||''));
    }
  }else{
    for(const row of rows){
      const value=String(row.answer_value_masked||'').trim();
      if(!value)continue;
      const country=String(row.country_iso||'');
      const key=country+'|'+value;
      if(!grouped.has(key))grouped.set(key,{country_iso:country,answer_value:value,respondents:new Set()});
      grouped.get(key).respondents.add(String(row.respondent_id||''));
    }
  }

  return [...grouped.values()].map(item=>{
    const total=(totals.get(item.country_iso)||new Set()).size;
    const respondentCount=item.respondents.size;
    return{
      country_iso:item.country_iso,
      answer_value:item.answer_value,
      respondent_count:respondentCount,
      percentage:total?round2((respondentCount/total)*100):0
    };
  }).sort((a,b)=>a.country_iso===b.country_iso?b.respondent_count-a.respondent_count:String(a.country_iso).localeCompare(String(b.country_iso)));
};

const getCountryDeltas=(rows,topN=10)=>{
  const grouped=new Map();
  for(const row of rows){
    const answer=String(row.answer_value||'');
    if(!grouped.has(answer))grouped.set(answer,[]);
    grouped.get(answer).push(row);
  }
  const out=[];
  for(const [answer,values] of grouped.entries()){
    let min=Number.POSITIVE_INFINITY,max=Number.NEGATIVE_INFINITY,minCountry='',maxCountry='';
    for(const row of values){
      const p=Number(row.percentage||0);
      if(p<min){min=p;minCountry=String(row.country_iso||'');}
      if(p>max){max=p;maxCountry=String(row.country_iso||'');}
    }
    out.push({answer_value:answer,delta_pp:round2(max-min),max_country:maxCountry,min_country:minCountry});
  }
  return out.sort((a,b)=>b.delta_pp-a.delta_pp).slice(0,topN);
};

const getTextThemes=(questionId,topN=12)=>{
  if(APP.filters.aggregateOnly)return [];
  const tokens=new Map();
  const rows=filteredAnswers().filter(row=>row.question_id===questionId&&String(getEffectiveQuestionType(questionId)||'')==='text'&&row.answer_state==='answered');
  for(const row of rows){
    const text=String(row.answer_value_masked||'').toLowerCase();
    const matches=text.match(TOKEN_RE)||[];
    for(const token of matches){
      if(STOP_WORDS.has(token))continue;
      tokens.set(token,(tokens.get(token)||0)+1);
    }
  }
  return [...tokens.entries()].map(([theme,count])=>({theme,count}))
    .sort((a,b)=>b.count-a.count||a.theme.localeCompare(b.theme))
    .slice(0,topN);
};

const getMaskedTextResponses=(questionId)=>{
  return filteredAnswers().filter(row=>row.question_id===questionId&&String(getEffectiveQuestionType(questionId)||'')==='text'&&row.answer_state==='answered'&&String(row.answer_value_masked||'').trim()!=='')
    .map(row=>({
      country_iso:String(row.country_iso||''),
      role:String(row.role||''),
      text_response:String(row.answer_value_masked||'')
    }));
};

const buildWordCloudTokens=(themes,minSize=14,maxSize=44)=>{
  if(!themes.length)return [];
  const ordered=[...themes].sort((a,b)=>b.count-a.count||String(a.theme).localeCompare(String(b.theme)));
  const max=Math.max(...ordered.map(t=>Number(t.count||0)));
  const min=Math.min(...ordered.map(t=>Number(t.count||0)));
  const span=Math.max(max-min,1);
  return ordered.map((theme,index)=>{
    const count=Number(theme.count||0);
    const scale=(count-min)/span;
    return{
      theme:String(theme.theme||''),
      count,
      font_size:Math.round(minSize+(maxSize-minSize)*scale),
      weight:index<Math.ceil(ordered.length/4)?700:600,
      color:WORD_COLORS[index%WORD_COLORS.length]
    };
  });
};

const rTable=(container,rows,columns)=>{
  container.innerHTML='';
  if(!rows.length){
    container.appendChild(E('div','empty','No data for the current filters.'));
    return;
  }
  const wrap=E('div','tbl');
  const table=E('table');
  const thead=E('thead');
  const headRow=E('tr');
  for(const column of columns)headRow.appendChild(E('th','',column.label));
  thead.appendChild(headRow);
  const tbody=E('tbody');
  for(const row of rows){
    const tr=E('tr');
    for(const column of columns){
      const value=row[column.key];
      tr.appendChild(E('td','',value!==null&&value!==undefined?String(value):''));
    }
    tbody.appendChild(tr);
  }
  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);
  container.appendChild(wrap);
};

const rWordCloud=(container,themes,title)=>{
  container.innerHTML='';
  if(!themes.length){
    container.appendChild(E('div','empty','No theme tokens available.'));
    return;
  }
  const cloud=E('div','cloud');
  cloud.appendChild(E('div','cloud-title',title));
  const tokensWrap=E('div','cloud-tokens');
  for(const token of buildWordCloudTokens(themes)){
    const span=E('span','cloud-token',token.theme);
    span.style.fontSize=String(token.font_size)+'px';
    span.style.fontWeight=String(token.weight);
    span.style.color=token.color;
    span.title=token.theme+' ('+token.count+')';
    tokensWrap.appendChild(span);
  }
  cloud.appendChild(tokensWrap);
  container.appendChild(cloud);
};

const rHorizontalChart=(container,rows,labelKey,valueKey,valueLabel)=>{
  container.innerHTML='';
  if(!rows.length){
    container.appendChild(E('div','empty','No data for chart.'));
    return;
  }
  const ordered=[...rows].sort((a,b)=>Number(b[valueKey]||0)-Number(a[valueKey]||0)||String(a[labelKey]).localeCompare(String(b[labelKey])));
  const max=Math.max(...ordered.map(row=>Number(row[valueKey]||0)),1);
  const list=E('div','hbars');
  for(const row of ordered){
    const line=E('div','hrow');
    line.appendChild(E('div','hlabel',String(row[labelKey])));
    const track=E('div','htrack');
    const fill=E('div','hfill');
    fill.style.width=((Number(row[valueKey]||0)/max)*100).toFixed(2)+'%';
    track.appendChild(fill);
    line.appendChild(track);
    line.appendChild(E('div','hvalue',String(row[valueKey])+' '+valueLabel));
    list.appendChild(line);
  }
  container.appendChild(list);
};

const rLollipopChart=(container,rows,labelKey,valueKey,valueLabel)=>{
  container.innerHTML='';
  if(!rows.length){
    container.appendChild(E('div','empty','No data for chart.'));
    return;
  }
  const ordered=[...rows].sort((a,b)=>Number(b[valueKey]||0)-Number(a[valueKey]||0)||String(a[labelKey]).localeCompare(String(b[labelKey])));
  const max=Math.max(...ordered.map(row=>Number(row[valueKey]||0)),1);
  const list=E('div','lolis');
  for(const row of ordered){
    const line=E('div','lrow');
    line.appendChild(E('div','hlabel',String(row[labelKey])));
    const axis=E('div','laxis');
    const dot=E('div','ldot');
    dot.style.left='calc('+((Number(row[valueKey]||0)/max)*100).toFixed(2)+'% - 5px)';
    axis.appendChild(dot);
    line.appendChild(axis);
    line.appendChild(E('div','hvalue',String(row[valueKey])+' '+valueLabel));
    list.appendChild(line);
  }
  container.appendChild(list);
};

const rGradientChart=(container,rows,labelKey,valueKey,valueLabel)=>{
  container.innerHTML='';
  if(!rows.length){
    container.appendChild(E('div','empty','No data for chart.'));
    return;
  }
  const ordered=[...rows].sort((a,b)=>Number(b[valueKey]||0)-Number(a[valueKey]||0)||String(a[labelKey]).localeCompare(String(b[labelKey])));
  const values=ordered.map(row=>Number(row[valueKey]||0));
  const max=Math.max(...values,1);
  const average=values.reduce((sum,current)=>sum+current,0)/values.length;
  const width=Math.max(640,ordered.length*86);
  const height=300;
  const m={top:20,right:18,bottom:96,left:44};
  const plotW=width-m.left-m.right;
  const plotH=height-m.top-m.bottom;
  const step=plotW/ordered.length;
  let bars='';
  let labels='';
  for(let i=0;i<ordered.length;i+=1){
    const row=ordered[i];
    const x=m.left+i*step+step*0.18;
    const w=step*0.64;
    const val=Number(row[valueKey]||0);
    const ratio=val/max;
    const h=ratio*plotH;
    const y=m.top+plotH-h;
    const hue=Math.round(180-(ratio*26));
    bars+='<rect x="'+x.toFixed(2)+'" y="'+y.toFixed(2)+'" width="'+w.toFixed(2)+'" height="'+h.toFixed(2)+'" fill="hsl('+hue+',74%,38%)" rx="4"></rect>';
    bars+='<text x="'+(x+w/2).toFixed(2)+'" y="'+(y-6).toFixed(2)+'" font-size="11" text-anchor="middle" fill="#334155" font-weight="700">'+escapeHtml(String(val))+'</text>';
    labels+='<text x="'+(x+w/2).toFixed(2)+'" y="'+(m.top+plotH+14).toFixed(2)+'" font-size="10" fill="#334155" transform="rotate(-30 '+(x+w/2).toFixed(2)+' '+(m.top+plotH+14).toFixed(2)+')" text-anchor="end">'+escapeHtml(String(row[labelKey]))+'</text>';
  }
  const avgY=m.top+plotH-(average/max)*plotH;
  const grid='<line x1="'+m.left+'" y1="'+m.top+'" x2="'+m.left+'" y2="'+(m.top+plotH)+'" stroke="#cbd5e1"></line>'
    +'<line x1="'+m.left+'" y1="'+(m.top+plotH)+'" x2="'+(m.left+plotW)+'" y2="'+(m.top+plotH)+'" stroke="#cbd5e1"></line>'
    +'<line x1="'+m.left+'" y1="'+avgY.toFixed(2)+'" x2="'+(m.left+plotW)+'" y2="'+avgY.toFixed(2)+'" stroke="#dc2626" stroke-width="2" stroke-dasharray="6 4"></line>'
    +'<text x="'+(m.left+plotW-4)+'" y="'+(avgY-5).toFixed(2)+'" fill="#dc2626" font-size="11" text-anchor="end" font-weight="700">Average ('+average.toFixed(1)+')</text>';
  const axis='<text x="8" y="'+(m.top+plotH/2).toFixed(2)+'" transform="rotate(-90 8 '+(m.top+plotH/2).toFixed(2)+')" fill="#475569" font-size="11">'+escapeHtml(valueLabel)+'</text>';
  const wrap=E('div','grad-wrap');
  wrap.innerHTML='<svg class="grad-svg" width="'+width+'" height="'+height+'" viewBox="0 0 '+width+' '+height+'" role="img" aria-label="Gradient chart">'+grid+bars+labels+axis+'</svg>';
  container.appendChild(wrap);
};

const rStructuredDualAxisChart=(container,summary,title)=>{
  container.innerHTML='';
  if(!summary.length){
    container.appendChild(E('div','empty','No data for chart.'));
    return;
  }
  const answeredTotal=Number(summary[0].answered_respondent_total||0);
  const countMaxRaw=Math.max(...summary.map(item=>Number(item.response_count||0)),0);
  const domainAnchor=Math.max(countMaxRaw,answeredTotal,1);
  const countAxisMax=countMaxRaw>=domainAnchor?domainAnchor+1:domainAnchor;

  const ordered=[...summary].sort((a,b)=>Number(b.response_count||0)-Number(a.response_count||0)||String(a.answer_value).localeCompare(String(b.answer_value)));
  const width=Math.max(680,ordered.length*94);
  const height=420;
  const m={top:30,right:66,bottom:120,left:66};
  const plotW=width-m.left-m.right;
  const plotH=height-m.top-m.bottom;
  const step=plotW/ordered.length;
  const barW=step*0.58;
  const gridTicks=5;

  let grid='';
  for(let idx=0;idx<=gridTicks;idx+=1){
    const y=m.top+(plotH/gridTicks)*idx;
    grid+='<line x1="'+m.left+'" y1="'+y.toFixed(2)+'" x2="'+(m.left+plotW)+'" y2="'+y.toFixed(2)+'" stroke="#d8e3e1" stroke-width="1"></line>';
    const countLabel=Math.round(countAxisMax-((countAxisMax/gridTicks)*idx));
    const pctLabel=Math.round((100/gridTicks)*(gridTicks-idx));
    grid+='<text x="'+(m.left-10)+'" y="'+(y+4).toFixed(2)+'" font-size="11" text-anchor="end" fill="#475569">'+countLabel+'</text>';
    grid+='<text x="'+(m.left+plotW+10)+'" y="'+(y+4).toFixed(2)+'" font-size="11" text-anchor="start" fill="#475569">'+pctLabel+'</text>';
  }

  let bars='';
  let labels='';
  let pointPath='';
  let points='';
  for(let i=0;i<ordered.length;i+=1){
    const row=ordered[i];
    const xCenter=m.left+i*step+(step/2);
    const x=xCenter-(barW/2);
    const count=Number(row.response_count||0);
    const pct=Number(row.percentage||0);
    const barH=(count/countAxisMax)*plotH;
    const y=m.top+plotH-barH;
    bars+='<rect x="'+x.toFixed(2)+'" y="'+y.toFixed(2)+'" width="'+barW.toFixed(2)+'" height="'+barH.toFixed(2)+'" fill="#0f766e" rx="4"></rect>';
    bars+='<text x="'+xCenter.toFixed(2)+'" y="'+(y-7).toFixed(2)+'" font-size="11" fill="#334155" text-anchor="middle" font-weight="700">'+escapeHtml(String(count))+'</text>';
    labels+='<text x="'+xCenter.toFixed(2)+'" y="'+(m.top+plotH+16).toFixed(2)+'" font-size="10" fill="#334155" transform="rotate(-30 '+xCenter.toFixed(2)+' '+(m.top+plotH+16).toFixed(2)+')" text-anchor="end">'+escapeHtml(String(row.answer_value))+'</text>';
    const py=m.top+plotH-(Math.max(0,Math.min(100,pct))/100)*plotH;
    pointPath+=(pointPath?' ':'')+xCenter.toFixed(2)+','+py.toFixed(2);
    points+='<circle cx="'+xCenter.toFixed(2)+'" cy="'+py.toFixed(2)+'" r="4" fill="#5eead4" stroke="#0f766e" stroke-width="1.5"></circle>';
  }
  const line='<polyline points="'+pointPath+'" fill="none" stroke="#14b8a6" stroke-width="2" stroke-dasharray="4 2"></polyline>';
  const axes='<line x1="'+m.left+'" y1="'+m.top+'" x2="'+m.left+'" y2="'+(m.top+plotH)+'" stroke="#94a3b8"></line>'
    +'<line x1="'+(m.left+plotW)+'" y1="'+m.top+'" x2="'+(m.left+plotW)+'" y2="'+(m.top+plotH)+'" stroke="#94a3b8"></line>'
    +'<line x1="'+m.left+'" y1="'+(m.top+plotH)+'" x2="'+(m.left+plotW)+'" y2="'+(m.top+plotH)+'" stroke="#94a3b8"></line>'
    +'<text x="'+(m.left-46)+'" y="'+(m.top+plotH/2).toFixed(2)+'" transform="rotate(-90 '+(m.left-46)+' '+(m.top+plotH/2).toFixed(2)+')" font-size="12" fill="#334155">Total Count</text>'
    +'<text x="'+(m.left+plotW+46)+'" y="'+(m.top+plotH/2).toFixed(2)+'" transform="rotate(90 '+(m.left+plotW+46)+' '+(m.top+plotH/2).toFixed(2)+')" font-size="12" fill="#334155">Percentage (%)</text>';
  const titleText='<text x="'+(width/2).toFixed(2)+'" y="18" text-anchor="middle" font-size="14" fill="#0f172a" font-weight="700">'+escapeHtml(title)+'</text>';
  const wrap=E('div','sa-wrap');
  wrap.innerHTML='<svg class="sa-svg" width="'+width+'" height="'+height+'" viewBox="0 0 '+width+' '+height+'" role="img" aria-label="Structured answer chart">'+titleText+grid+axes+bars+line+points+labels+'</svg>';
  container.appendChild(wrap);
};

const rChartModeTabs=(container,current,onChange)=>{
  const tabs=E('div','chart-tabs');
  for(const [mode,label] of CHART_MODES){
    const button=E('button','chip',label);
    button.setAttribute('aria-pressed',mode===current?'true':'false');
    button.addEventListener('click',()=>onChange(mode));
    tabs.appendChild(button);
  }
  container.appendChild(tabs);
};

const rAlternativeChart=(container,rows,labelKey,valueKey,mode,valueLabel)=>{
  if(mode==='lollipop'){
    rLollipopChart(container,rows,labelKey,valueKey,valueLabel);
    return;
  }
  if(mode==='gradient'){
    rGradientChart(container,rows,labelKey,valueKey,valueLabel);
    return;
  }
  rHorizontalChart(container,rows,labelKey,valueKey,valueLabel);
};

const rTextResponses=(container,responses)=>{
  container.innerHTML='';
  if(!responses.length){
    container.appendChild(E('div','empty','No masked text responses for the current filters.'));
    return;
  }
  const count=E('p','small','Showing all '+responses.length+' masked responses.');
  container.appendChild(count);
  const wrap=E('div','responses');
  const table=E('table');
  const thead=E('thead');
  const head=E('tr');
  head.appendChild(E('th','','Country'));
  head.appendChild(E('th','','Role'));
  head.appendChild(E('th','','Masked Response'));
  thead.appendChild(head);
  const tbody=E('tbody');
  for(const row of responses){
    const tr=E('tr');
    tr.appendChild(E('td','',row.country_iso||''));
    tr.appendChild(E('td','',row.role||''));
    tr.appendChild(E('td','',row.text_response||''));
    tbody.appendChild(tr);
  }
  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);
  container.appendChild(wrap);
};

const rHeat=(container,rows)=>{
  container.innerHTML='';
  if(!rows.length){
    container.appendChild(E('div','empty','No heatmap data for selected filters.'));
    return;
  }
  const sections=U(rows.map(row=>row.section_id));
  const countries=U(rows.map(row=>row.country_iso));
  const grid=new Map(rows.map(row=>[row.section_id+'|'+row.country_iso,row]));
  const wrap=E('div','tbl');
  const table=E('table','heat');
  const thead=E('thead');
  const head=E('tr');
  head.appendChild(E('th','','Section'));
  for(const country of countries)head.appendChild(E('th','',country));
  thead.appendChild(head);
  const tbody=E('tbody');
  for(const section of sections){
    const tr=E('tr');
    tr.appendChild(E('th','',section));
    for(const country of countries){
      const item=grid.get(section+'|'+country);
      const pct=item?Number(item.answered_pct||0):0;
      const cell=E('td','',String(pct));
      cell.style.backgroundColor='hsl(175 55% '+(98-Math.round((pct/100)*48))+'%)';
      cell.title=section+' / '+country+': '+pct+'% answered';
      tr.appendChild(cell);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);
  container.appendChild(wrap);
};

const kpis=()=>{
  const respondents=APP.raw.respondents||[];
  const answers=filteredAnswers();
  return{
    respondents:respondents.length,
    countries:U(respondents.map(row=>row.country_iso)).length,
    questions:(APP.raw.questions||[]).length,
    answeredRows:answers.filter(row=>row.answer_state==='answered').length
  };
};

const side=()=>{
  const el=E('aside','side');
  el.appendChild(E('h2','title','Filters'));
  el.appendChild(E('p','sub','Refine analysis by country, role, section, and question type.'));

  const groups=[
    ['countries','Countries (ISO)',U((APP.raw.respondents||[]).map(row=>row.country_iso))],
    ['roles','Roles',U((APP.raw.respondents||[]).map(row=>row.role))],
    ['sections','Sections',U((APP.raw.questions||[]).map(row=>row.section_id))],
    ['questionTypes','Question Types',U((APP.raw.questions||[]).map(row=>row.question_type))]
  ];
  for(const [key,label,values] of groups){
    const block=E('div','');
    block.style.marginBottom='12px';
    block.appendChild(E('label','',label));
    const box=E('div','checks');
    for(const value of values){
      const id='f-'+key+'-'+String(value).replace(/[^A-Za-z0-9_-]/g,'_');
      const line=document.createElement('label');
      line.setAttribute('for',id);
      const cb=document.createElement('input');
      cb.type='checkbox';
      cb.id=id;
      cb.checked=APP.filters[key].includes(value);
      cb.addEventListener('change',()=>{
        if(cb.checked){
          if(!APP.filters[key].includes(value))APP.filters[key].push(value);
        }else{
          APP.filters[key]=APP.filters[key].filter(item=>item!==value);
        }
        render();
      });
      line.appendChild(cb);
      line.appendChild(E('span','',String(value)));
      box.appendChild(line);
    }
    block.appendChild(box);
    el.appendChild(block);
  }

  const privacy=E('div','');
  privacy.style.marginBottom='12px';
  privacy.appendChild(E('label','','Privacy View'));
  const privacyBox=E('div','checks');
  const row=document.createElement('label');
  const cb=document.createElement('input');
  cb.type='checkbox';
  cb.checked=APP.filters.aggregateOnly;
  cb.addEventListener('change',()=>{APP.filters.aggregateOnly=cb.checked;render();});
  row.appendChild(cb);
  row.appendChild(E('span','','Aggregate-only view'));
  privacyBox.appendChild(row);
  privacy.appendChild(privacyBox);
  el.appendChild(privacy);

  const reset=E('button','','Reset Filters');
  reset.addEventListener('click',()=>{
    APP.filters.countries=[];
    APP.filters.roles=[];
    APP.filters.sections=[];
    APP.filters.questionTypes=[];
    APP.filters.aggregateOnly=false;
    render();
  });
  el.appendChild(reset);

  const rep=window.__EXPORT_REPORT__||{};
  const status=E('div','small','Encoded size: '+String(rep.size_bytes||0)+' bytes'+((rep.warnings||[]).length?' | Warning: '+rep.warnings.join('; '):''));
  status.style.marginTop='10px';
  el.appendChild(status);
  return el;
};

const rQuestionView=(container)=>{
  container.appendChild(E('h2','','Question Analysis'));
  const questions=getQuestions();
  if(!questions.length){
    container.appendChild(E('div','empty','No questions available.'));
    return;
  }

  if(!APP.questionState.selectedQuestionId){
    APP.questionState.selectedQuestionId=questions[0].question_id;
  }
  const exists=questions.some(question=>question.question_id===APP.questionState.selectedQuestionId);
  if(!exists)APP.questionState.selectedQuestionId=questions[0].question_id;

  const picker=E('div','');
  picker.style.marginBottom='10px';
  picker.appendChild(E('label','','Question'));
  const select=document.createElement('select');
  for(const question of questions){
    const option=document.createElement('option');
    option.value=question.question_id;
    option.textContent=question.question_id+' ['+question.section_id+'] '+String(question.question_prompt||'').slice(0,90);
    if(question.question_id===APP.questionState.selectedQuestionId)option.selected=true;
    select.appendChild(option);
  }
  select.addEventListener('change',()=>{
    APP.questionState.selectedQuestionId=select.value;
    render();
  });
  picker.appendChild(select);
  container.appendChild(picker);

  const questionId=APP.questionState.selectedQuestionId;
  const meta=getQuestionMeta(questionId);
  const questionType=String(getEffectiveQuestionType(questionId)||((meta||{}).question_type||''));
  const metaLine=E('p','small',(meta?String(meta.section_id):'')+' | '+questionType);
  container.appendChild(metaLine);
  if(meta&&meta.question_prompt)container.appendChild(E('p','',String(meta.question_prompt)));

  if(STRUCTURED_TYPES.has(questionType)){
    const summary=computeQuestionDistribution(questionId);
    if(!summary.length){
      container.appendChild(E('div','empty','No answer distribution for selected filters.'));
      return;
    }
    const metric=E('div','metric');
    metric.appendChild(E('span','label','Answered Respondents'));
    metric.appendChild(E('span','value',String(summary[0].answered_respondent_total||0)));
    container.appendChild(metric);
    container.appendChild(E('p','small','Percentages are calculated against the answered-respondent total for this question.'));

    const primaryChart=E('div','');
    rStructuredDualAxisChart(primaryChart,summary,'Response Count by Answer Option');
    container.appendChild(primaryChart);

    container.appendChild(E('h3','','Answer Summary Table'));
    const tableWrap=E('div','');
    rTable(tableWrap,summary,[
      {key:'answer_value',label:'Answer'},
      {key:'response_count',label:'Response Count'},
      {key:'respondent_count',label:'Respondents'},
      {key:'percentage',label:'Percentage'}
    ]);
    container.appendChild(tableWrap);

    container.appendChild(E('h3','','Alternative Biomedical Chart Views'));
    const chartHost=E('div','');
    const chartBody=E('div','');
    const repaint=()=>{
      chartBody.innerHTML='';
      rAlternativeChart(chartBody,summary,'answer_value','response_count',APP.questionState.chartMode,'count');
    };
    rChartModeTabs(chartHost,APP.questionState.chartMode,(mode)=>{APP.questionState.chartMode=mode;render();});
    chartHost.appendChild(chartBody);
    container.appendChild(chartHost);
    repaint();
    return;
  }

  const themes=getTextThemes(questionId,12);
  container.appendChild(E('h3','','Masked Theme Cloud'));
  const cloud=E('div','');
  rWordCloud(cloud,themes,'Masked Theme Cloud');
  container.appendChild(cloud);

  container.appendChild(E('h3','','Theme Summary Table'));
  const themeTable=E('div','');
  rTable(themeTable,themes,[{key:'theme',label:'Theme'},{key:'count',label:'Count'}]);
  container.appendChild(themeTable);

  container.appendChild(E('h3','','Alternative Biomedical Chart Views'));
  const chartHost=E('div','');
  const chartBody=E('div','');
  rChartModeTabs(chartHost,APP.questionState.chartMode,(mode)=>{APP.questionState.chartMode=mode;render();});
  chartHost.appendChild(chartBody);
  container.appendChild(chartHost);
  rAlternativeChart(chartBody,themes,'theme','count',APP.questionState.chartMode,'count');

  container.appendChild(E('h3','','Masked Text Responses'));
  const responsesWrap=E('div','');
  rTextResponses(responsesWrap,getMaskedTextResponses(questionId));
  container.appendChild(responsesWrap);
};

const rView=(container)=>{
  if(APP.view==='heat'){
    container.appendChild(E('h2','','Section Heatmap'));
    const heatWrap=E('div','');
    rHeat(heatWrap,computeSectionHeatmap());
    container.appendChild(heatWrap);
    container.appendChild(E('p','small','Heatmap shows answered percentage by section and country ISO.'));
    return;
  }
  if(APP.view==='section'){
    container.appendChild(E('h2','','Section Summary'));
    const tableWrap=E('div','');
    rTable(tableWrap,sectionRows(),[
      {key:'question_id',label:'Question ID'},
      {key:'section_id',label:'Section'},
      {key:'question_type',label:'Type'},
      {key:'countries_answered',label:'Countries Answered'},
      {key:'answered_pct',label:'Answered %'},
      {key:'country_iso_list',label:'Country List'}
    ]);
    container.appendChild(tableWrap);
    return;
  }
  if(APP.view==='question'){
    rQuestionView(container);
    return;
  }
  if(APP.view==='compare'){
    container.appendChild(E('h2','','Country Comparison'));
    const questions=getQuestions();
    if(!questions.length){
      container.appendChild(E('div','empty','No questions available.'));
      return;
    }
    const picker=E('div','');
    picker.style.marginBottom='10px';
    picker.appendChild(E('label','','Question'));
    const select=document.createElement('select');
    for(const question of questions){
      const option=document.createElement('option');
      option.value=question.question_id;
      option.textContent=question.question_id+' ['+question.section_id+'] '+String(question.question_prompt||'').slice(0,90);
      select.appendChild(option);
    }
    picker.appendChild(select);
    container.appendChild(picker);

    const distributionHost=E('div','');
    const deltaHost=E('div','');
    container.appendChild(distributionHost);
    container.appendChild(deltaHost);
    const refresh=()=>{
      const distribution=getQuestionCountryDistribution(select.value);
      distributionHost.innerHTML='';
      rTable(distributionHost,distribution,[
        {key:'country_iso',label:'Country'},
        {key:'answer_value',label:'Answer'},
        {key:'respondent_count',label:'Count'},
        {key:'percentage',label:'%'}
      ]);
      deltaHost.innerHTML='';
      deltaHost.appendChild(E('h3','','Largest Differences (Delta pp)'));
      const deltaTable=E('div','');
      rTable(deltaTable,getCountryDeltas(distribution,10),[
        {key:'answer_value',label:'Answer'},
        {key:'delta_pp',label:'Delta (pp)'},
        {key:'max_country',label:'Max Country'},
        {key:'min_country',label:'Min Country'}
      ]);
      deltaHost.appendChild(deltaTable);
    };
    select.addEventListener('change',refresh);
    refresh();
  }
};

const main=()=>{
  const panel=E('section','main');
  const hero=E('div','card panel');
  hero.appendChild(E('h1','title','CANDLE NCDN Biomedical Data Dashboard'));
  hero.appendChild(E('p','sub','Single-file offline analytics for national cancer data node planning.'));
  hero.appendChild(E('div','warn','Data sensitivity notice: respondent-level normalized rows are embedded. Names/emails are excluded and open text is masked.'));
  panel.appendChild(hero);

  const kpiCard=E('div','card');
  const kpiGrid=E('div','kpis');
  const values=kpis();
  for(const [label,value] of [['Respondents',values.respondents],['Countries',values.countries],['Questions',values.questions],['Answered Rows',values.answeredRows]]){
    const item=E('div','k');
    item.appendChild(E('div','l',label));
    item.appendChild(E('div','v',String(value)));
    kpiGrid.appendChild(item);
  }
  kpiCard.appendChild(kpiGrid);
  panel.appendChild(kpiCard);

  const tabsCard=E('div','card');
  const tabs=E('div','tabs');
  for(const [id,label] of VIEWS){
    const button=E('button','tab',label);
    button.setAttribute('aria-pressed',APP.view===id?'true':'false');
    button.addEventListener('click',()=>{APP.view=id;render();});
    tabs.appendChild(button);
  }
  tabsCard.appendChild(tabs);
  panel.appendChild(tabsCard);

  const viewCard=E('div','card panel');
  rView(viewCard);
  panel.appendChild(viewCard);
  return panel;
};

const render=()=>{
  const root=document.getElementById('app-root');
  root.innerHTML='';
  const shell=E('div','shell');
  shell.appendChild(side());
  shell.appendChild(main());
  root.appendChild(shell);
};

const boot=()=>{
  const root=document.getElementById('app-root');
  if(!root)return;
  try{
    APP.raw=decode();
    render();
  }catch(error){
    root.innerHTML='';
    const card=E('div','card panel');
    card.appendChild(E('h2','','Static Dashboard Error'));
    card.appendChild(E('p','',String(error&&error.message?error.message:error)));
    root.appendChild(card);
  }
};
boot();
})();
"""
