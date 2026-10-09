import io,json,zipfile,httpx
from datetime import date,datetime,timedelta
from app.core import Tender
from app.filters import relevant
from app.fx import eur
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(countries,published_from,min_eur):
 out=[];now=datetime.now();days=min(31,max(1,(date.today()-published_from.date()).days+1))
 async with httpx.AsyncClient(timeout=65,headers={'User-Agent':'GOODRAM-Tender-Intelligence/1.2.0'}) as c:
  for i in range(1,days+1):
   day=date.today()-timedelta(days=i)
   if day<published_from.date():break
   r=await c.get('https://oeffentlichevergabe.de/api/notice-exports',params={'pubDay':day.isoformat(),'format':'ocds.zip'})
   if r.status_code in (400,404):continue
   r.raise_for_status()
   with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    for fn in z.namelist():
     doc=json.loads(z.read(fn));rel=(doc.get('releases') or [{}])[0];t=rel.get('tender') or {};ddl=dt((t.get('tenderPeriod') or {}).get('endDate'));items=t.get('items') or [];cpv=[x.get('classification',{}).get('id','') for x in items];title=t.get('title','');desc=t.get('description','')
     if not ddl or ddl<now or not relevant('ted',cpv,title+' '+desc):continue
     val=(t.get('value') or {}).get('amount');cur=(t.get('value') or {}).get('currency','EUR');ve=await eur(val,cur)
     if min_eur>0 and (ve is None or ve<min_eur):continue
     parties=rel.get('parties') or [];buyer=next((p.get('name','') for p in parties if 'buyer' in p.get('roles',[])),'');ocid=rel.get('ocid') or rel.get('id') or fn;url=f'https://oeffentlichevergabe.de/ui/de/notices/{ocid}'
     out.append(Tender('de:'+ocid,'germany','DEU',title or ocid,buyer,val,cur,ddl,dt(rel.get('date')),url=url,description=desc,procurement_id=ocid,cpv=cpv,value_eur=ve))
 return out
