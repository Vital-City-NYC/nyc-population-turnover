#!/usr/bin/env python3
# Title: New York City population turnover, 1970-2025 — data build
# Author: Josh Greenman, with coding by Claude Code (Anthropic)
# Date: 2026-09-15
# Data sources (all official; every file is kept verbatim in data/raw/):
#   U.S. Census Bureau, Population Estimates Program:
#     e7079co.txt (intercensal county estimates 1970-79), e8089co.txt (1980-89),
#     comp8090.txt (county components of change 1980-90),
#     api.census.gov/data/1990/pep/int_charagegroups (intercensal 1990-99 by age/sex/race),
#     2000c8_36.txt (CO-2000-8, county components 1990-2000, postcensal),
#     co-est00int-tot.csv (intercensal county totals 2000-2010),
#     co-est2009-alldata.csv (vintage 2009 components 2000-09),
#     co-est2020int-pop-36.xlsx (intercensal county totals 2010-2020), co-est2020-alldata.csv (vintage 2020 components 2010-20),
#     co-est2025-alldata.csv (vintage 2025 totals + components 2020-25),
#     co-asr-7079 (1970s county age/sex/race), pe-02 (1980s), co-est00int-alldata-36,
#     cc-est2020-alldata-36, cc-est2025-alldata-36 (age/sex/race/Hispanic).
#   U.S. Census Bureau, decennial census: 2000 SF3 P24 (residence in 1995), P21 (nativity),
#     2000 county-to-county migration flow files (1995-2000).
#   U.S. Census Bureau, American Community Survey 1-year, 2006-2024: B07001, B05002, B01001, B01002.
#   U.S. Census Bureau, ACS county-to-county migration flows, vintages 2010-2020 (5-year windows).
#   NYC Dept. of Health and Mental Hygiene, Summary of Vital Statistics 2023, Table PC1
#     (population, live births, deaths, 1898-2023).
#   NYC Dept. of City Planning, The Newest New Yorkers 2013, Table 2-1 (foreign-born 1900-2011).
#   Campbell Gibson and Kay Jung, Census Bureau Working Paper 76 (race/Hispanic 1970-1990),
#     via the compiled series in nyc-demographics-horserace/data/data.json.
# Description: parses the raw files into docs/data.json — one annual ledger 1970-2025
#   (population, births, deaths, implied net migration, gross in/out used by the turnover
#   model), decade ledgers, age structure, race/ethnicity, foreign-born, and inflow origins.
# Dependencies: Python 3.11+, standard library only.
import csv, json, os, re, statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'data', 'raw')
OUT = os.path.join(HERE, '..', 'docs', 'data.json')
NYC = ['36005', '36047', '36061', '36081', '36085']
NYC3 = ['005', '047', '061', '081', '085']
def num(s): return int(str(s).replace(',', '').strip())
def rp(name): return os.path.join(RAW, name)

# ---------------------------------------------------------------- population by year
pop = {}          # year -> July 1 population (April 1 count in census years), 5 boroughs
pop_src = {}      # year -> source label

def parse_blocks(fname, ncols):
    """Fixed-width Census text tables: blocks headed by a 'Code  Area Name  YYYY YYYY ...' line."""
    out = defaultdict(dict)
    years = None
    for line in open(rp(fname), encoding='latin-1'):
        m = re.match(r'^Code\s+Area Name\s+((?:\d{4}\s*)+)$', line.strip())
        if m:
            years = [int(y) for y in m.group(1).split()]
            continue
        m = re.match(r'^(36\d{3})\s+.*?((?:\s+\d+){%d})\s*$' % ncols, line.rstrip())
        if m and years and m.group(1) in NYC:
            vals = [int(v) for v in m.group(2).split()]
            for y, v in zip(years, vals):
                out[y][m.group(1)] = v
    return out

e70 = parse_blocks('e7079co.txt', 5)
e80 = parse_blocks('e8089co.txt', 5)
for y in range(1970, 1980):
    pop[y] = sum(e70[y][c] for c in NYC); pop_src[y] = 'census1970' if y == 1970 else 'intercensal70s'
for y in range(1980, 1990):
    pop[y] = sum(e80[y][c] for c in NYC); pop_src[y] = 'census1980' if y == 1980 else 'intercensal80s'
assert pop[1980] == 7071639, pop[1980]
pop1970_file = pop[1970]
pop[1970] = 7894862   # published 1970 count; the estimates file carries a modified count of 7,895,563

