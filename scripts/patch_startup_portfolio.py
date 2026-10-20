#!/usr/bin/env python3
"""Patch live startup-portfolio HTML with CLP26 national cards + One-pager buttons."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/tmp/portfolio.html")
OUT = ROOT / "portfolio" / "startup-portfolio.html"


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source HTML at {SRC}")
    html = SRC.read_text()

    css_add = """
.onepager-btn{display:inline-flex;align-items:center;gap:3px;padding:4px 8px;background:#5a3d8a;color:#fff;border-radius:6px;text-decoration:none;font-size:9.5px;font-weight:700;transition:background .13s;flex-shrink:0}
.onepager-btn:hover{background:#7b52b8}
.ct-modal-footer{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.card-actions{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-left:auto}
"""
    html = html.replace(
        ".nexus-btn:hover{background:#669348}",
        ".nexus-btn:hover{background:#669348}" + css_add,
        1,
    )

    html = html.replace(
        "'Series B+':'Ser. B+'}}",
        "'Series B+':'Ser. B+','National':'National'}}",
    )
    html = html.replace(
        "'Series B+':'Ser. B+'}}",
        "'Series B+':'Ser. B+','National':'National'}}",
    )

    html = html.replace(
        "const STAGE_LABELS={'Pre-Seed':'Pre-Seed','Seed':'Seed','Pre-Series A':'Pre-A','Series A':'Ser. A','Series B+':'Ser. B+'};",
        "const STAGE_LABELS={'Pre-Seed':'Pre-Seed','Seed':'Seed','Pre-Series A':'Pre-A','Series A':'Ser. A','Series B+':'Ser. B+','National':'National'};",
    )

    start = html.find("function openCTModal(cardEl)")
    end = html.find("function closeCTModal", start)
    if start < 0 or end < 0:
        raise SystemExit("openCTModal block not found")
    open_modal_new = (
        'function openCTModal(cardEl){if(event.target.closest(\'a\'))return;'
        "const s=JSON.parse(decodeURIComponent(cardEl.dataset.startup));"
        "const ct1Block=s.ct1?'<div class=\"ct-modal-node\"><span class=\"ct-modal-node-label\">Primary CT Node</span><a class=\"badge bt-ct bt-ct-'+s.ct1.split(\"-\")[1].toLowerCase()+'\" href=\"'+CT_WIKI_BASE+encodeURIComponent(s.ct1)+'\" target=\"_blank\" rel=\"noopener\">'+s.ct1+' \\u00B7 '+(CT_LABELS[s.ct1]||s.ct1)+'</a></div>':'';"
        "const ct2Block=s.ct2?'<div class=\"ct-modal-node\"><span class=\"ct-modal-node-label\">Secondary CT Node</span><a class=\"badge bt-ct bt-ct-'+s.ct2.split(\"-\")[1].toLowerCase()+'\" href=\"'+CT_WIKI_BASE+encodeURIComponent(s.ct2)+'\" target=\"_blank\" rel=\"noopener\">'+s.ct2+' \\u00B7 '+(CT_LABELS[s.ct2]||s.ct2)+'</a></div>':'';"
        "const website=s.w?'<a href=\"https://'+s.w+'\" target=\"_blank\" rel=\"noopener\" class=\"site-btn\">Visit Website</a>':'';"
        "const onePager=s.slug?'<a href=\"/s/'+s.slug+'\" class=\"onepager-btn\">One-pager</a>':'';"
        'const stKey={"Pre-Seed":"PS","Seed":"S","Pre-Series A":"PSA","Series A":"SA","Series B+":"SBP","National":"NAT"}[s.st]||"PS";'
        "document.getElementById('ct-modal-content').innerHTML='<div class=\"ct-modal-header\"><span class=\"ct-modal-flag\">'+s.c+'</span><h2 class=\"ct-modal-name\">'+s.n+'</h2></div><div class=\"ct-modal-meta\"><span class=\"badge bp-'+s.p+'\">'+s.p+'</span><span class=\"badge bs-'+stKey+'\">'+(STAGE_LABELS[s.st]||s.st)+'</span></div><p class=\"ct-modal-desc\">'+(s.d||'No description available.')+'</p>'+ct1Block+ct2Block+'<div class=\"ct-modal-footer\">'+website+onePager+'</div><div class=\"ct-modal-attribution\"><small>CT nodes from the <a href=\"https://wiki.cleantechhub.net\" target=\"_blank\">LATAM Cleantech Taxonomy</a> \\u00B7 CleantechHUB 2026</small></div>';"
        "document.getElementById('ct-modal').style.display='flex';}"
    )
    html = html[:start] + open_modal_new + html[end:]

    render_card_new = r"""function renderCard(s,t){
  const flag=FLAGS[s.c]||'\u{1F30D}';
  const hasW=!!s.w;
  const desc=lang==='ES'?s.ds:s.d;
  const webBtn=hasW
    ?'<a class="site-btn" href="https://'+s.w+'" target="_blank" rel="noopener" onclick="event.stopPropagation()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg> '+t.visit+'</a>'
    :'';
  const slug=s.slug||'';
  const nexusHref=s.nexusPath||(slug?'/s/'+slug:'');
  const nexusBtn=nexusHref?'<a class="nexus-btn" href="'+nexusHref+'" onclick="event.stopPropagation()">Nexus ↗</a>':'';
  const onePagerBtn=slug?'<a class="onepager-btn" href="/s/'+slug+'" onclick="event.stopPropagation()">One-pager</a>':'';
  const epicBadge=s.epic?'<span class="epic-badge">Epic Angels</span>':'';
  const imdBadge=s.imd?'<span class="imd-badge">IMD · Perú</span>':'';
  const stk={'Pre-Seed':'PS','Seed':'S','Pre-Series A':'PSA','Series A':'SA','Series B+':'SBP','National':'NAT'}[s.st]||'PS';
  const themeBadge=s.t?'<span class="badge bt-'+s.t+'">'+t.tShort[s.t]+'</span>':'';
  const ctBadges=(s.ct1?ctBadge(s.ct1):'')+(s.ct2?ctBadge(s.ct2):'');
  const modalData=encodeURIComponent(JSON.stringify({n:s.n,p:s.p,c:FLAGS[s.c]||'\u{1F30D}',w:s.w,t:s.t,st:s.st,d:lang==='ES'?s.ds:s.d,ct1:s.ct1||'',ct2:s.ct2||'',slug:slug}));
  const actions='<div class="card-actions">'+nexusBtn+onePagerBtn+webBtn+'</div>';
  const stageLabel=(t.sShort[s.st]||s.st);
  return '<div class="card '+(hasW?'':'nw')+'" data-startup="'+modalData+'" onclick="openCTModal(this)"><div class="cb bar-'+s.p+'"></div><div class="ct"><div class="cn">'+s.n+'</div><div class="cf">'+flag+'</div></div><div class="cd">'+desc+'</div><div class="cbot">'+epicBadge+imdBadge+'<span class="badge bp-'+s.p+'">'+s.p+'</span>'+themeBadge+'<span class="badge bs-'+stk+'">'+stageLabel+'</span>'+ctBadges+actions+'</div></div>';
}"""

    rc_start = html.find("function renderCard(s,t)")
    rc_end = html.find("function toggleWeb()", rc_start)
    if rc_start < 0 or rc_end < 0:
        raise SystemExit("renderCard block not found")
    html = html[:rc_start] + render_card_new + html[rc_end:]

    clp26_block = """
let CLP26_NATIONAL_CARDS=[];
function clp26ToCard(e){
  const desc=e.desc_en||(`${e.name} — CleantechHUB portfolio startup.`);
  const descEs=e.desc_es||desc;
  return {
    slug:e.slug,n:e.name,p:normalizeProgram(e.program),c:e.country||'CO',w:e.website||'',
    t:e.theme||'',st:e.stage==='national'?'National':normalizeStage(e.stage)||'National',
    d:desc,ds:descEs,ct1:e.ct1||'',ct2:e.ct2||''
  };
}
async function loadClp26NationalCards(){
  try{
    const res=await fetch('/nexus-assets/clp26-national-shareable.json?v=20261013-clp26-ca');
    const data=await res.json();
    CLP26_NATIONAL_CARDS=(data.startups||[]).map(clp26ToCard);
  }catch(err){console.error('CLP26 national list load failed',err);CLP26_NATIONAL_CARDS=[];}
  render();
}
"""

    html = html.replace("let EPIC_CARDS=[];", "let EPIC_CARDS=[];" + clp26_block, 1)

    html = html.replace(
        "  let list=S;",
        "  let list=[...S,...CLP26_NATIONAL_CARDS];",
        1,
    )

    html = html.replace(
        "  if(webOnly) list=list.filter(s=>s.w);",
        "  if(webOnly) list=list.filter(s=>s.w||s.slug);",
        1,
    )

    html = html.replace(
        "applyUI();loadEpicCards();loadImdCards();",
        "applyUI();loadEpicCards();loadImdCards();loadClp26NationalCards();",
        1,
    )

    # bs-NAT badge style
    if ".bs-NAT" not in html:
        html = html.replace(
            ".bs-SBP{background:#e8eaf6;color:#3949ab}",
            ".bs-SBP{background:#e8eaf6;color:#3949ab}\n.bs-NAT{background:#e3f2fd;color:#1565c0}",
            1,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"Patched portfolio -> {OUT}")


if __name__ == "__main__":
    main()
