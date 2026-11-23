"""Validate Pogo's canonical graph, registry, protocol boundaries and script integrity."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,base64,hashlib
ROOT=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
ID='https://pogo.vet/#organization'
graph=json.loads((ROOT/'schema.json').read_text())['@graph']
assert len(graph)==len({n['@id'] for n in graph})
org=next(n for n in graph if n['@id']==ID)
assert org['name']=='Pogo' and org['alternateName']=='Pogo Protocol'
assert org['@type']=='Organization' and org['url']=='https://pogo.vet'
assert org['parentOrganization']=={'@id':'https://seveneightythree.com/#organization'}
assert 'Not a veterinary clinic.' in org['description']
assert 'founder' not in org, 'Do not invent a human founder for the co-principal'
listing=next(n for n in graph if n['@id']=='https://seveneightythree.com/#holdings')['itemListElement']
assert [n['position'] for n in listing]==list(range(1,len(listing)+1))
assert listing[-1]['item']=={'@id':ID}
node=next(n for n in json.loads((ROOT/'universe.json').read_text())['nodes'] if n['id']=='pogo-vet-01')
assert node['node_id']==node['id'] and node['resonance_hz']==7.83
assert node['name']=='Pogo' and node['origin_audit']['status']=='reported'
assert node['entity_name']=='Pogo' and node['alternate_name']=='Pogo Protocol' and node['visual_tokens']['accent']=='#C8A265'
assert node['co_principal']=='Pogo' and node['acoustic_engine']=='basalt.fm'
assert [p['name'] for p in node['pillars']]==['The Ledger','The Floor','The Bowl']
assert 'Licensed DVM sign-off' in node['pillars'][0]['verification_requirement']
assert 'not establish' in node['claims_boundary']
js=(ROOT/'universe-node.js').read_text()
payload=json.loads(re.search(r'value:freeze\((.*?)\),writable:false',js)[1])
assert next(n for n in payload['ventures'] if n['id']=='pogo-vet-01')==node
assert any(n['id']=='casa-josefin-01' for n in payload['ventures'])
home=(ROOT/'index.html').read_text();digest='sha256-'+base64.b64encode(hashlib.sha256(js.encode()).digest()).decode()
assert 'integrity="'+digest+'"' in home and "'"+digest+"'" in home
for name in ['llms.txt','llm.txt']:
 text=(ROOT/name).read_text();entry=text.split('### Pogo (',1)[1].split('### Acquisition',1)[0]
 assert '\u2014' not in entry
 for value in ['pogo-vet-01','https://pogo.vet','Pogo (Crown Heights','7.83 Hz','Not a veterinary clinic','The Ledger','The Floor','The Bowl','not establish therapeutic effects']:assert value in entry,(name,value)
for route in ['index.html','foundry/index.html']:
 text=(ROOT/route).read_text();row=re.search(r'<article class="structure-entry pogo-entry".*?</article>',text,re.S)[0]
 assert '>POGO</a>' in row and 'class="pogo-coordinate content-label"' in row and 'Pogo Protocol' not in row
 assert 'h3 class=entity-title' in row and 'NOT A CLINIC' in row and 'BASALT ACOUSTIC RAIL' in row
 assert 'down-regulate chronic hypervigilance' not in row and 'trigger vagal calm' not in row
for path in ROOT.rglob('*'):
 if path.suffix in {'.html','.json','.txt','.js','.xml','.css'}:
  text=path.read_text();assert 'pogo'+'vet' not in text.lower(),path
  assert '\u2014' not in text,path
print('PASS Pogo entity, sequential portfolio, registry and frozen-payload parity, SRI hash, verification requirements and clinical boundary.')
