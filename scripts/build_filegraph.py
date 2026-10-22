#!/usr/bin/env python3
"""
build_filegraph.py — render EVERY file in the repo as a node.

Companion to build_graph.py (which renders only the note series).
Imports its scanner so there is one definition of what an edge is.

Edge kinds, all measured, none invented (counts: run it; the page prints the numbers it draws):
    contains   directory holds file
    sibling    same note number, different file     (note <-> figure <-> script)
    builds_on  note header citation
    links_to   a markdown or [[wiki]] link in a .md file that resolves to a file in the graph

The page is interactive: tap a node for its details, a link to the file on GitHub, and its neighbours; search by
name; switch edge kinds on and off. On load it compares itself with GitHub's file list and says how stale it is.

Renders with additive-glow compositing on canvas 2D: no WebGL, no CDN, no
backdrop-filter. Works offline, survives Adreno, runs on the S25.

    python scripts/build_filegraph.py --out file-graph.html   # the site page
    python scripts/build_filegraph.py --selftest              # anti-vacuity gate
    python scripts/build_filegraph.py --verify file-graph.html  # the page's numbers equal the data it draws
"""

import argparse
import datetime
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_graph import scan_files  # noqa: E402  — single source of edge truth


def selftest():
    """The instrument must be able to report an empty graph."""
    print("=" * 62)
    print("build_filegraph.py — ANTI-VACUITY SELF-TEST")
    print("=" * 62)
    ok = total = 0

    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as d:
        # Case 1: empty repo -> 0 files, 0 edges
        total += 1
        p = scan_files(d)
        if p["stats"]["files"] == 0 and p["stats"]["edges"] == 0:
            print("[PASS] empty repo: 0 files, 0 edges")
            ok += 1
        else:
            print(f"[FAIL] empty repo: {p['stats']}")

        # Case 2: two unrelated files -> containment only, no siblings
        os.makedirs(os.path.join(d, "a"))
        open(os.path.join(d, "a", "alpha.txt"), "w").write("x")
        open(os.path.join(d, "a", "beta.txt"), "w").write("y")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 0 and p["stats"]["builds_on"] == 0:
            print(f"[PASS] unrelated files: 0 sibling, 0 builds_on "
                  f"({p['stats']['contains']} contains)")
            ok += 1
        else:
            print(f"[FAIL] unrelated files invented edges: {p['stats']}")

        # Case 3: matched note number across dirs -> exactly 1 sibling edge
        os.makedirs(os.path.join(d, "research_notes"))
        os.makedirs(os.path.join(d, "figures"))
        open(os.path.join(d, "research_notes", "077_thing.md"), "w").write(
            "# Note #077\n**Status:** Draft\n")
        open(os.path.join(d, "figures", "note077_pic.png"), "w").write("x")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 1:
            print("[PASS] note077 md + note077 png -> exactly 1 sibling edge")
            ok += 1
        else:
            print(f"[FAIL] sibling count = {p['stats']['sibling']} (expected 1)")

        # Case 4: a number that matches nothing must NOT create an edge
        open(os.path.join(d, "research_notes", "088_lonely.md"), "w").write(
            "# Note #088\n**Status:** Draft\n**Builds on:** #999 (does not exist)\n")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 1 and p["stats"]["builds_on"] == 0:
            print("[PASS] #999 does not resolve -> no phantom edge")
            ok += 1
        else:
            print(f"[FAIL] phantom edge created: {p['stats']}")

        # Case 5: markdown links. Only a link that resolves to a file in the graph makes an edge
        open(os.path.join(d, "a", "links.md"), "w").write(
            "[ok](alpha.txt) [missing](nope.md) [web](https://example.com/a.md) [anchor](#top)\n"
            "```\n[in code](beta.txt)\n```\n`[inline](beta.txt)`\n")
        total += 1
        p = scan_files(d)
        if p["stats"]["links_to"] == 1 and p["stats"]["links_unresolved"] == 1:
            print("[PASS] 1 resolving link -> 1 links_to; missing link counted unresolved; web, anchor and code ignored")
            ok += 1
        else:
            print(f"[FAIL] link edges: {p['stats']}")

        # Case 6: wikilinks. A unique name links; an ambiguous one does not guess
        os.makedirs(os.path.join(d, "b"))
        open(os.path.join(d, "b", "beta.txt"), "w").write("z")   # now two files are named beta.txt
        open(os.path.join(d, "a", "wiki.md"), "w").write("[[alpha]] [[beta]] [[ghost]]\n")
        total += 1
        p = scan_files(d)
        if p["stats"]["links_to"] == 2 and p["stats"]["links_unresolved"] == 3:
            print("[PASS] [[alpha]] links; ambiguous [[beta]] and missing [[ghost]] make no edge")
            ok += 1
        else:
            print(f"[FAIL] wikilink edges: {p['stats']}")

        # Case 7: --verify must say the other thing on a page whose counts disagree with its data
        page = os.path.join(d, "page.html")
        good = scan_files(d)
        open(page, "w").write(SHELL.replace("__DATA__", json.dumps(good)))
        bad = dict(good, stats=dict(good["stats"], edges=good["stats"]["edges"] + 380), edges=[])
        badpage = os.path.join(d, "bad.html")
        open(badpage, "w").write(SHELL.replace("__DATA__", json.dumps(bad)))
        total += 1
        if verify(page) and not verify(badpage):
            print("[PASS] --verify passes a consistent page and fails one whose counts are not drawn")
            ok += 1
        else:
            print("[FAIL] --verify did not separate the consistent and inconsistent pages")

    print()
    print(f"RESULT: {ok}/{total} checks passed")
    print("=" * 62)
    return ok == total


SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<!-- principia-graph-generated: written by scripts/build_filegraph.py; edit the script, not this file -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Principia Artificialis — File Graph</title>
<style>
  :root{
    --void:#05070C; --panel:#0C1119; --rule:#1A2431; --text:#D6E2F0;
    --dim:#7288A3; --faint:#55667D; --hot:#FFB454; --link:#78AAFF;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    --serif:Georgia,"Iowan Old Style",serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:var(--void);color:var(--text);
    font-family:var(--mono);overflow:hidden;-webkit-text-size-adjust:100%}
  canvas{display:block;width:100vw;height:100vh;touch-action:none;cursor:grab}
  canvas.drag{cursor:grabbing}
  a{color:var(--link)}
  button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;text-align:left}
  .panel{position:fixed;background:rgba(12,17,25,.95);border:1px solid var(--rule)}

  #hud{top:0;left:0;bottom:0;width:280px;border-width:0 1px 0 0;
    padding:18px 16px;overflow-y:auto;z-index:10}
  #hud h1{font-family:var(--serif);font-size:19px;font-weight:400;line-height:1.15}
  #hud h1 em{font-style:italic;color:var(--dim);display:block;font-size:15px}
  #hud h1 a{color:inherit;text-decoration:none}
  .stamp{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin:6px 0 14px}
  #hudToggle{display:none;position:absolute;top:14px;right:12px;font-size:11px;color:var(--dim);
    border:1px solid var(--rule);padding:3px 8px}

  .hero{border-left:2px solid var(--hot);padding:10px 12px;background:rgba(255,180,84,.05);margin-bottom:16px}
  .hero .n{font-family:var(--serif);font-size:30px;line-height:1;color:var(--hot);font-variant-numeric:tabular-nums}
  .hero .l{font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-top:4px;line-height:1.5}

  .sec{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--faint);
    padding-bottom:6px;margin:0 0 8px;border-bottom:1px solid var(--rule)}
  .grp{margin-bottom:16px}
  .r{display:flex;justify-content:space-between;align-items:center;font-size:11.5px;padding:2.5px 0;color:var(--dim)}
  .r b{color:var(--text);font-weight:500;font-variant-numeric:tabular-nums}
  .r label{display:flex;align-items:center;gap:7px;cursor:pointer}
  .sw{width:14px;height:2px;display:inline-block}
  .k{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--dim);padding:2px 0}
  .d{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 7px currentColor}
  .note{font-size:10.5px;line-height:1.55;color:var(--dim)}

  #q{width:100%;background:#070B12;border:1px solid var(--rule);color:var(--text);
    font:inherit;font-size:12px;padding:7px 8px;outline:none}
  #q:focus{border-color:var(--dim)}
  #qr button,.nb button{display:block;width:100%;font-size:11px;padding:4px 2px;color:var(--text);
    border-bottom:1px solid rgba(26,36,49,.6);word-break:break-all}
  #qr button:hover,.nb button:hover{color:var(--hot)}
  #live{font-size:10.5px;line-height:1.55;color:var(--dim)}
  #live.warn{color:var(--hot)}

  #det{top:0;right:0;bottom:0;width:380px;border-width:0 0 0 1px;padding:16px;overflow-y:auto;
    z-index:20;display:none}
  #det .p{font-size:9.5px;letter-spacing:.06em;color:var(--faint);word-break:break-all}
  #det h2{font-family:var(--serif);font-size:17px;font-weight:400;line-height:1.25;margin:5px 0 6px;word-break:break-word}
  #det .m{font-size:11px;color:var(--dim);line-height:1.55;margin-bottom:10px}
  #det .acts{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
  #det .acts a,#det .acts button{font-size:11px;border:1px solid var(--rule);padding:5px 9px;text-decoration:none;color:var(--text)}
  #det .acts a.primary{border-color:var(--hot);color:var(--hot)}
  #det .x{position:absolute;top:10px;right:12px;font-size:16px;color:var(--dim)}
  .nb{margin-bottom:12px}
  .nb .h{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-bottom:3px}
  #pv{border-top:1px solid var(--rule);padding-top:10px}
  #pv pre{font-size:10.5px;line-height:1.5;white-space:pre-wrap;word-break:break-word;color:#B9C8DA}
  #pv img{max-width:100%;background:#fff}
  #pv .s{font-size:10px;color:var(--faint);margin-bottom:6px}

  #tip{display:none;max-width:290px;padding:10px 12px;z-index:30;pointer-events:none}
  #tip .p{font-size:9px;letter-spacing:.06em;color:var(--faint);word-break:break-all}
  #tip .t{font-family:var(--serif);font-size:14px;line-height:1.3;margin-top:3px;word-break:break-word}

  #bar{position:fixed;left:280px;right:0;bottom:0;padding:8px 16px;font-size:10px;color:var(--faint);
    letter-spacing:.04em;z-index:5;background:linear-gradient(transparent,var(--void) 65%)}
  @media(max-width:760px){
    #hud{width:100%;bottom:auto;max-height:46vh;border-width:0 0 1px 0}
    #hud.min{max-height:122px;overflow:hidden}
    #hud.min.searching{max-height:46vh;overflow-y:auto}
    #hudToggle{display:block}
    #det{top:auto;left:0;width:100%;height:50vh;border-width:1px 0 0 0}
    #bar{left:0}
  }
