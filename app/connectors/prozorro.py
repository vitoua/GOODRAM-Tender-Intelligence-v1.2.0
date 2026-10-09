from datetime import datetime
import httpx
from app.core import Tender
from app.filters import relevant
from app.fx import eur
B='https://public-api.prozorro.gov.ua/api/2.5/tenders'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(countries,published_from,min_eur,limit=500):
 out=[];offset=None;seen=0
 async with httpx.AsyncClient(timeout=50) as c:
  while seen<limit:
   p={'limit':100,'descending':1};
   if offset:p['offset']=offset
   r=await c.get(B,params=p);r.raise_for_status();body=r.json()
   for row in body.get('data',[]):
    seen+=1;d=await c.get(f"{B}/{row['id']}");d.raise_for_status();x=d.json().get('data',{});pub=dt(x.get('dateCreated') or x.get('dateModified'))
    if pub and pub<published_from:return out
    ddl=dt((x.get('tenderPeriod') or {}).get('endDate'));items=x.get('items',[]);cpv=[i.get('classification',{}).get('id','') for i in items];text=' '.join([x.get('title',''),x.get('description','')]+[i.get('description','') for i in items])
    if not ddl or ddl<datetime.now() or not relevant('prozorro',cpv,text):continue
    val=(x.get('value') or {}).get('amount');cur=(x.get('value') or {}).get('currency','UAH');ve=await eur(val,cur)
    if min_eur>0 and (ve is None or ve<min_eur):continue
    n=x.get('tenderID',row['id']);out.append(Tender('prozorro:'+n,'prozorro','UKR',x.get('title') or n,(x.get('procuringEntity') or {}).get('name',''),val,cur,ddl,pub,url=f'https://prozorro.gov.ua/tender/{n}',description=x.get('description',''),procurement_id=n,cpv=cpv,value_eur=ve))
   offset=(body.get('next_page') or {}).get('offset')
   if not offset:break
 return out
