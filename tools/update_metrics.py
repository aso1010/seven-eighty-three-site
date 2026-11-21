#!/usr/bin/env python3
"""Refresh measured source byte counts without compiling the static site."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
def fill(s,attribute,key,value):
    return re.sub(r'(<span '+attribute+'="'+key+r'">).*?(</span>)',lambda m:m[1]+str(value)+m[2],s)
p=R/'work/index.html';s=p.read_text()
for key,name in [('home','index.html'),('styles','styles.css'),('opening','opening.css')]:s=fill(s,'data-source-metric',key,(R/name).stat().st_size)
p.write_text(s)
p=R/'case-study/index.html';s=p.read_text();g=json.loads((R/'schema.json').read_text())
for key,value in [('styles',(R/'styles.css').stat().st_size),('script',(R/'site.js').stat().st_size),('graph',len(g['@graph']))]:s=fill(s,'data-case-metric',key,value)
for _ in range(10):
    updated=fill(s,'data-case-metric','document',len(s.encode()))
    if updated==s:break
    s=updated
p.write_text(s)
p=R/'site.json';data=json.loads(p.read_text());data["thesis"]="We found and compile sovereign companies from a founder's worldview and domain intelligence.";data['protocol']='Tier 01 and Tier 02 company builds, acquisition, and enterprise licensing. Each build starts with a 60-minute narrative extraction session. Scope, rights, timelines, and terms are agreed before work starts.';data['entities']=data['portfolio'];data['case_study']['metrics'].update(document_bytes=len(s.encode()),shared_css_bytes=(R/'styles.css').stat().st_size,native_navigation_script_bytes=(R/'site.js').stat().st_size,graph_nodes=len(g['@graph']));p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Updated measured source metrics. Homepage:',(R/'index.html').stat().st_size,'bytes.')