</style>
</head>
<body>
<canvas id="c" aria-label="3D graph of every file in the repository"></canvas>

<aside class="panel" id="hud">
  <button id="hudToggle" type="button">less</button>
  <h1><a href="./">File Graph<em>Principia Artificialis</em></a></h1>
  <div class="stamp" id="stamp"></div>

  <div class="grp">
    <input id="q" type="search" placeholder="Find a file… (/)" autocomplete="off" aria-label="Find a file">
    <div id="qr"></div>
  </div>

  <div class="hero">
    <div class="n" id="hE">—</div>
    <div class="l">edges drawn, all measured<br>counted from the drawn data</div>
  </div>

  <div class="grp">
    <div class="sec">Nodes</div>
    <div class="r"><span>files</span><b id="sF">—</b></div>
    <div class="r"><span>directories</span><b id="sD">—</b></div>
  </div>

  <div class="grp">
    <div class="sec">Edges · tap to show or hide</div>
    <div class="r"><label><input type="checkbox" data-k="contains" checked><span class="sw" style="background:rgb(70,92,124)"></span>folder holds</label><b id="eC">—</b></div>
    <div class="r"><label><input type="checkbox" data-k="sibling" checked><span class="sw" style="background:rgb(199,125,214)"></span>same note number</label><b id="eS">—</b></div>
    <div class="r"><label><input type="checkbox" data-k="builds_on" checked><span class="sw" style="background:rgb(79,214,184)"></span>builds on</label><b id="eB">—</b></div>
    <div class="r"><label><input type="checkbox" data-k="links_to" checked><span class="sw" style="background:rgb(120,170,255)"></span>links to</label><b id="eL">—</b></div>
    <div class="note" id="unres"></div>
  </div>

  <div class="grp">
    <div class="sec">Live check against GitHub</div>
    <div id="live">checking…</div>
  </div>

  <div class="grp">
    <div class="sec">Legend</div>
    <div id="leg"></div>
  </div>

  <div class="grp">
    <div class="sec">Reading it</div>
    <p class="note">Every tracked file is a dot. Tap one to read it here, see what it connects to, and open it on
    GitHub; tap it again to go straight to GitHub. An amber ring marks a note whose registered claim failed and was
    kept. Lines are only relations found in the files: a folder holding a file, a shared note number, a
    "Builds on" header, or a link written in a note. None is inferred.</p>
  </div>
</aside>

<aside class="panel" id="det" aria-live="polite">
  <button class="x" id="detX" type="button" aria-label="Close">×</button>
  <div class="p" id="dP"></div>
  <h2 id="dT"></h2>
  <div class="m" id="dM"></div>
  <div class="acts" id="dA"></div>
  <div id="dN"></div>
  <div id="pv"></div>
</aside>

<div class="panel" id="tip"><div class="p" id="tp"></div><div class="t" id="tt"></div></div>

<div id="bar">drag to orbit · pinch or scroll to zoom · tap a dot to open it · esc to clear</div>