# 1990s: intercensal 1990-2000 by age/sex/race/Hispanic from the Census API — sum to totals
cag = json.load(open(rp('int_charagegroups_1990s.json')))
h = cag[0]; rows90 = [dict(zip(h, r)) for r in cag[1:]]
tot90 = defaultdict(int); age90 = defaultdict(lambda: defaultdict(int))
for r in rows90:
    y = 1900 + int(r['YEAR']); tot90[y] += int(r['POP']); age90[y][int(r['AGEGRP'])] += int(r['POP'])
for y in range(1990, 2000):
    pop[y] = tot90[y]; pop_src[y] = 'intercensal90s'
pop[1990] = 7322564; pop_src[1990] = 'census1990'   # April 1 count (intercensal 7/1/1990 differs by a few hundred)

# 2000s: intercensal county totals (consistent with both censuses)
for r in csv.DictReader(open(rp('co-est00int-tot.csv'), encoding='latin-1')):
    if r['STATE'] == '36' and r['COUNTY'].zfill(3) in NYC3:
        for y in range(2000, 2010):
            pop[y] = pop.get(y, 0) + int(r[f'POPESTIMATE{y}']); pop_src[y] = 'intercensal00s'
        pop[2010] = pop.get(2010, 0) + int(r['CENSUS2010POP']); pop_src[2010] = 'census2010'
pop[2000] = 8008278; pop_src[2000] = 'census2000'
assert pop[2010] == 8175133, pop[2010]

# 2010s: vintage-2020 file for components; population from the intercensal table below
v20 = defaultdict(int); comp = defaultdict(lambda: defaultdict(int))
stub2000 = defaultdict(int); stub2010 = defaultdict(int); stub2020 = defaultdict(int)
for r in csv.DictReader(open(rp('co-est2020-alldata.csv'), encoding='latin-1')):
    if r['STATE'] == '36' and r['COUNTY'] in NYC3:
        for y in range(2010, 2021):
            v20[y] += int(r[f'POPESTIMATE{y}'])
            if y >= 2011:   # BIRTHS2010 etc. cover only April-June 2010; full years run July-June
                for k in ('BIRTHS', 'DEATHS', 'INTERNATIONALMIG', 'DOMESTICMIG', 'RESIDUAL'):
                    comp[y][k] += int(r[f'{k}{y}'])
            else:
                for k in ('BIRTHS', 'DEATHS'): stub2010[k] += int(r[f'{k}{y}'])
census2020 = 8804190
closure2020 = census2020 - v20[2020]          # how far the vintage-2020 series fell short of the count (for the notes)
# Official 2010-2020 intercensal county estimates (Census Bureau table CO-EST2020INT-POP-36)
import openpyxl
ws = openpyxl.load_workbook(rp('co-est2020int-pop-36.xlsx')).active
int10 = defaultdict(int); hdr = None
for row in ws.iter_rows(values_only=True):
    if row[2] == 2010: hdr = list(row); continue
    if row[0] and any(k in str(row[0]) for k in ('Bronx County', 'Kings County', 'New York County', 'Queens County', 'Richmond County')):
        for i, y in enumerate(hdr):
            if isinstance(y, int) and 2010 <= y <= 2019: int10[y] += int(row[i])
        int10['census2020'] += int(row[12]); int10['base2010'] += int(row[1])
assert abs(int10['census2020'] - census2020) <= 100, int10['census2020']   # table's census column sums to 8,804,200 (post-count corrections); the page keeps the published 8,804,190
for y in range(2011, 2020):
    pop[y] = int10[y]; pop_src[y] = 'intercensal10s'
pop[2020] = census2020; pop_src[2020] = 'census2020'

# 2020s: vintage 2025 postcensal
v25 = defaultdict(int)
for r in csv.DictReader(open(rp('co-est2025-alldata.csv'), encoding='latin-1')):
    if r['STATE'] == '36' and r['COUNTY'] in NYC3:
        for y in range(2020, 2026):
            v25[y] += int(r[f'POPESTIMATE{y}'])
            if y >= 2021:   # 2020 column is the April-June 2020 stub
                for k in ('BIRTHS', 'DEATHS', 'INTERNATIONALMIG', 'DOMESTICMIG', 'RESIDUAL'):
                    comp[y][k] += int(r[f'{k}{y}'])
            else:
                for k in ('BIRTHS', 'DEATHS'): stub2020[k] += int(r[f'{k}{y}'])
for y in range(2021, 2026):
    pop[y] = v25[y]; pop_src[y] = 'v2025'

