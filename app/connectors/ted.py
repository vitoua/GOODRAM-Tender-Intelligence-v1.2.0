from datetime import datetime
import re,httpx
from app.core import Tender
from app.filters import codes,keywords,relevant
from app.fx import eur
URL='https://api.ted.europa.eu/v3/notices/search';FIELDS=['publication-number','notice-title','buyer-name','buyer-country','publication-date','deadline','description-proc','form-type','classification-cpv','total-value','total-value-cur']
def first(v):
 if isinstance(v,dict):return first(v.get('eng') or v.get('pol') or next(iter(v.values()),''))
 if isinstance(v,list):return first(v[0]) if v else ''
 return str(v or '')
def dt(v):
 try:return datetime.fromisoformat(first(v)[:10])
 except:return None
async def request(c,q,limit=100):
 p={'query':q,'fields':FIELDS,'page':1,'limit':limit,'scope':'ACTIVE','paginationMode':'PAGE_NUMBER','onlyLatestVersions':True};r=await c.post(URL,json=p)
 if r.status_code!=200:raise RuntimeError(f'TED HTTP {r.status_code}: {r.text[:500]}')
 return r.json().get('notices',[])
async def fetch(countries,published_from,min_eur):
 cut=published_from.strftime('%Y%m%d');raw={}
 async with httpx.AsyncClient(timeout=60,headers={'User-Agent':'GOODRAM-Tender-Intelligence/1.2.0'}) as c:
  for code in codes('ted'):
   try:rows=await request(c,f'classification-cpv={code} AND publication-date>={cut}')
   except RuntimeError as e:
    if 'QUERY_UNSUPPORTED_FIELD_VALUE' in str(e) or 'not supported' in str(e):continue
    raise
   for x in rows:raw[first(x.get('publication-number'))]=x
  terms=' OR '.join(f'FT~"{k}"' for k in keywords()[:30])
  for x in await request(c,f'({terms}) AND publication-date>={cut}'):raw[first(x.get('publication-number'))]=x
 out=[]
 for n,x in raw.items():
  co=first(x.get('buyer-country'))[:3].upper();ddl=dt(x.get('deadline'));pub=dt(x.get('publication-date'));cpv=[first(z) for z in x.get('classification-cpv',[])];title=first(x.get('notice-title'));desc=first(x.get('description-proc'))
  if co not in countries or not ddl or ddl<datetime.now() or not pub or pub<published_from or not relevant('ted',cpv,title+' '+desc):continue
  try:val=float(first(x.get('total-value')))
  except:val=None
  cur=first(x.get('total-value-cur')) or 'EUR';ve=await eur(val,cur)
  if min_eur>0 and (ve is None or ve<min_eur):continue
  out.append(Tender('ted:'+n,'ted',co,title,first(x.get('buyer-name')),val,cur,ddl,pub,url=f'https://ted.europa.eu/en/notice/-/detail/{n}',description=desc,procurement_id=n,cpv=cpv,value_eur=ve))
 return out