<script id="D" type="application/json">__DATA__</script>
<script>
(function(){
"use strict";
var D=JSON.parse(document.getElementById('D').textContent);
var REPO=D.repo,BR=D.branch||'main';
function $(i){return document.getElementById(i);}
function T(i,v){var e=$(i);if(e)e.textContent=v;}
function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e;}
function encPath(p){return p.split('/').map(encodeURIComponent).join('/');}
function ghUrl(n){if(n.id==='/')return REPO;return REPO+(n.kind==='dir'?'/tree/':'/blob/')+BR+'/'+encPath(n.id);}
function rawUrl(n){return 'https://raw.githubusercontent.com/'+REPO.replace('https://github.com/','')+'/'+BR+'/'+encPath(n.id);}

var COL={dir:'#5B7FA8',doc:'#8FA8C4',code:'#4FD6B8',figure:'#C77DD6',
         data:'#E0C060',proof:'#FF7B6B',build:'#6B7C93',other:'#5A6B82',
         refuted:'#FFB454',verified:'#4FD6B8',draft:'#8FA8C4',
         speculative:'#6A7E9B',unlabeled:'#5A6B82'};
var ECOL={contains:'70,92,124',sibling:'199,125,214',builds_on:'79,214,184',links_to:'120,170,255'};
var LEG=[['dir','directory'],['doc','markdown'],['code','python / shell'],
         ['figure','figure'],['data','data + logs'],['other','other'],['refuted','refuted, kept']];
LEG.forEach(function(p){var d=el('div','k');var s=el('span','d');s.style.background=COL[p[0]];s.style.color=COL[p[0]];
  d.appendChild(s);d.appendChild(document.createTextNode(p[1]));$('leg').appendChild(d);});

var N=D.nodes.map(function(n){return Object.assign({},n);});
var ix={};N.forEach(function(n,i){ix[n.id]=i;});
var E=D.edges.filter(function(e){return ix[e.source]!==undefined&&ix[e.target]!==undefined;})
             .map(function(e){return {s:ix[e.source],t:ix[e.target],k:e.kind};});

// Every number shown is counted from what is drawn, never copied from a stored total.
var cnt={contains:0,sibling:0,builds_on:0,links_to:0};E.forEach(function(e){cnt[e.k]=(cnt[e.k]||0)+1;});
var nFiles=N.filter(function(n){return n.kind!=='dir';}).length,nDirs=N.length-nFiles;
T('stamp',(D.generated||''));T('hE',E.length);T('sF',nFiles);T('sD',nDirs);
T('eC',cnt.contains);T('eS',cnt.sibling);T('eB',cnt.builds_on);T('eL',cnt.links_to);
T('unres',(D.stats.links_unresolved||0)+' written link'+(D.stats.links_unresolved===1?'':'s')+' point at nothing in the repo and draw no line.');

var adj=N.map(function(){return [];});
E.forEach(function(e){adj[e.s].push({j:e.t,k:e.k,out:true});adj[e.t].push({j:e.s,k:e.k,out:false});});
N.forEach(function(n,i){n.deg=adj[i].length;});

var vis={contains:true,sibling:true,builds_on:true,links_to:true};
document.querySelectorAll('input[data-k]').forEach(function(cb){
  cb.addEventListener('change',function(){vis[cb.getAttribute('data-k')]=cb.checked;paint();});});

var _s=1337;function rnd(){_s=(_s*1103515245+12345)&0x7fffffff;return _s/0x7fffffff;}
N.forEach(function(n){
  var u=rnd()*2-1,th=rnd()*6.2832,r=190*Math.cbrt(rnd())+40,s=Math.sqrt(1-u*u);
  n.x=r*s*Math.cos(th);n.y=r*s*Math.sin(th);n.z=r*u;n.vx=n.vy=n.vz=0;
  n.m=n.kind==='dir'?3.2:1;
  n.rad=n.kind==='dir'?3.4:(1.5+Math.min(3.2,Math.log(1+n.bytes/900)));
  n.col=COL[n.cls]||COL[n.kind]||COL.other;
});

var cv=$('c'),cx=cv.getContext('2d'),DPR=1;
function fit(){DPR=Math.min(devicePixelRatio||1,2);cv.width=Math.round(cv.clientWidth*DPR);cv.height=Math.round(cv.clientHeight*DPR);}
addEventListener('resize',function(){fit();paint();});fit();

var rotY=0.4,rotX=-0.22,zoom=innerWidth<760?0.9:1.5,alpha=1,auto=true;
var F={x:0,y:0,z:0},FT={x:0,y:0,z:0},follow=-1;   // follow: keep this node centred while the layout settles

function tick(){
  if(alpha<0.0025)return false;
  alpha*=0.986;
  var i,j,a,b,dx,dy,dz,d2,d,f,u;
  for(i=0;i<N.length;i++){a=N[i];
    for(j=i+1;j<N.length;j++){b=N[j];dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;d2=dx*dx+dy*dy+dz*dz;
      if(d2<1e-4){dx=rnd()-.5;dy=rnd()-.5;dz=rnd()-.5;d2=1e-4;}
      if(d2>250000)continue;
      d=Math.sqrt(d2);f=900*a.m*b.m/d2/d;
      a.vx-=dx*f;a.vy-=dy*f;a.vz-=dz*f;b.vx+=dx*f;b.vy+=dy*f;b.vz+=dz*f;}}
  for(i=0;i<E.length;i++){a=N[E[i].s];b=N[E[i].t];
    dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;d=Math.sqrt(dx*dx+dy*dy+dz*dz)||1e-4;
    u=E[i].k==='contains'?46:(E[i].k==='sibling'?26:70);
    f=(d-u)*(E[i].k==='sibling'?0.030:(E[i].k==='contains'?0.016:0.006))/d;
    a.vx+=dx*f;a.vy+=dy*f;a.vz+=dz*f;b.vx-=dx*f;b.vy-=dy*f;b.vz-=dz*f;}
  for(i=0;i<N.length;i++){a=N[i];
    a.vx-=a.x*0.0075;a.vy-=a.y*0.0075;a.vz-=a.z*0.0075;
    a.x+=a.vx*alpha*1.7;a.y+=a.vy*alpha*1.7;a.z+=a.vz*alpha*1.7;
    a.vx*=0.80;a.vy*=0.80;a.vz*=0.80;}
  return true;
}

var W,H,CXp,CYp;
function proj(n){
  var X=n.x-F.x,Y=n.y-F.y,Z=n.z-F.z;
  var cy=Math.cos(rotY),sy=Math.sin(rotY),cxr=Math.cos(rotX),sxr=Math.sin(rotX);
  var x=X*cy-Z*sy,z=X*sy+Z*cy,y=Y*cxr-z*sxr;z=Y*sxr+z*cxr;
  var p=760/(760+z+420);n.px=CXp+x*p*zoom;n.py=CYp+y*p*zoom;n.pz=z;n.pp=p;
}

var sel=-1,near={},hov=null;
function paint(){
  W=cv.clientWidth;H=cv.clientHeight;
  var wide=W>760,detOpen=sel>=0;
  CXp=wide?(280+(W-280-(detOpen?380:0))/2):W/2;
  var top=$('hud').offsetHeight;
  CYp=wide?H/2:(detOpen?(top+H*0.5)/2:(top+H)/2);
  cx.setTransform(DPR,0,0,DPR,0,0);cx.globalCompositeOperation='source-over';
  var g=cx.createRadialGradient(CXp,CYp,0,CXp,CYp,Math.max(W,H)*.78);
  g.addColorStop(0,'#0B1220');g.addColorStop(1,'#05070C');cx.fillStyle=g;cx.fillRect(0,0,W,H);
  var i,n,r,dep;
  for(i=0;i<N.length;i++)proj(N[i]);

  cx.globalCompositeOperation='lighter';
  for(i=0;i<E.length;i++){var e=E[i];if(!vis[e.k])continue;
    var a=N[e.s],b=N[e.t];dep=Math.max(.08,Math.min(1,(a.pp+b.pp)/2));
    var o=(e.k==='contains'?.16:(e.k==='sibling'?.40:.34))*dep,w=(e.k==='contains'?.6:1.05)*dep;
    if(sel>=0){if(e.s===sel||e.t===sel){o=Math.min(1,o*2.6+.25);w*=1.8;}else o*=.18;}
    cx.strokeStyle='rgba('+ECOL[e.k]+','+o.toFixed(3)+')';cx.lineWidth=w;
    cx.beginPath();cx.moveTo(a.px,a.py);cx.lineTo(b.px,b.py);cx.stroke();}

  var ord=N.map(function(_,k){return k;}).sort(function(p,q){return N[q].pz-N[p].pz;});
  for(i=0;i<ord.length;i++){n=N[ord[i]];
    var fade=(sel<0||ord[i]===sel||near[ord[i]])?1:.22;
    r=Math.max(.7,n.rad*n.pp*zoom);dep=Math.max(.1,Math.min(1,n.pp))*fade;
    var gr=cx.createRadialGradient(n.px,n.py,0,n.px,n.py,r*7);
    gr.addColorStop(0,hex(n.col,.62*dep));gr.addColorStop(.35,hex(n.col,.14*dep));gr.addColorStop(1,hex(n.col,0));
    cx.fillStyle=gr;cx.beginPath();cx.arc(n.px,n.py,r*7,0,6.2832);cx.fill();}
  cx.globalCompositeOperation='source-over';
  for(i=0;i<ord.length;i++){n=N[ord[i]];
    var fd=(sel<0||ord[i]===sel||near[ord[i]])?1:.25;
    r=Math.max(.7,n.rad*n.pp*zoom);dep=Math.max(.15,Math.min(1,n.pp));
    cx.fillStyle=hex(n.col,(.55+.45*dep)*fd);cx.beginPath();cx.arc(n.px,n.py,r,0,6.2832);cx.fill();
    if(n.cls==='refuted'){cx.strokeStyle='rgba(255,180,84,'+(.72*fd).toFixed(2)+')';cx.lineWidth=1.25;
      cx.beginPath();cx.arc(n.px,n.py,r+3.4,0,6.2832);cx.stroke();}
    if(ord[i]===sel||n===hov){cx.strokeStyle='rgba(214,226,240,.95)';cx.lineWidth=1.3;
      cx.beginPath();cx.arc(n.px,n.py,r+6,0,6.2832);cx.stroke();}}

  cx.font='500 10px '+getComputedStyle(document.body).fontFamily;cx.textAlign='center';
  for(i=0;i<N.length;i++){n=N[i];
    var show=(sel<0&&n.kind==='dir'&&n.pp>.62&&zoom>.75)||i===sel||(sel>=0&&near[i]&&n.pp>.5);
    if(show){cx.fillStyle=i===sel?'rgba(214,226,240,.95)':'rgba(114,136,163,'+Math.min(.85,n.pp).toFixed(2)+')';
      cx.fillText(n.label,n.px,n.py-n.rad*n.pp*zoom-7);}}
}
function hex(h,a){var n=parseInt(h.slice(1),16);return 'rgba('+(n>>16)+','+((n>>8)&255)+','+(n&255)+','+a.toFixed(3)+')';}

function pick(mx,my){var best=-1,bd=1e9;
  for(var i=0;i<N.length;i++){var n=N[i],dx=n.px-mx,dy=n.py-my,d=dx*dx+dy*dy;
    if(sel>=0&&i!==sel&&!near[i])d*=4;          // prefer what is lit
    var rr=Math.max(9,n.rad*n.pp*zoom+8);rr*=rr;if(d<rr&&d<bd){bd=d;best=i;}}
  return best;}

// ---------- details panel ----------
var REL={contains:['in folder','contains'],sibling:['same note number','same note number'],
         builds_on:['builds on','built on by'],links_to:['links to','linked from']};
var TEXT=/\.(md|py|sh|txt|json|jsonl|csv|tsv|yml|yaml|toml|cfg|ini|thy|bib|cff|mmd|tex|js|css|html|go|rs|c|h|log|sha256|sha256sums)$|(^|\/)(Makefile|LICENSE|SHA256SUMS|CITATION\.cff)$/i;
var IMG=/\.(png|gif|jpe?g|svg|webp)$/i;
var pvTok=0;
function select(i,center){
  sel=i;near={};var n=N[i];
  if(innerWidth<760){var hd=$('hud');hd.classList.add('min');hd.classList.remove('searching');
    $('hudToggle').textContent='more';q.blur();}
  adj[i].forEach(function(a){near[a.j]=true;});
  $('det').style.display='block';
  T('dP',n.id==='/'?'repository root':n.id);T('dT',n.label);
  var kb=n.bytes>=1024?(n.bytes/1024).toFixed(1)+' KB':n.bytes+' B';
  T('dM',(n.status?n.status.replace(/\*\*/g,'')+' · ':'')+(n.kind==='dir'?'directory':n.kind+' · '+kb)+' · '+n.deg+' connection'+(n.deg===1?'':'s'));
  var A=$('dA');A.textContent='';
  var o=el('a','primary','Open on GitHub ↗');o.href=ghUrl(n);o.target='_blank';o.rel='noopener';A.appendChild(o);
  if(n.kind!=='dir'){var rw=el('a','','Raw ↗');rw.href=rawUrl(n);rw.target='_blank';rw.rel='noopener';A.appendChild(rw);}
  var NB=$('dN');NB.textContent='';
  var groups={};
  adj[i].forEach(function(a){var lab=REL[a.k][a.k==='contains'?(a.out?1:0):(a.out?0:1)];
    (groups[lab]=groups[lab]||[]).push(a.j);});
  Object.keys(groups).forEach(function(lab){
    var box=el('div','nb');box.appendChild(el('div','h',lab+' · '+groups[lab].length));
    groups[lab].sort(function(p,q){return N[p].id<N[q].id?-1:1;}).slice(0,80).forEach(function(j){
      var b=el('button','',N[j].id==='/'?'(root)':N[j].id);b.type='button';
      b.addEventListener('click',function(){select(j,true);});box.appendChild(b);});
    if(groups[lab].length>80)box.appendChild(el('div','h','+'+(groups[lab].length-80)+' more'));
    NB.appendChild(box);});
  preview(n);
  follow=center?i:-1;if(center)auto=false;
  try{history.replaceState(null,'','#'+encodeURIComponent(n.id));}catch(e){}
  kick();
}
function clearSel(){sel=-1;near={};follow=-1;$('det').style.display='none';FT={x:0,y:0,z:0};
  try{history.replaceState(null,'',location.pathname+location.search);}catch(e){}kick();}
$('detX').addEventListener('click',clearSel);

function preview(n){
  var pv=$('pv');pv.textContent='';var tok=++pvTok;
  if(n.kind==='dir'){pv.appendChild(el('div','s','A folder: its files are listed above under "contains".'));return;}
  if(IMG.test(n.id)){pv.appendChild(el('div','s','Current version on GitHub main'));
    var im=document.createElement('img');im.alt=n.label;im.loading='lazy';im.src=rawUrl(n);
    im.onerror=function(){if(tok===pvTok){pv.textContent='';pv.appendChild(el('div','s','Could not load the image (offline, or not on GitHub main yet).'));}};
    pv.appendChild(im);return;}
  if(!TEXT.test(n.id)){pv.appendChild(el('div','s','No preview for this file type. Use "Open on GitHub".'));return;}
  if(n.bytes>400000){pv.appendChild(el('div','s','Large file ('+Math.round(n.bytes/1024)+' KB): open it on GitHub.'));return;}
  pv.appendChild(el('div','s','Loading the current version from GitHub main…'));
  fetch(rawUrl(n)).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.text();}).then(function(t){
    if(tok!==pvTok)return;pv.textContent='';
    var lines=t.split('\n'),cut=lines.length>500;
    pv.appendChild(el('div','s','Current version on GitHub main'+(cut?' · first 500 of '+lines.length+' lines':'')));
    pv.appendChild(el('pre','',cut?lines.slice(0,500).join('\n'):t));
  }).catch(function(err){if(tok!==pvTok)return;pv.textContent='';
    pv.appendChild(el('div','s','Could not load a preview ('+err.message+'; offline, or not on GitHub main yet). "Open on GitHub" still works.'));});
}