# Census components for 1990s (CO-2000-8, postcensal) and 2000s (vintage 2009, postcensal)
blk = {}
for line in open(rp('2000c8_36.txt'), encoding='latin-1'):
    m = re.match(r'^([1-9])\s+(36\d{3})\s+((?:\s*-?[\d,]+){12})', line)
    if m and m.group(2) in NYC:
        vals = [num(v) for v in m.group(3).split()]
        # columns: total 4/1/90-7/1/00, then 7/1/99..7/1/90 periods (each = year ending July 1), then 4/1/90-7/1/90
        blk.setdefault(int(m.group(1)), defaultdict(int))
        per = list(reversed(vals[1:11]))   # periods ending 7/1/1991 .. 7/1/2000
        for i, v in enumerate(per):
            blk[int(m.group(1))][1991 + i] += v        # PEP year y = period 7/1/(y-1) .. 7/1/y
        blk[int(m.group(1))]['stub'] += vals[11]       # 4/1/1990-7/1/1990
comp_names = {4: 'BIRTHS', 5: 'DEATHS', 6: 'INTERNATIONALMIG', 8: 'DOMESTICMIG', 9: 'RESIDUAL', 7: 'FEDERAL'}
for b, k in comp_names.items():
    for y in range(1991, 2001):
        comp[y][k] += blk[b][y]
for r in csv.DictReader(open(rp('co-est2009-alldata.csv'), encoding='latin-1')):
    if r['STATE'] == '36' and r['COUNTY'] in NYC3:
        for y in range(2001, 2010):   # BIRTHS_2000 etc. are the April-June 2000 stub
            for k in ('BIRTHS', 'DEATHS', 'INTERNATIONALMIG', 'DOMESTICMIG', 'RESIDUAL'):
                comp[y][k] += int(r[f'{k}_{y}'] if f'{k}_{y}' in r else r[f'{k}{y}'])
        for k in ('BIRTHS', 'DEATHS'): stub2000[k] += int(r[f'{k}_2000'] if f'{k}_2000' in r else r[f'{k}2000'])
# 1980-90 decade components (comp8090 record A: pop80, pop90, change, pct, births, deaths, netmig, pct)
c8090 = defaultdict(int)
c8090_b = defaultdict(int); c8090_d = defaultdict(int)   # record B: ten birth periods then ten death periods
for line in open(rp('comp8090.txt'), encoding='latin-1'):
    m = re.match(r'^A (36\d{3})\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?[\d.]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', line)
    if m and m.group(1) in NYC:
        c8090['pop80'] += int(m.group(2)); c8090['pop90'] += int(m.group(3))
        c8090['births'] += int(m.group(6)); c8090['deaths'] += int(m.group(7)); c8090['netmig'] += int(m.group(8))
    mb = re.match(r'^B (36\d{3})\s+((?:\d+\s*){20})$', line.rstrip())
    if mb and mb.group(1) in NYC:
        v = [int(x) for x in mb.group(2).split()]
        # periods: 0 = April 1, 1980-June 30, 1981; 1-8 = July-June years ending 1983..1990? no: 1982..1989; 9 = July 1989-March 1990
        for i in range(10): c8090_b[1980 + i] += v[i]; c8090_d[1980 + i] += v[10 + i]
assert sum(c8090_b.values()) == c8090['births'] and sum(c8090_d.values()) == c8090['deaths'], (sum(c8090_b.values()), c8090['births'])

PEP_YEARS = set(range(1991, 2001)) | set(range(2001, 2010)) | set(range(2011, 2021)) | set(range(2021, 2026))
PEP_YEARS_ALL = PEP_YEARS
# ---------------------------------------------------------------- births and deaths, by residence
# Each ledger row t covers the interval between its population dates: July 1 t to July 1 t+1, except that
# census years anchor on April 1 (so row 1980 = April 1980-July 1981, 15 months; row 1989 = July 1989-
# April 1990, 9 months). Births and deaths are counted for residents of the five boroughs.
#   1970-79: DOHMH Table PC1 counts (events occurring in the city, any residence), scaled to a residence
#            basis by the 1980s ratio of NCHS resident counts to DOHMH occurrence counts (see methodology).
#   1980-89: Census Bureau comp8090 record B (NCHS resident births and deaths by estimate period).
#   1990-2024: Census Bureau components of change (NCHS resident counts), periods ending June 30 of t+1,
#            plus the April-June stub in census years; July 2009-March 2010 has no Census file and uses the
#            New York State Health Department's resident counts for calendar 2009 and 2010.
dohmh_b = {}; dohmh_d = {}
pc1 = open(rp('dohmh_2023sum_tablePC1_page53.txt')).read()
for line in pc1.splitlines():
    m = re.match(r'^(\d{4})(?:-(\d{4}))?[‡]?\s', line)
    if not m or 'Excluding' in line: continue
    tok = line.split(); y0 = int(m.group(1)); y1 = int(m.group(2)) if m.group(2) else y0
    if y1 < 1966: continue
    b = num(tok[2]); dd = num(tok[-4])
    for y in range(y0, y1 + 1):
        if y in dohmh_b: continue          # first 2001 row (with World Trade Center deaths) wins
        dohmh_b[y] = b; dohmh_d[y] = dd
