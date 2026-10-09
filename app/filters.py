import json,re
from pathlib import Path
def load(name):return json.loads(Path('data/'+name).read_text())
def keywords(langs=None):
 d=load('keywords.json');langs=langs or d.keys();return list(dict.fromkeys(k for lang in langs for k in d.get(lang,[])))
def codes(source):return [x['code'] for x in load('prozorro_cpv.json' if source=='prozorro' else 'ted_cpv.json') if x.get('active')]
def relevant(source,items,text):
 norm=[re.sub(r'\D','',str(c))[:8] for c in items];active=codes(source)
 code_ok=any(c==a or (a.endswith('0000') and c.startswith(a.rstrip('0'))) for c in norm for a in active)
 langs=['uk'] if source=='prozorro' else None;t=(text or '').casefold();kw_ok=any(k.casefold() in t for k in keywords(langs))
 return code_ok or kw_ok
