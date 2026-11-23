"""Validate canonical operating-company and preview-system relationships."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
PARENT='https://seveneightythree.com/#organization'
PERSON='https://argelysoriach.com/#person'
DOMAINS=['basalt.fm','retentionrail.io','bullpen.vip','wildlakestudio.com','casajosefin.com']
def strict_object(pairs):
    result={}
    for key,value in pairs:
        assert key not in result, f'Duplicate JSON key: {key}'
        result[key]=value
    return result
def parse(text):return json.loads(text,object_pairs_hook=strict_object)
canonical=parse((ROOT/'schema.json').read_text())
required={PARENT,PERSON,'https://apsis.club/#software','https://pogo.vet/#organization'}|{f'https://{d}/#organization' for d in DOMAINS}|{f'https://{d}/#software' for d in DOMAINS[:3]}
for path in ROOT.rglob('*.html'):
    graph=parse(re.search(r'<script type="application/ld\+json">(.*?)</script>',path.read_text(),re.S)[1])['@graph']
    ids=[n['@id'] for n in graph];assert len(ids)==len(set(ids)),path
    nodes={n['@id']:n for n in graph};assert required<=nodes.keys(),path
    parent=nodes[PARENT];assert parent['alternateName']==['783','Lab 783']
    assert {n['@id'] for n in parent['subOrganization']}=={f'https://{d}/#organization' for d in DOMAINS}|{'https://pogo.vet/#organization'}
    assert parent['founder']['jobTitle']=='Founder & Chief Systems Architect'
    assert nodes[PERSON]['jobTitle']=='Founder & Chief Systems Architect'
    for domain in DOMAINS:
        org=nodes[f'https://{domain}/#organization'];assert org['@type']=='Organization'
        assert org['parentOrganization']=={'@id':PARENT}
        assert org['url']==f'https://{domain}/'
    for domain in DOMAINS[:3]:
        app=nodes[f'https://{domain}/#software'];assert app['@type']=='SoftwareApplication'
        assert app['provider']=={'@id':f'https://{domain}/#organization'}
    apsis=nodes['https://apsis.club/#software'];assert apsis['@type']=='SoftwareApplication'
    assert apsis['softwareVersion']=='Preview-Live'
    assert apsis['applicationCategory']=='Direct-to-Fan Publishing System'
    assert apsis['provider']['@id']==apsis['publisher']['@id']==PARENT
    assert apsis['author']['@id']==apsis['creator']['@id']==PERSON
    assert not any('apsis.club' in n['@id'] and (n.get('@type')=='Organization' or isinstance(n.get('@type'),list) and 'Organization' in n['@type']) for n in graph)
    assert not {'https://basalt.fm/#engine','https://apsis.club/#application','https://wild-lake.org/#organization'}&set(ids)
    assert nodes['https://basalt.fm/#software']['releaseNotes']=='https://basalt.fm/spec#provenance'
for name in ['llms.txt','llm.txt','llms-full.txt']:
    path=ROOT/name
    if not path.exists():continue
    text=path.read_text()
    for entity_id in required-{PERSON}:assert entity_id in text,(name,entity_id)
    for phrase in ['Operating Company (Seven Eighty Three Subsidiary)','Preview-Live System (Seven Eighty Three Infrastructure)','Juanel Oriach, Founder & CEO','Jordy Oriach, Co-Founder & Player-Coach','https://seveneightythree.com/llms.txt','https://argelysoriach.com']:assert phrase in text,(name,phrase)
print('PASS: strict JSON, unique entity IDs, five operating subsidiaries, software providers, Apsis preview governance, provenance, and LLM cross-links.')