// ---------- search ----------
var q=$('q'),qr=$('qr');
function search(){var s=q.value.trim().toLowerCase();qr.textContent='';
  $('hud').classList.toggle('searching',!!s);if(!s)return [];
  var hits=[];for(var i=0;i<N.length;i++)if(N[i].id.toLowerCase().indexOf(s)>=0)hits.push(i);
  function rank(i){var n=N[i],b=n.label.toLowerCase();   // name starts with it, then files before folders, then notes
    return (b.indexOf(s)===0?0:4)+(n.kind==='dir'?2:0)+(/\.md$/.test(n.id)?0:1);}
  hits.sort(function(a,b){return rank(a)-rank(b)||N[a].id.length-N[b].id.length;});hits=hits.slice(0,12);
  if(!hits.length)qr.appendChild(el('div','note','No file matches.'));
  hits.forEach(function(i){var b=el('button','',N[i].id==='/'?'(root)':N[i].id);b.type='button';
    b.addEventListener('click',function(){select(i,true);});qr.appendChild(b);});
  return hits;}
q.addEventListener('input',search);
q.addEventListener('keydown',function(e){if(e.key==='Enter'){var h=search();if(h.length)select(h[0],true);}});
addEventListener('keydown',function(e){
  if(e.key==='Escape'){clearSel();q.blur();}
  else if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}});