assert dohmh_b[1990] == 139630 and dohmh_d[2020] == 82143 and dohmh_d[2001] == 62964
nys = {int(k): v for k, v in json.load(open(rp('nysdoh/nyc_resident_births_deaths.json'))).items()}
births = {}; deaths = {}; bd_src = {}; bd_period = {}
# 1970s: scale occurrence counts to residence with the 1980s ratio (NCHS / DOHMH, calendar 1980-89 vs April 1980-April 1990)
r_b = c8090['births'] / sum(dohmh_b[y] for y in range(1980, 1990))
r_d = c8090['deaths'] / sum(dohmh_d[y] for y in range(1980, 1990))
for y in range(1970, 1980):
    span = 1.25 if y == 1970 else 1.0   # row 1970 runs April 1970-July 1971
    births[y] = round(dohmh_b[y] * r_b * span); deaths[y] = round(dohmh_d[y] * r_d * span)
    bd_src[y] = 'dohmh_scaled'; bd_period[y] = 'April 1970 to July 1971' if y == 1970 else f'July {y} to June {y+1}'
births[1979] = round(dohmh_b[1979] * r_b * 0.75); deaths[1979] = round(dohmh_d[1979] * r_d * 0.75); bd_period[1979] = 'July 1979 to March 1980'
for y in range(1980, 1990):
    births[y] = c8090_b[y]; deaths[y] = c8090_d[y]; bd_src[y] = 'nchs_census'
    bd_period[y] = 'April 1980 to June 1981' if y == 1980 else ('July 1989 to March 1990' if y == 1989 else f'July {y} to June {y+1}')
for y in range(1990, 2025):
    p = y + 1
    if p in comp and p in PEP_YEARS_ALL:
        births[y] = comp[p]['BIRTHS']; deaths[y] = comp[p]['DEATHS']; bd_src[y] = 'nchs_census'; bd_period[y] = f'July {y} to June {y+1}'
    else:
        births[y] = None; deaths[y] = None
# rows that end at a census (July 1999-April 2000, July 2019-April 2020): nine-twelfths of the July-June count
for y in (1999, 2019):
    births[y] = round(births[y] * 0.75); deaths[y] = round(deaths[y] * 0.75); bd_period[y] = f'July {y} to March {y+1}'
MONTHS = {y: 12 for y in range(1970, 2026)}
for y in (1970, 1980, 1990, 2000, 2010, 2020): MONTHS[y] = 15
for y in (1979, 1989, 1999, 2009, 2019): MONTHS[y] = 9
MONTHS[2025] = 0
# census-year stubs (April 1-June 30) belong to the row that starts at the census
births[1990] += blk[4]['stub']; deaths[1990] += blk[5]['stub']; bd_period[1990] = 'April 1990 to June 1991'
births[2000] += stub2000['BIRTHS']; deaths[2000] += stub2000['DEATHS']; bd_period[2000] = 'April 2000 to June 2001'
births[2010] += stub2010['BIRTHS']; deaths[2010] += stub2010['DEATHS']; bd_period[2010] = 'April 2010 to June 2011'
births[2020] += stub2020['BIRTHS']; deaths[2020] += stub2020['DEATHS']; bd_period[2020] = 'April 2020 to June 2021'
# July 2009-March 2010: no Census component file; nine months at the state's resident counts for 2009-10
births[2009] = round(0.75 * (nys[2009]['births'] + nys[2010]['births']) / 2); deaths[2009] = round(0.75 * (nys[2009]['deaths'] + nys[2010]['deaths']) / 2)
bd_src[2009] = 'nysdoh'; bd_period[2009] = 'July 2009 to March 2010'
births[2025] = None; deaths[2025] = None; bd_src[2025] = 'none'; bd_period[2025] = 'July 2025 onward, not yet published'

# ---------------------------------------------------------------- gross in-migration anchors
# ACS 1-year 2006-2024 (2005 used a different table layout and is not used)
acs = {}
for y in list(range(2006, 2020)) + [2021, 2022, 2023, 2024]:
    d = json.load(open(rp(f'acs/acs1_{y}.json'))); r = dict(zip(d[0], d[1]))
    acs[y] = {k: int(r[k]) for k in r if k.startswith('B0') and k != 'B01002_001E'}
    acs[y]['medage'] = float(r['B01002_001E'])
