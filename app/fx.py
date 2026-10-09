import httpx
CACHE={'EUR':1.0}
async def eur(value,currency):
 if value is None:return None
 cur=(currency or 'EUR').upper()
 if cur=='EUR':return float(value)
 if cur not in CACHE:
  try:
   async with httpx.AsyncClient(timeout=12) as c:r=await c.get(f'https://api.frankfurter.dev/v2/rate/eur/{cur.lower()}');r.raise_for_status();CACHE[cur]=float(r.json()['rate'])
  except:return None
 return float(value)/CACHE[cur]