$('hudToggle').addEventListener('click',function(){var h=$('hud');h.classList.toggle('min');
  this.textContent=h.classList.contains('min')?'more':'less';paint();});
if(innerWidth<760){$('hud').classList.add('min');$('hudToggle').textContent='more';}

// ---------- pointer ----------
var tip=$('tip');
function hoverTip(i,mx,my){
  if(i<0){tip.style.display='none';if(hov){hov=null;paint();}return;}
  hov=N[i];T('tp',hov.id==='/'?'repository root':hov.id);T('tt',hov.label);tip.style.display='block';
  var tw=tip.offsetWidth,th=tip.offsetHeight;
  tip.style.left=Math.max(6,Math.min(mx+15,innerWidth-tw-6))+'px';tip.style.top=Math.max(6,Math.min(my+15,innerHeight-th-6))+'px';paint();}
var down=false,lx=0,ly=0,mv=0,touch=false;
function pDown(x,y){down=true;lx=x;ly=y;mv=0;auto=false;cv.classList.add('drag');}
function pMove(x,y){
  if(down){rotY+=(x-lx)*0.0058;rotX+=(y-ly)*0.0058;rotX=Math.max(-1.5,Math.min(1.5,rotX));
    mv+=Math.abs(x-lx)+Math.abs(y-ly);lx=x;ly=y;paint();}
  else if(!touch)hoverTip(pick(x,y),x,y);}