# ACS county-to-county flows: share of "different county, same state" arrivals who came from
# outside the five boroughs (vs. from another borough), per 5-year window
flow_win = {}
for v in range(2010, 2021):
    d = json.load(open(rp(f'flows/flows_{v}.json'))); h = d[0]
    agg = dict(dom_in=0, abroad_in=0, dom_out=0, intra=0, nys_in=0, state_in=defaultdict(int))
    for row in d[1:]:
        r = dict(zip(h, row)); g2 = r['GEOID2'] or ''; mi = int(r['MOVEDIN'] or 0); mo = int(r['MOVEDOUT'] or 0)
        if g2 in NYC: agg['intra'] += mi; continue
        if r['MOVEDOUT'] is None and r['MOVEDNET'] is None: agg['abroad_in'] += mi; continue
        agg['dom_in'] += mi; agg['dom_out'] += mo
        if g2.startswith('36'): agg['nys_in'] += mi
        agg['state_in'][g2[:2]] += mi
    agg['share_nonnyc'] = agg['nys_in'] / (agg['nys_in'] + agg['intra'])
    agg['state_in'] = dict(agg['state_in'])
    flow_win[v] = dict(window=f'{v-4}-{v}', mid=v - 2, **agg)
def share_for(y):
    mids = sorted(w['mid'] for w in flow_win.values())
    m = min(mids, key=lambda x: abs(x - y))
    return next(w['share_nonnyc'] for w in flow_win.values() if w['mid'] == m)
# 2000 census: residence in 1995 (people 5+) and county-to-county flows 1995-2000
sf3 = json.load(open(rp('sf3_2000_nyc_mobility_nativity.json'))); sf3 = dict(zip(sf3[0], sf3[1]))
c2c_in = defaultdict(int); c2c_out = defaultdict(int)
for line in open(rp('c2c2000_inflow_nyc.txt'), encoding='latin-1'):
    p = line.split()
    if p[0] in NYC and p[1] not in NYC: c2c_in['dom'] += int(p[2]); c2c_in['nys' if p[1].startswith('36') else 'other'] += int(p[2])
for line in open(rp('c2c2000_outflow_nyc.txt'), encoding='latin-1'):
    p = line.split()
    if p[0] in NYC and p[1] not in NYC: c2c_out['dom'] += int(p[2])
assert c2c_in['other'] == int(sf3['P024008']), (c2c_in['other'], sf3['P024008'])   # flows tie to SF3 different-state
c2c_in['abroad'] = int(sf3['P024016']) + int(sf3['P024013'])   # foreign country/at sea + island areas + Puerto Rico
c2c_in['total'] = c2c_in['dom'] + c2c_in['abroad']

PEP_YEARS = set(range(1991, 2001)) | set(range(2001, 2010)) | set(range(2011, 2021)) | set(range(2021, 2026))
PEP_YEARS_ALL = PEP_YEARS
# ---------------------------------------------------------------- annual ledger + turnover inputs
years = list(range(1970, 2026))
ledger = []
in_meas = {}   # measured gross in-migration from outside NYC (people/year)
for y in acs:
    a = acs[y]
    in_meas[y] = dict(value=a['B07001_065E'] + a['B07001_081E'] + round(a['B07001_049E'] * share_for(y)),
                      source='acs', other_state=a['B07001_065E'], abroad=a['B07001_081E'],
                      rest_of_state=round(a['B07001_049E'] * share_for(y)), share=round(share_for(y), 3))
for y in range(1995, 2000):
    in_meas[y] = dict(value=round(c2c_in['total'] / 5), source='census2000', other_state=round(c2c_in['other'] / 5),
                      abroad=round(c2c_in['abroad'] / 5), rest_of_state=round(c2c_in['nys'] / 5))
rate_first = in_meas[1995]['value'] / pop[1995]
rate_2006 = in_meas[2006]['value'] / pop[2006]
for y in years:
    P = pop[y]; Pn = pop.get(y + 1)
    b = births[y]; d = deaths[y]
    net = (Pn - P) - (b - d) if (Pn is not None and b is not None) else None
    if y in in_meas:
        inn = in_meas[y]['value']; isrc = in_meas[y]['source']
    elif y == 2020:
        inn = round((in_meas[2019]['value'] + in_meas[2021]['value']) / 2); isrc = 'interp'
    elif y == 2025:
        inn = round(in_meas[2024]['value'] / pop[2024] * P); isrc = 'carried'
    elif 2000 <= y <= 2005:
        t = (y - 1999) / 7; inn = round(P * (rate_first * (1 - t) + rate_2006 * t)); isrc = 'interp'
    else:
        inn = round(P * rate_first); isrc = 'assumed'
    out = (inn - net) if net is not None else None
    if out is not None and out < 0: out = 0
    ledger.append(dict(year=y, pop=P, pop_src=pop_src[y], births=b, deaths=d, bd_src=bd_src[y], period=bd_period[y], months=MONTHS[y],
                       net=net, inflow=inn, in_src=isrc, outflow=out,
                                          pep_intl=comp[y]['INTERNATIONALMIG'] if y in PEP_YEARS else None,
                       pep_dom=comp[y]['DOMESTICMIG'] if y in PEP_YEARS else None,
                       pep_period=f'July {y-1} to June {y}' if y in PEP_YEARS else None))

