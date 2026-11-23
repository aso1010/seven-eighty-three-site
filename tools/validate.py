#!/usr/bin/env python3
"""Dependency-free validation of the published static site and canonical graph."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, hashlib, base64, xml.etree.ElementTree as ET
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
    previous_level = 0
    for tag, attrs in page.tags:
        level = int(tag[1]) if re.fullmatch(r'h[1-6]', tag) else int(attrs['aria-level']) if attrs.get('role') == 'heading' and attrs.get('aria-level', '').isdigit() else None
        if level is not None:
            assert level <= previous_level + 1, f'Skipped heading level: {path}: H{previous_level} to H{level}'
            previous_level = level

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
    is_home = path == ROOT/'index.html'
    assert source.count('href="/styles.css"') == (0 if is_home else 1)
    assert source.count('src="/site.js"') == (0 if is_home else 1)
    if is_home: assert len(re.sub(r'<script type="application/ld\+json">.*?</script>', '', source, flags=re.S).encode()) < 27000, 'Homepage visual document and runtime exceed 27 KB'
    assert source.count('class="site-header"') == 1 and source.count('class="page-index"') == 1
    assert any(attrs.get('aria-current')=='page' for tag,attrs in page.tags)
    for endpoint in ('schema.json','site.json','llms.txt'): assert f'href="/{endpoint}"' in source
    assert re.search(r'rel="canonical" href="https://seveneightythree.com/',source)
    fonts=re.findall(r'@font-face\s*\{[^}]+\}',source)
    assert len(fonts)==2
    if is_home:
        for filename in ['archivo.woff2','jetbrains-mono.woff2']:assert (ROOT/'assets'/filename).is_file()
    else:
        assert all('data:font/woff2;base64,' in f and 'font-display: block' in f for f in fonts)
        font_reference=fonts
    canonical=json.loads((ROOT/'schema.json').read_text())
    inline=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
    if is_home:
        nodes={n['@id']:n for n in canonical['@graph']}
        def subset(a,b):
            if isinstance(a,dict):return all(k in b and subset(v,b[k]) for k,v in a.items())
            if isinstance(a,list):return len(a)==len(b) and all(subset(x,y) for x,y in zip(a,b))
            return a==b
        assert all(n['@id'] in nodes and subset(n,nodes[n['@id']]) for n in inline['@graph']), 'Stale homepage graph projection'
    else: assert inline==canonical, f'Stale embedded graph: {path}'
    for tag, attrs in page.tags:
        if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy':
            policy=attrs['content']
            for style in re.findall(r'<style>(.*?)</style>',source,re.S):
                digest=base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()
                assert 'sha256-'+digest in policy, f'Stale embedded font policy hash: {path}'
            if is_home:
                for script in re.findall(r'<script>(.*?)</script>',source,re.S):
                    digest=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
                    assert 'sha256-'+digest in policy, 'Stale inline script policy hash'
            else: assert "style-src 'self'" in policy and "script-src 'self'" in policy

for path in pages:
    if path!=ROOT/'index.html': assert re.findall(r'@font-face\s*\{[^}]+\}',path.read_text())==font_reference
for block in font_reference:
    name='archivo.woff2' if "'Archivo'" in block else 'jetbrains-mono.woff2'
    data=re.search(r'base64,([^)]*)',block)[1]
    assert (ROOT/'assets'/name).read_bytes()==base64.b64decode(data), 'Font bytes changed'
for path in ROOT.rglob('*.json'): json.loads(path.read_text())
sitemap = ET.parse(ROOT/'sitemap.xml')
assert sitemap.getroot().tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
sitemap_urls = [node.text for node in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(sitemap_urls) == len(set(sitemap_urls))
assert set(sitemap_urls) == {ORIGIN + ('/' if p == ROOT/'index.html' else '/' + str(p.parent.relative_to(ROOT)) + '/') for p in pages}
assert 'Sitemap: ' + ORIGIN + '/sitemap.xml' in (ROOT/'robots.txt').read_text()
assert '/sitemap.xml\n  Content-Type: application/xml; charset=utf-8' in (ROOT/'_headers').read_text()
graph=canonical['@graph']; ids=[n['@id'] for n in graph]; assert len(ids)==len(set(ids))
org=next(n for n in graph if n['@id']==ORIGIN+'/#organization')
assert {n['@id'] for n in org['subOrganization']} == {'https://basalt.fm/#organization','https://theangel.biz/#retention-rail','https://bullpen.vip/#organization','https://theangel.biz/#casa-josefin','https://pogo.vet/#organization'}
assert 'venture foundry' in org['description']
assert {n['@id'] for n in graph if n.get('@type')=='Service'} == {ORIGIN+'/#venture-compilation'}
for path in pages:
    route='/' if path==ROOT/'index.html' else '/'+str(path.parent.relative_to(ROOT))+'/'
    for fragment in ['webpage','breadcrumbs','sections']:assert ORIGIN+route+'#'+fragment in ids
home=(ROOT/'index.html').read_text()
assert home.count('<button class="monolith-trigger"')==1 and "document.createElement('button')" not in home
assert 'translateX(-115vw)' in home and '860' in home
assert 'prefers-reduced-motion' in home
assert all('href="/opening.css"' not in p.read_text() for p in pages)
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
