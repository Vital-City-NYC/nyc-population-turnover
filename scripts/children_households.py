"""Children in New York City households, 1970-2024: married couples with and without their own children under
18, and households with anyone under 18. Writes data/raw/fix/children_households.json, read by build_data.py.

Sources
  1970  Census of Population PC(1)-B34, Table 25, page 34-115 (New York City column, read from the scan):
        husband-wife families 1,603,387, with own children under 18 774,496. No count of households with
        anyone under 18 is published for the city.
  1980  Married couples with own children: 1980 Public Use Microdata Sample A (5 percent; household record
        HHTYPE column 104, CHILDREN column 105); the sample's share among married couples is applied to the
        published 1,203,135 married couples. Households with anyone under 18: Summary Tape File 1A (100 percent),
        Table 19, five county records (the same file's Table 3 and Table 16 reproduce the published 2,788,530
        households and 1,203,135 married couples exactly).
  1990  Census of Population CP-1-34, Table 57 ("Household and Family Characteristics"), the five county columns:
        married-couple families and those with own children under 18. Households with anyone under 18: Summary
        Tape File 1A, table P18, five county records (households sum to the published 2,819,401).
        Check on the sample method: the 1990 PUMS gives 43.7 percent of married couples with own children against
        43.5 percent in Table 57.
  2000  SF1 P18 (married-couple family with/without own children under 18), P19 (households with people under 18).
  2010  SF1 P19 (husband-wife family with/without own children under 18), P20.
  2020  DHC P20 (married couple household with/without own children under 18), P21.
  2006-2024  ACS 1-year B11003 (married-couple family with own children under 18), B11005, B11001.
"""
import json, os, subprocess, urllib.request, zipfile
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), '..')
CACHE = os.path.join(ROOT, 'data', 'cache')
OUT = os.path.join(ROOT, 'data', 'raw', 'fix', 'children_households.json')
KEY = subprocess.run(['security', 'find-generic-password', '-s', 'CENSUS_API_KEY', '-w'], capture_output=True, text=True).stdout.strip()


def api(path, vars_):
    url = f'https://api.census.gov/data/{path}?get={",".join(vars_)}&for=place:51000&in=state:36&key={KEY}'
    rows = json.load(urllib.request.urlopen(url))
    return {k: int(v) for k, v in zip(rows[0], rows[1]) if k in vars_}


def cached(name, url):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path


out = {}

# 1970: printed table
out['1970'] = dict(households=2836872, married=1603387, married_own=774496, any_u18=None,
                   source='1970 Census of Population PC(1)-B34, Table 25, page 34-115, New York City column (husband-wife families; with own children under 18 years)')

# 1980: PUMS shares applied to published counts
z = zipfile.ZipFile(cached('1980_PUMSAXNY.ZIP', 'https://www2.census.gov/census_1980/pums_1980_a/PUMSAXNY.ZIP'))
data = z.read(next(n for n in z.namelist() if n.upper().endswith('.NY'))).decode('latin-1')
nyc80 = {'036', '037', '038', '039', '040'}
c = Counter(); cur = None
def flush80():
    if cur and cur['hh']:
        c['hh'] += 20; c['married'] += 20 * cur['m']; c['married_own'] += 20 * (cur['m'] and cur['own']); c['any_u18'] += 20 * cur['u18']
for i in range(0, len(data), 193):
    l = data[i:i + 193]
    if l[0] == 'H':
        flush80()
        cur = dict(hh=l[5:8] in nyc80 and l[103] in '1234', m=l[103] == '1', own=l[104] in '123', u18=False)
    elif l[0] == 'P' and cur and cur['hh'] and int(l[7:9]) < 18:
        cur['u18'] = True
flush80()
HH80, M80 = 2788530, 1203135
nyc = {'005', '047', '061', '081', '085'}
z = zipfile.ZipFile(cached('1980_stf1axny.zip', 'https://www2.census.gov/census_1980/stf1a/stf1axny.zip'))
s80 = Counter()
for raw in z.open(z.namelist()[0]):
    l = raw.decode('latin-1').rstrip('\r\n')
    if l[9:11] == '11' and l[33:35] == '36' and l[39:42] in nyc:       # county records
        s80['hh'] += int(l[288:297])                                        # Table 3: households
        s80['married'] += int(l[1566:1575])                                 # Table 16 cell 3: married-couple family
        s80['any_u18'] += sum(int(l[1821 + 9 * i:1830 + 9 * i]) for i in range(4))   # Table 19: households with persons under 18
