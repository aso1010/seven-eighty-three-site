"""Validate Gotham Gay's peer-lab hierarchy and Lab 783 portfolio references."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
HOLD='https://gothamgay.com/#organization';LAB='https://seveneightythree.com/#organization';PERSON='https://gothamgay.com/#person';WILD='https://wildlakestudio.com/#organization'
RET='https://gothamgay.com/#retention-rail';CASA='https://gothamgay.com/#casa-josefin';DIVISION='https://seveneightythree.com/foundry/#division'
ASSETS={'https://basalt.fm/#software','https://apsis.club/#software','https://bullpen.vip/#software','https://communalfoundation.org/#organization',RET,CASA,'https://pogo.vet/#organization','https://seveneightythree.com/#literary-dramatic-ip'}
CHILDREN={'https://basalt.fm/#organization',RET,'https://bullpen.vip/#organization',CASA,'https://pogo.vet/#organization'}
def strict_object(pairs):
 result={}
 for key,value in pairs:
  assert key not in result,f'Duplicate JSON key: {key}'
  result[key]=value
 return result
def parse(text):return json.loads(text,object_pairs_hook=strict_object)
def refs(item):
 if not item:return []
 return item if isinstance(item,list) else [item]
canonical=parse((ROOT/'schema.json').read_text())
for path in ROOT.rglob('*.html'):
 graph=parse(re.search(r'<script type="application/ld\+json">(.*?)</script>',path.read_text(),re.S)[1])['@graph'];ids=[n['@id'] for n in graph];assert len(ids)==len(set(ids)),path;nodes={n['@id']:n for n in graph}
 assert {HOLD,LAB,PERSON,WILD,DIVISION}|ASSETS<=nodes.keys(),path
 assert nodes[LAB]['parentOrganization']=={'@id':HOLD}
 assert nodes[WILD]['parentOrganization']=={'@id':HOLD}
 assert {n['@id'] for n in nodes[HOLD]['subOrganization']}=={LAB,WILD}
 assert {n['@id'] for n in nodes[LAB]['subOrganization']}==CHILDREN
 assert WILD not in {n['@id'] for n in nodes[LAB]['subOrganization']}
 assert {n['@id'] for n in nodes[LAB]['owns']}==ASSETS
 assert nodes[LAB]['founder']['@id']==PERSON and nodes[PERSON]['url']=='https://gothamgay.com/'
 assert nodes[LAB]['alternateName']=='Lab 783'
 assert nodes[DIVISION]['parentOrganization']=={'@id':LAB}
 assert nodes[RET]['url']==RET and nodes[CASA]['url']==CASA
 assert 'https://argelysoriach.com/#person' not in path.read_text()
 apsis=nodes['https://apsis.club/#software'];assert apsis['@type']=='SoftwareApplication' and apsis['softwareVersion']=='Preview-Live'
 assert apsis['publisher']['@id']==apsis['provider']['@id']==LAB
 assert apsis['creator']['@id']==apsis['author']['@id']==PERSON
 assert not any(n.get('@type')=='Organization' and 'apsis.club' in n['@id'] for n in graph)
 assert nodes['https://basalt.fm/#software']['releaseNotes']=='https://basalt.fm/spec#provenance'
 # Combine parent pointers and child lists in one directed parent-to-child graph.
 edges={}
 for n in graph:
  for parent in refs(n.get('parentOrganization')):edges.setdefault(parent['@id'],set()).add(n['@id'])
  for child in refs(n.get('subOrganization'))+refs(n.get('department')):edges.setdefault(n['@id'],set()).add(child['@id'])
 visited=set();active=set()
 def visit(node):
  assert node not in active,('Circular parent-child relationship',path,node)
  if node in visited:return
  active.add(node)
  for child in edges.get(node,[]):visit(child)
  active.remove(node);visited.add(node)
 for node in list(edges):visit(node)
for name in ['llms.txt','llm.txt','llms-full.txt']:
 p=ROOT/name
 if not p.exists():continue
 s=p.read_text()
 for value in ['Operating Lab 01','Operating Lab 02','https://gothamgay.com/llms.txt',PERSON,RET,CASA,'Literary & Dramatic IP']:
  # The IP asset may retain its published work title in the portfolio inventory.
  if value=='Literary & Dramatic IP':assert value in s
  else:assert value in s,(name,value)
 assert 'https://argelysoriach.com/#person' not in s
 assert '- Parent: '+HOLD in s.split('### Wild Lake Studio')[1].split('### Apsis')[0]
home=(ROOT/'index.html').read_text();assert '<link rel="canonical" href="https://seveneightythree.com/">' in home
for domain in ['gothamgay.com','wildlakestudio.com']:assert f'<link rel="me" href="https://{domain}/">' in home
registry=parse((ROOT/'universe.json').read_text())
for field,value in {'node_id':'seveneightythree-lab-01','role':'Operating Lab 01 (Systems Laboratory & Venture Foundry)','parent_node':'https://gothamgay.com/','principal_node':PERSON,'peer_lab':'https://wildlakestudio.com/','resonance_hz':7.83}.items():assert registry[field]==value
print('PASS Gotham Gay holding, two peer labs, eight portfolio assets, canonical principal, Apsis preview governance, provenance, sequential references and zero parent-child cycles.')