function pUp(x,y){
  if(down&&mv<6){var i=pick(x,y);tip.style.display='none';
    if(i<0)clearSel();
    else if(i===sel){window.open(ghUrl(N[i]),'_blank','noopener');}   // second tap: open the file itself
    else select(i,false);}
  down=false;cv.classList.remove('drag');}
cv.addEventListener('mousedown',function(e){touch=false;pDown(e.clientX,e.clientY);});
addEventListener('mousemove',function(e){if(!touch)pMove(e.clientX,e.clientY);});
addEventListener('mouseup',function(e){if(!touch)pUp(e.clientX,e.clientY);});
var pd=0;
cv.addEventListener('touchstart',function(e){touch=true;
  if(e.touches.length===1){var t=e.touches[0];pDown(t.clientX,t.clientY);}
  else if(e.touches.length===2){down=false;pd=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);}},{passive:true});
cv.addEventListener('touchmove',function(e){
  if(e.touches.length===1){var t=e.touches[0];pMove(t.clientX,t.clientY);}
  else if(e.touches.length===2&&pd){var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
    zoom=Math.max(.25,Math.min(9,zoom*(d/pd)));pd=d;paint();}},{passive:true});
cv.addEventListener('touchend',function(e){var t=e.changedTouches[0];if(e.touches.length===0){pUp(t.clientX,t.clientY);pd=0;}},{passive:true});
cv.addEventListener('wheel',function(e){e.preventDefault();auto=false;
  zoom=Math.max(.25,Math.min(9,zoom*(e.deltaY<0?1.1:.909)));paint();},{passive:false});

// ---------- animation ----------
var slow=matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,running=false;
function step(){if(follow>=0){var fn=N[follow];FT={x:fn.x,y:fn.y,z:fn.z};}
  var dx=FT.x-F.x,dy=FT.y-F.y,dz=FT.z-F.z,moving=Math.abs(dx)+Math.abs(dy)+Math.abs(dz)>.05;
  if(slow){F.x=FT.x;F.y=FT.y;F.z=FT.z;moving=false;}else{F.x+=dx*.14;F.y+=dy*.14;F.z+=dz*.14;}
  return moving;}
function kick(){if(running)return;running=true;requestAnimationFrame(loop);}
function loop(){var live=slow?false:tick(),mv2=step();if(auto&&!slow)rotY+=0.00075;paint();
  if(live||mv2||(auto&&!slow))requestAnimationFrame(loop);else running=false;}
if(slow){for(var k=0;k<320;k++)tick();alpha=0;}
kick();