assert s80['hh'] == HH80 and s80['married'] == M80, s80
out['1980'] = dict(households=HH80, married=M80, married_own=round(M80 * c['married_own'] / c['married']),
                   any_u18=s80['any_u18'], sample=dict(c),
                   source='Married couples with own children: 1980 PUMS A share x published married couples (1,203,135); households with anyone under 18: 1980 STF 1A Table 19')

# 1990: Table 57 county columns (households, married-couple families, with own children under 18) + PUMS for any under 18
t57 = {'Bronx': (424112, 146234, 67041), 'Kings': (828199, 335295, 155867), 'New York': (716422, 187016, 65975),
       'Queens': (720149, 351675, 150066), 'Richmond': (130519, 78198, 38986)}
HH90 = sum(v[0] for v in t57.values()); M90 = sum(v[1] for v in t57.values()); MO90 = sum(v[2] for v in t57.values())
assert HH90 == 2819401, HH90
import struct
z = zipfile.ZipFile(cached('1990_stf1a5ny.dbf.zip', 'https://www2.census.gov/census_1990/CD90_1A_2_1/stf1a5ny.dbf.zip'))
b = z.read(z.namelist()[0]); n, hlen, rlen = struct.unpack('<IHH', b[4:12])
F = {}; off, pos = 32, 1
while b[off] != 0x0D:
    F[b[off:off + 11].split(b'\0')[0].decode()] = (pos, b[off + 16]); pos += b[off + 16]; off += 32
s90 = Counter()
for i in range(n):
    r = b[hlen + i * rlen:hlen + (i + 1) * rlen]
    g = lambda k: r[F[k][0]:F[k][0] + F[k][1]].decode('latin-1').strip()
    if g('SUMLEV') == '050' and g('STATEFP') == '36' and g('CNTY') in nyc:
        v = [int(g(f'P01800{j:02d}')) for j in range(1, 11)]
        s90['any_u18'] += sum(v[:5]); s90['hh'] += sum(v)
assert s90['hh'] == HH90, s90
out['1990'] = dict(households=HH90, married=M90, married_own=MO90, any_u18=s90['any_u18'], counties=t57,
                   source='1990 CP-1-34 Table 57, five county columns (PDF pages 411, 422, 426, 432, 434); households with anyone under 18 from 1990 STF 1A table P18')

# 2000-2020 decennial
d = api('2000/dec/sf1', ['P018001', 'P018008', 'P018009', 'P019001', 'P019002'])
out['2000'] = dict(households=d['P018001'], married=d['P018008'] + d['P018009'], married_own=d['P018008'], any_u18=d['P019002'], source='2000 SF1 P18, P19')
d = api('2010/dec/sf1', ['P019001', 'P019008', 'P019009', 'P020001', 'P020002'])
out['2010'] = dict(households=d['P019001'], married=d['P019008'] + d['P019009'], married_own=d['P019008'], any_u18=d['P020002'], source='2010 SF1 P19, P20')
d = api('2020/dec/dhc', ['P20_001N', 'P20_002N', 'P20_003N', 'P21_001N', 'P21_002N'])
out['2020'] = dict(households=d['P20_001N'], married=d['P20_002N'], married_own=d['P20_003N'], any_u18=d['P21_002N'], source='2020 DHC P20, P21')

# ACS
acs = {}
for y in list(range(2006, 2020)) + [2021, 2022, 2023, 2024]:
    d = api(f'{y}/acs/acs1', ['B11001_001E', 'B11003_002E', 'B11003_003E', 'B11005_002E'])
    acs[y] = dict(households=d['B11001_001E'], married=d['B11003_002E'], married_own=d['B11003_003E'], any_u18=d['B11005_002E'], source=f'ACS {y} 1-year B11001, B11003, B11005')
out['acs'] = acs
json.dump(out, open(OUT, 'w'), indent=1)
for k, v in list(out.items())[:6]:
    print(k, {x: v[x] for x in ('households', 'married', 'married_own', 'any_u18')},
          round(v['married_own'] / v['households'] * 100, 1), v['any_u18'] and round(v['any_u18'] / v['households'] * 100, 1))
print('acs 2024', acs[2024], round(acs[2024]['married_own'] / acs[2024]['households'] * 100, 1), round(acs[2024]['any_u18'] / acs[2024]['households'] * 100, 1))
