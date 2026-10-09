from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from app.core import Tender
from app.filters import keywords
URL='https://www.juntadeandalucia.es/haciendayadministracionpublica/apl/pdc-front-publico/perfiles-licitaciones/licitaciones-publicadas'
async def fetch(countries,published_from,min_eur):
 async with httpx.AsyncClient(timeout=45,follow_redirects=True,headers={'User-Agent':'Mozilla/5.0 GOODRAM-Tender-Intelligence/1.2'}) as c:r=await c.get(URL);r.raise_for_status()
 s=BeautifulSoup(r.text,'html.parser');terms=[k.casefold() for k in keywords(['es','en'])];out=[]
 for a in s.select('a[href]'):
  title=' '.join(a.get_text(' ',strip=True).split());href=a.get('href','');text=' '.join((a.parent or a).get_text(' ',strip=True).split())
  if len(title)<8 or not any(k in text.casefold() for k in terms):continue
  rid=str(abs(hash(href)));out.append(Tender('junta:'+rid,'junta','ESP',title,'Junta de Andalucía',published=datetime.now(),url=str(httpx.URL(URL).join(href)),description=text,procurement_id=rid))
 return list({x.id:x for x in out}.values())
