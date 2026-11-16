#!/usr/bin/env python3
"""Dependency-free validation of the published static site and canonical graph."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1] / 'seven-eighty-three-website'
ORIGIN = 'https://seveneightythree.com'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = []; self.links = []; self.assets = []; self.tags = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); self.tags.append((tag,a))
        if 'id' in a: self.ids.append(a['id'])
        if 'href' in a: self.links.append(a['href'])
        if tag in ('script','img','source') and 'src' in a: self.assets.append(a['src'])
        if tag == 'link' and a.get('rel') in ('stylesheet','icon','manifest','apple-touch-icon'): self.assets.append(a['href'])
pages = {}
for path in ROOT.rglob('*.html'):
    page = Page(); page.feed(path.read_text()); pages[path] = page
    assert len(page.ids) == len(set(page.ids)), f'Duplicate IDs: {path}'
for path,page in pages.items():
    source=path.read_text()
    for asset in page.assets:
        assert asset.startswith('/'), f'Non-local runtime asset: {path}: {asset}'
        assert (ROOT/urlsplit(asset).path.lstrip('/')).is_file(), f'Missing asset: {asset}'
    for link in page.links:
        u=urlsplit(link)
        if u.netloc and u.netloc != 'seveneightythree.com' or u.scheme not in ('','https'): continue
        if not u.path or u.path.startswith('/'):
            target = path if not u.path else ROOT / unquote(u.path).lstrip('/')
            if target.is_dir(): target /= 'index.html'
            assert target.exists(), f'Broken local link: {path}: {link}'
            if u.fragment and target.suffix=='.html':
                assert unquote(u.fragment) in pages[target].ids, f'Broken anchor: {path}: {link}'
    assert 'cz-shortcut-listen' not in source and '_files/' not in source and 'beacon.min.js' not in source
    assert source.count('href="/styles.css"') == 1
    assert source.count('src="/site.js"') == 1
    assert source.count('class="site-header"') == 1 and source.count('class="page-index"') == 1
    assert 'aria-current="page"' in source
    for endpoint in ('schema.json','site.json','llms.txt'): assert f'href="/{endpoint}"' in source
    assert re.search(r'rel="canonical" href="https://seveneightythree.com/',source)
    fonts=re.findall(r'@font-face\s*\{[^}]+\}',source)
    assert len(fonts)==2 and all('data:font/woff2;base64,' in f and 'font-display: block' in f for f in fonts)
    if path==ROOT/'index.html': font_reference=fonts
    canonical=json.loads((ROOT/'schema.json').read_text())
    inline=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
    assert inline==canonical, f'Stale embedded graph: {path}'
for path in pages:
    assert re.findall(r'@font-face\s*\{[^}]+\}',path.read_text())==font_reference
for path in ROOT.rglob('*.json'): json.loads(path.read_text())
ET.parse(ROOT/'sitemap.xml')
graph=canonical['@graph']; ids=[n['@id'] for n in graph]; assert len(ids)==len(set(ids))
org=next(n for n in graph if n['@id']==ORIGIN+'/#organization')
assert len(org['subOrganization'])==2 and 'venture foundry' in org['description']
assert not any(n.get('@type')=='Service' for n in graph)
for path in pages:
    route='/' if path==ROOT/'index.html' else '/'+str(path.parent.relative_to(ROOT))+'/'
    for fragment in ['webpage','breadcrumbs','sections']:assert ORIGIN+route+'#'+fragment in ids
home=(ROOT/'index.html').read_text()
assert home.count('<button class="monolith-trigger"')==1 and "document.createElement('button')" not in home
assert 'translateX(-115vw)' in home and '{ duration: 1000 }' in home and '{ duration: 860 }' in home
assert 'prefers-reduced-motion: reduce' in home
assert 'opening.css' in home and all('opening.css' not in p.read_text() for p in pages if p!=ROOT/'index.html')
# Every selector has exactly one definition in a given media context.
def rules(text, context=''):
    text=re.sub(r'/\*.*?\*/','',text,flags=re.S);i=0
    while i<len(text):
        start=text.find('{',i)
        if start<0:break
        label=text[i:start].strip(); depth=1;j=start+1
        while depth:
            if text[j]=='{':depth+=1
            if text[j]=='}':depth-=1
            j+=1
        block=text[start+1:j-1]
        if label.startswith('@media'):yield from rules(block,label)
        else:yield context,label
        i=j
assert not re.search(r'(--[\w-]+):\s*var\(\1\)', (ROOT/'styles.css').read_text()), 'Self-referencing design token'
seen=set()
for name in ['styles.css','opening.css']:
    for key in rules((ROOT/name).read_text()):
        assert key not in seen, f'Duplicate CSS selector/context: {key}'
        seen.add(key)
print(f'PASS: {len(pages)} pages, local assets/fragments, embedded fonts, canonical graph, JSON/XML, static monolith trigger, and {len(seen)} unique CSS rules.')
