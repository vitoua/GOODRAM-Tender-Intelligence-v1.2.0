from datetime import datetime
import httpx
from app.config import settings
from app.core import Tender
from app.filters import codes,relevant
from app.fx import eur
URL='https://www.base.gov.pt/APIBase2/GetInfoAnuncio'
def dt(v):
 for f in ('%d/%m/%Y','%Y-%m-%d'):
  try:return datetime.strptime(str(v),f)
  except:pass
async def fetch(countries,published_from,min_eur):
 if not settings.base_api_token:raise RuntimeError('BASE Portugal wymaga BASE_API_TOKEN')
 out=[]
 async with httpx.AsyncClient(timeout=50,headers={'_AcessToken':settings.base_api_token}) as c:
  for cpv in codes('ted'):
   r=await c.get(URL,params={'CPV':cpv,'numDias':min(90,max(1,(datetime.now()-published_from).days))});r.raise_for_status();body=r.json();rows=body if isinstance(body,list) else body.get('data',body.get('results',[])) if isinstance(body,dict) else []
   for x in rows:
    title=x.get('objectoContrato') or x.get('descContrato') or x.get('TipoAnuncio','');desc=x.get('descContrato','');cpvs=x.get('cpv',[]) if isinstance(x.get('cpv',[]),list) else [x.get('cpv','')]
    if not relevant('ted',cpvs,title+' '+desc):continue
    val=x.get('precoBaseProcedimento') or x.get('precoContratual');
    try:val=float(str(val).replace('.','').replace(',','.'))
    except:val=None
    ve=await eur(val,'EUR')
    if min_eur>0 and (ve is None or ve<min_eur):continue
    n=str(x.get('nAnuncio') or x.get('idINCM') or x.get('idContrato'));out.append(Tender('base:'+n,'base','PRT',title,str(x.get('adjudicante','')),val,'EUR',published=dt(x.get('dataPublicacao')),url='https://www.base.gov.pt',description=desc,procurement_id=n,cpv=cpvs,value_eur=ve))
 return out
