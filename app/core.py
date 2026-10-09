from dataclasses import dataclass,field
from datetime import datetime
from collections import Counter
@dataclass
class Tender:
 id:str;source:str;country:str;title:str;buyer:str='';value:float|None=None;currency:str='';deadline:datetime|None=None;published:datetime|None=None;status:str='active';url:str='';description:str='';procurement_id:str='';cpv:list[str]=field(default_factory=list);value_eur:float|None=None;source_links:dict=field(default_factory=dict)
class Store:
 def __init__(self):self.data={};self.runs=[];self.last_update=None
 def replace(self,results):
  self.data={};self.runs=[]
  for src,rows,error in results:
   added=0;dupes=0
   if error:self.runs.append({'source':src,'status':'error','count':0,'added':0,'duplicates':0,'error':str(error)[:500]});continue
   for x in rows:
    key=(x.country,(x.procurement_id or x.id).lower())
    old=next((y for y in self.data.values() if (y.country,(y.procurement_id or y.id).lower())==key),None)
    if old:old.source_links.update(x.source_links or {x.source:x.url});dupes+=1
    else:x.source_links=x.source_links or {x.source:x.url};self.data[x.id]=x;added+=1
   self.runs.append({'source':src,'status':'ok','count':len(rows),'added':added,'duplicates':dupes,'error':''})
  self.last_update=datetime.now()
store=Store()
def active(x):return not x.deadline or x.deadline>=datetime.now()
def analytics(rows):return {'countries':dict(Counter(x.country for x in rows).most_common(12)),'sources':dict(Counter(x.source for x in rows).most_common(12)),'cpv':dict(Counter(c for x in rows for c in x.cpv).most_common(12)),'buyers':dict(Counter(x.buyer for x in rows if x.buyer).most_common(12))}
