import json
from app.main import app,rows
from app.filters import codes,relevant
assert app.version=='1.2.0'
assert '30230000' in codes('prozorro')
assert relevant('prozorro',['30230000'],'')
assert not relevant('prozorro',['09123000'],'Природний газ')
paths={r.path for r in app.routes};assert {'/refresh/start','/refresh/status','/cpv','/export.xlsx'}<=paths
print('tests ok')