# ---------------------------------------------------------------- decade ledgers
dec_bounds = [1970, 1980, 1990, 2000, 2010, 2020, 2025]
decades = []
for a, z in zip(dec_bounds[:-1], dec_bounds[1:]):
    rows = [r for r in ledger if a <= r['year'] < z]
    B = sum(r['births'] for r in rows if r['births'] is not None); D = sum(r['deaths'] for r in rows if r['deaths'] is not None)
    net = (pop[z] - pop[a]) - (B - D)
    pys = [y for y in range(a + 1, z + 1) if y in PEP_YEARS]
    pep = dict(births=sum(comp[y]['BIRTHS'] for y in pys), deaths=sum(comp[y]['DEATHS'] for y in pys),
               intl=sum(comp[y]['INTERNATIONALMIG'] for y in pys), dom=sum(comp[y]['DOMESTICMIG'] for y in pys),
               years=len(pys), period=f'July {pys[0]-1} to June {pys[-1]}') if pys else None
    if a == 1980: pep = dict(births=c8090['births'], deaths=c8090['deaths'], intl=None, dom=None, netmig=c8090['netmig'], years=10, period='April 1980 to April 1990')
    decades.append(dict(start=a, end=z, pop_start=pop[a], pop_end=pop[z], change=pop[z] - pop[a], births=B, deaths=D,
                        natural=B - D, net=net, inflow=sum(r['inflow'] for r in rows), outflow=sum(r['outflow'] for r in rows),
                        pep=pep, years=z - a))

# ---------------------------------------------------------------- age structure
AGE_BINS = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+']
def age_summary(bins18, label, src):
    tot = sum(bins18)
    g = dict(under15=sum(bins18[0:3]), a15_24=sum(bins18[3:5]), a25_44=sum(bins18[5:9]), a45_64=sum(bins18[9:13]), a65=sum(bins18[13:]))
    # median from 5-year bins by linear interpolation within the bin that crosses the midpoint
    half = tot / 2; c = 0
    for i, v in enumerate(bins18):
        if c + v >= half:
            lo = i * 5; width = 5 if i < 17 else 15
            med = lo + width * (half - c) / v; break
        c += v
    return dict(year=label, total=tot, bins=bins18, shares={k: round(v / tot * 100, 1) for k, v in g.items()}, median=round(med, 1), source=src)
ages = []
b70 = [0] * 18
for r in csv.reader(open(rp('co-asr-7079-nyc.csv'))):
    if r[0] == '1970':
        for i in range(18): b70[i] += int(r[3 + i])
ages.append(age_summary(b70, 1970, 'Census Bureau county estimates by age, sex and race (co-asr-7079), April 1, 1970 modified count'))
b80 = [0] * 18
for r in csv.reader(open(rp('pe-02-nyc.csv'))):
    if r[0] == '1980':
        for i in range(18): b80[i] += int(r[3 + i])
ages.append(age_summary(b80, 1980, 'Census Bureau intercensal county estimates by age, sex and race 1980-89 (PE-02), July 1, 1980'))
a90 = age90[1990]; b90 = [a90[0] + a90[1]] + [a90[i] for i in range(2, 19)]
ages.append(age_summary(b90, 1990, 'Census Bureau intercensal county estimates 1990-2000 (API int_charagegroups), July 1, 1990'))
def agesum(fname, year_code, zero_is_under1=False):
    """cc-est files: AGEGRP 0 = total, 1-18 = five-year groups. The 2000-2010 intercensal state file instead
    uses 99 = total, 0 = under 1 year, 1 = 1-4 years, 2-18 = five-year groups (verified: Manhattan codes 0+1 =
    76,098, the census under-5 count), so code 0 is folded into the 0-4 bin there."""
    b = [0] * 18
    for r in csv.DictReader(open(rp(fname), encoding='latin-1')):
        if r['COUNTY'] in NYC3 and r['YEAR'] == str(year_code) and r['AGEGRP'] != '99':
            g = int(r['AGEGRP'])
            if g == 0:
                if zero_is_under1: b[0] += int(r['TOT_POP'])
                continue
            b[g - 1] += int(r['TOT_POP'])
    return b
