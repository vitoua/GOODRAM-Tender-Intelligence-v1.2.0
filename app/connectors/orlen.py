from datetime import datetime,timedelta
import re,httpx
from bs4 import BeautifulSoup
from app.core import Tender
from app.filters import keywords
URL='https://connect.orlen.pl/servlet/HomeServlet'
async def fetch(countries,published_from,min_eur):
 async with httpx.AsyncClient(timeout=45,follow_redirects=True,headers={'User-Agent':'Mozilla/5.0 GOODRAM-Tender-Intelligence/1.2'}) as c:r=await c.get(URL);r.raise_for_status()
 s=BeautifulSoup(r.text,'html.parser');out=[];terms=[k.casefold() for k in keywords(['pl','en'])]
 for a in s.select('a[href*="/app/outRfx/"]'):
  title=' '.join(a.get_text(' ',strip=True).split());href=a.get('href','');text=' '.join((a.parent or a).get_text(' ',strip=True).split())
  if not title or not any(k in text.casefold() for k in terms):continue
  m=re.search(r'/outRfx/(\d+)',href);rid=m.group(1) if m else href;url=httpx.URL(URL).join(href).__str__();deadline=None
  dm=re.search(r'(\d+)\s*dni?',text,re.I)
  if dm:deadline=datetime.now()+timedelta(days=int(dm.group(1)))
  out.append(Tender('orlen:'+rid,'orlen','POL',title,'Grupa ORLEN',deadline=deadline,published=datetime.now(),url=url,description=text,procurement_id=rid))
 return list({x.id:x for x in out}.values())