// open a file named in the address (#path), so a link can point at one file
if(location.hash.length>1){var h=decodeURIComponent(location.hash.slice(1));if(ix[h]!==undefined)select(ix[h],true);}

// ---------- live check: is this page behind GitHub? ----------
(function(){
  var live=$('live'),gen={};(D.generated_pages||[]).forEach(function(p){gen[p]=true;});
  var have={};N.forEach(function(n){if(n.kind!=='dir')have[n.id]=true;});
  var api='https://api.github.com/repos/'+REPO.replace('https://github.com/','')+'/git/trees/'+BR+'?recursive=1';
  fetch(api).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(function(j){
    var now={},added=[],removed=[];
    (j.tree||[]).forEach(function(t){if(t.type==='blob'&&!gen[t.path])now[t.path]=true;});
    Object.keys(now).forEach(function(p){if(!have[p])added.push(p);});
    Object.keys(have).forEach(function(p){if(!now[p])removed.push(p);});
    live.textContent='';
    if(!added.length&&!removed.length){live.textContent='Up to date: the '+nFiles+' files drawn are exactly the files on GitHub '+BR+' now.'+(j.truncated?' (GitHub truncated its list.)':'');return;}
    live.className='warn';
    live.appendChild(document.createTextNode('Behind GitHub '+BR+': '+added.length+' file'+(added.length===1?'':'s')+' added and '+removed.length+' removed since this page was built. Rebuild with python scripts/build_filegraph.py --out file-graph.html'));
    added.slice(0,6).forEach(function(p){var a=el('a','',' + '+p);a.href=REPO+'/blob/'+BR+'/'+encPath(p);a.target='_blank';a.rel='noopener';a.style.display='block';live.appendChild(a);});
    if(added.length>6)live.appendChild(el('div','',' … and '+(added.length-6)+' more'));
  }).catch(function(err){live.textContent='Live check unavailable ('+err.message+'; offline or GitHub rate limit). The graph shows the repository as of '+(D.generated||'its build')+'.';});
})();
})();
</script>
</body>
</html>
"""


def page_data(path):
    """The JSON a built page draws from."""
    import re
    txt = open(path, encoding="utf-8").read()
    m = re.search(r'<script id="D" type="application/json">(.*?)</script>', txt, re.S)
    if not m:
        raise ValueError("no data block")
    return txt, json.loads(m.group(1).replace("<\\/", "</"))


def verify(path):
    """A built page must carry every stored count equal to what its own data draws, and only edges between drawn
    nodes. (The page shipped on 2026-10-19 showed 380 edges and 228 files while drawing 0 edges and 18 dots.)"""
    problems = []
    try:
        txt, d = page_data(path)
    except (OSError, ValueError) as exc:
        print(f"VERIFY {path}: cannot read ({exc})")
        return False
    if "principia-graph-generated" not in txt[:4096]:
        problems.append("generated marker missing (the page would be counted as a file of its own graph)")
    ids = {n["id"] for n in d["nodes"]}
    dangling = [e for e in d["edges"] if e["source"] not in ids or e["target"] not in ids]
    if dangling:
        problems.append(f"{len(dangling)} edges reference nodes that are not drawn")
    files = sum(1 for n in d["nodes"] if n["kind"] != "dir")
    dirs = len(d["nodes"]) - files
    kinds = {}
    for e in d["edges"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    want = {"files": files, "dirs": dirs, "nodes": len(d["nodes"]), "edges": len(d["edges"]),
            "contains": kinds.get("contains", 0), "sibling": kinds.get("sibling", 0),
            "builds_on": kinds.get("builds_on", 0), "links_to": kinds.get("links_to", 0)}
    for k, v in want.items():
        if d.get("stats", {}).get(k) != v:
            problems.append(f"stats.{k} = {d.get('stats', {}).get(k)!r} but the data draws {v}")
    for p in problems:
        print(f"VERIFY {path}: {p}")
    print(f"VERIFY {path}: {'OK' if not problems else 'FAILED'} ({files} files, {dirs} dirs, {len(d['edges'])} edges)")
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify", metavar="PAGE", help="check a built page's counts against the data it draws")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="graph_files.html")
    ap.add_argument("--repo", default="https://github.com/holland202/principia-artificialis")
    ap.add_argument("--branch", default="main")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.verify:
        sys.exit(0 if verify(a.verify) else 1)

    root = os.path.abspath(a.root)
    p = scan_files(root)
    p["generated"] = "generated " + datetime.date.today().isoformat()
    p["repo"], p["branch"] = a.repo.rstrip("/"), a.branch

    data = json.dumps(p, separators=(",", ":")).replace("</", "<\\/")
    out = os.path.join(root, a.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(SHELL.replace("__DATA__", data))

    s = p["stats"]
    print("FILE GRAPH — measured")
    for k in ("files", "dirs", "nodes", "edges", "contains", "sibling", "builds_on", "links_to",
              "links_unresolved", "orphans"):
        print(f"  {k:<17}{s[k]}")
    print()
    print(f"wrote {out}  ({os.path.getsize(out)} bytes; the page fetches previews and its live check from GitHub)")
    if not verify(out):
        sys.exit(1)


if __name__ == "__main__":
    main()