ages.append(age_summary(agesum('co-est00int-alldata-36.csv', 1, zero_is_under1=True), 2000, 'Census Bureau intercensal county characteristics 2000-2010, April 1, 2000 estimates base'))
ages.append(age_summary(agesum('cc-est2020-alldata-36.csv', 1), 2010, 'Census Bureau county characteristics vintage 2020, April 1, 2010 census'))
ages.append(age_summary(agesum('cc-est2025-alldata-36.csv', 1), 2020, 'Census Bureau county characteristics vintage 2025, April 1, 2020 estimates base'))
ages.append(age_summary(agesum('cc-est2025-alldata-36.csv', 7), 2025, 'Census Bureau county characteristics vintage 2025, July 1, 2025 estimate'))

# ---------------------------------------------------------------- race / Hispanic origin
hr = json.load(open(os.path.join(HERE, '..', '..', 'nyc-demographics-horserace', 'data', 'data.json')))
race = []
for i, y in enumerate(hr['years']):
    if y < 1970: continue
    g = {x['id']: x['pct'][i] for x in hr['groups']}
    if y == 2020: g['asian'] = round((1385144 + 6874) / 8804190 * 100, 2)   # DHC P3: Asian alone + Native Hawaiian/Pacific Islander alone, to match the API definition used for 1970-2010
    race.append(dict(year=y, total=hr['totals'][i], hispanic=g['hispanic'], nh_white=hr['nhwhite']['pct'][i], black=g['black'], asian=g['asian'], white=g['white'], other=g['other'],
                     source='Decennial census (Gibson and Jung WP76 for 1970-1990; SF1/P.L. 94-171 for 2000-2020)'))

# ---------------------------------------------------------------- foreign-born
fb = []
for line in open(rp('dcp_nny2013_table2-1_page20.txt')).read().splitlines():
    m = re.match(r'^(19[789]0|2000|2011)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s', line)
    if m and int(m.group(1)) < 2011:
        fb.append(dict(year=int(m.group(1)), total=num(m.group(2)), foreign_born=num(m.group(3)), share=float(m.group(4)), source='Decennial census via NYC Dept. of City Planning, The Newest New Yorkers 2013, Table 2-1'))
assert fb[-1]['foreign_born'] == int(sf3['P021013'])   # 2000 ties to SF3 P21
for y in sorted(acs):
    fb.append(dict(year=y, total=acs[y]['B01001_001E'], foreign_born=acs[y]['B05002_013E'], share=round(acs[y]['B05002_013E'] / acs[y]['B01001_001E'] * 100, 1), source=f'ACS {y} 1-year, B05002'))

# ---------------------------------------------------------------- turnover model (mirrors the page's JavaScript)
def turnover(A, B):
    """Cohort-survival model. Every resident faces the same yearly exit rate (deaths + out-moves) / population.
    Arrivals in a year are not exposed to that year's exits. Stocks sum exactly to the end-year population."""
    L = {r['year']: r for r in ledger}
    orig, born, moved = float(pop[A]), 0.0, 0.0
    sums = dict(births=0, deaths=0, inflow=0, outflow=0, assumed_years=0)
    for t in range(A, B):
        r = L[t]; f = 1 - (r['deaths'] + r['outflow']) / r['pop']
        orig *= f; born *= f; moved *= f
        born += r['births']; moved += r['inflow']
        for k in ('births', 'deaths', 'inflow', 'outflow'): sums[k] += r[k]
        sums['assumed_years'] += r['in_src'] == 'assumed'
    return dict(start=A, end=B, pop_start=pop[A], pop_end=pop[B], stayers=round(orig), born=round(born), moved=round(moved),
                new_share=round((1 - orig / pop[B]) * 100, 1), gone_share=round((1 - orig / pop[A]) * 100, 1), **sums)
examples = {f'{a}-{b}': turnover(a, b) for a, b in [(1970, 2025), (2001, 2013), (2001, 2025), (2001, 2026 - 1), (1990, 2000), (2010, 2020), (2020, 2025), (1995, 2000)]}

# ---------------------------------------------------------------- summary numbers for the page
first, last = ledger[0], ledger[-1]
# Totals cover calendar years 1970-2024, the 55 years whose net-migration residuals sum to the
# April 1970 to July 2025 population change (the 2025 row has no following year to difference).
L55 = [r for r in ledger if r['year'] <= 2024]
tot = dict(years='April 1970 to July 2025', births=sum(r['births'] for r in L55), deaths=sum(r['deaths'] for r in L55),
           net=(pop[2025] - pop[1970]) - (sum(r['births'] for r in L55) - sum(r['deaths'] for r in L55)),
           inflow=sum(r['inflow'] for r in L55), outflow=sum(r['outflow'] for r in L55))
assert tot['net'] == sum(r['net'] for r in L55)

data = dict(
    meta=dict(built='2026-09-15', years=[1970, 2025], census2020=census2020, closure2020=closure2020, v2020_2020=v20[2020],
              pop1970_published=7894862, pop1970_file=pop1970_file),
    ledger=ledger, decades=decades, ages=ages, race=race, foreign_born=fb, totals=tot,
    flows=flow_win, c2c2000=dict(in_dom=c2c_in['dom'], in_other_state=c2c_in['other'], in_rest_of_state=c2c_in['nys'], in_abroad=c2c_in['abroad'], out_dom=c2c_out['dom'],
                                 pop5plus=int(sf3['P024001']), same_house=int(sf3['P024002'])),
    acs_medage={y: acs[y]['medage'] for y in acs}, comp8090=dict(c8090), examples=examples,
    inflow_parts={y: {k: v for k, v in in_meas[y].items() if k in ('other_state', 'abroad', 'rest_of_state', 'share', 'source')} for y in in_meas})
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w'), separators=(',', ':'))

# ---------------------------------------------------------------- printed cross-checks
print('closure 2020 (census minus vintage-2020 estimate):', closure2020, '| intercensal 2015/2019:', int10[2015], int10[2019])
print('pop:', {y: pop[y] for y in (1970, 1975, 1980, 1990, 2000, 2010, 2015, 2019, 2020, 2021, 2025)})
print('totals 1970-2025:', tot)
print('decades:')
for d in decades:
    print(f"  {d['start']}-{d['end']}: pop {d['pop_start']:,}->{d['pop_end']:,} births {d['births']:,} deaths {d['deaths']:,} net {d['net']:,} | PEP {d['pep']}")
print('in-migration sources by year:', {r['year']: r['in_src'] for r in ledger})
print('ages:'); [print(' ', a['year'], a['shares'], 'median', a['median'], 'total', a['total']) for a in ages]
print('race:'); [print(' ', r['year'], r['hispanic'], r['nh_white'], r['black'], r['asian']) for r in race]
print('fb:', [(f['year'], f['share']) for f in fb])
print('c2c2000:', data['c2c2000'])
print('flows:', {v: (w['dom_in'], w['abroad_in'], w['dom_out'], round(w['share_nonnyc'], 3)) for v, w in flow_win.items()})
print('1980s decade check: rows 1980-89 births', sum(births[y] for y in range(1980,1990)), 'vs comp8090', c8090['births'], '| deaths', sum(deaths[y] for y in range(1980,1990)), 'vs', c8090['deaths'])
print('1970s scaling ratios (NCHS/DOHMH, 1980s): births', round(r_b,4), 'deaths', round(r_d,4))
print('Residence (Census/NCHS, July-June) vs state resident counts (calendar): two-year averages')
for y in (2005, 2010, 2015, 2019, 2022):
    if y in nys and y+1 in nys and nys[y].get('deaths') and nys[y+1].get('deaths'):
        print(f'  {y}-{y+1}: Census births (annual rate)', round(births[y]*12/MONTHS[y]), 'vs state avg', round((nys[y]['births']+nys[y+1]['births'])/2), '| deaths', round(deaths[y]*12/MONTHS[y]), 'vs', round((nys[y]['deaths']+nys[y+1]['deaths'])/2))
print('Occurrence (DOHMH PC1) vs residence (state), calendar years:')
for y in (2005, 2010, 2015, 2019, 2023): print(f'  {y}: DOHMH births {dohmh_b[y]} vs state {nys[y]["births"]} ({round((dohmh_b[y]/nys[y]["births"]-1)*100,1)}% higher); deaths {dohmh_d[y]} vs {nys[y].get("deaths")}')
print('turnover examples:'); [print(' ', k, v) for k, v in examples.items()]
chk = turnover(1995, 2000); print('1995-2000 model newcomers (moved) still present', chk['moved'], 'vs census 2000 residents 5+ who lived outside NYC in 1995:', c2c_in['total'])
print('min natural increase row (annual rate):', min(((r['births']-r['deaths'])*12/r['months'], r['year']) for r in ledger if r['births'] is not None))
print('births peak row since 2000 (annual rate):', max((round(r['births']*12/r['months']), r['year']) for r in ledger if r['year']>=2000 and r['births'] is not None), '| 2024 row', [(r['year'], r['births']) for r in ledger if r['year']==2024])
print('1970s ratios births', round(r_b,4), 'deaths', round(r_d,4), '| stubs', dict(stub2000), dict(stub2010), dict(stub2020), 'stub1990', blk[4]['stub'], blk[5]['stub'])
