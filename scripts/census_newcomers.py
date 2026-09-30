"""Newcomers counted by the 1980 and 1990 censuses: residents of the five boroughs aged 5 and over who
lived outside New York City five years earlier (elsewhere in New York State, another state, Puerto Rico or
abroad). These are the targets the turnover model's arrival rates are calibrated to for 1975-80 and 1985-90,
alongside the 2000 census figure computed in build_data.py.

Source: the Census Bureau's Public Use Microdata Samples (A samples, 5 percent), downloaded from
www2.census.gov. The files are large (about 300 MB and 240 MB unzipped), so they are cached in data/cache/
(not committed); the tabulated counts are written to data/raw/fix/census_newcomers_1980_1990.json.

1990 record layout: DOCUMENT/PUMSUSDD.doc on the same server. Housing record: PUMA columns 13-17 (the first
three digits identify the county: 050 Bronx, 051 Manhattan, 052 Staten Island, 053 Brooklyn, 054 Queens).
Person record: AGE 15-16, PWGT1 18-21, MIGSTATE 60-61, MIGPUMA 62-66.

1980 record layout: 1980 PUMS technical documentation (reproduced by IPUMS as 1980_PUMS_codebook.pdf).
Records are 193 characters with no line breaks. Housing record: county group columns 6-8 (036 Bronx,
037 Brooklyn, 038 Manhattan, 039 Queens, 040 Staten Island). Person record: AGE 8-9; migration items were
asked of half the sample (MIGWGT column 46 = 2), so those records carry twice the constant weight of 20;
STATE75 47-48 (97 abroad, 98 same house, 72 Puerto Rico, 73 outlying areas); COGRP75 49-51 (999 same house).

Each count is scaled by the census total over the sample's weighted total for the city.
"""
import io, json, os, urllib.request, zipfile
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), '..')
CACHE = os.path.join(ROOT, 'data', 'cache')
OUT = os.path.join(ROOT, 'data', 'raw', 'fix', 'census_newcomers_1980_1990.json')
URL90 = 'https://www2.census.gov/census_1990/1990_PUMS_A/PUMSAXNY.zip'
URL80 = 'https://www2.census.gov/census_1980/pums_1980_a/PUMSAXNY.ZIP'
CENSUS = {1980: 7071639, 1990: 7322564}


def fetch(url, member_suffix, year):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f'{year}_{os.path.basename(url)}')   # both files are named PUMSAXNY; macOS ignores case
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    z = zipfile.ZipFile(path)
    name = next(n for n in z.namelist() if n.upper().endswith(member_suffix))
    return z.read(name).decode('latin-1')


def tab1990():
    data = fetch(URL90, '.TXT', 1990)
    nyc = {'050', '051', '052', '053', '054'}
    c = Counter(); puma = None
    for line in data.splitlines():
        if line[0] == 'H':
            puma = line[12:17]
        elif line[0] == 'P' and puma[:3] in nyc:
            w = int(line[17:21]); c['weighted_total'] += w
            if int(line[14:16]) < 5:
                continue
            c['age5plus'] += w
            st, mp = line[59:61], line[61:66]
            if st == '00': c['same_house'] += w
            elif st == '36' and mp[:3] in nyc: c['other_house_in_city'] += w
            elif st == '36': c['rest_of_state'] += w
            elif st == '72': c['puerto_rico'] += w
            elif st == '98': c['abroad'] += w
            elif st == '99': c['not_identified'] += w
            else: c['other_state'] += w
    return c


def tab1980():
    data = fetch(URL80, '.NY', 1980)
    R = 193
    assert len(data) % R == 0, len(data) % R
    nyc = {'036', '037', '038', '039', '040'}
    c = Counter(); cg = None
    for i in range(0, len(data), R):
        line = data[i:i + R]
        if line[0] == 'H':
            cg = line[5:8]
        elif line[0] == 'P' and cg in nyc:
            c['weighted_total'] += 20
            if int(line[7:9]) < 5:
                continue
            if line[45] != '2':
                continue                      # not in the migration half-sample
            w = 40; c['age5plus'] += w
            st, g = line[46:48], line[48:51]
            if st == '98' or g == '999': c['same_house'] += w
            elif st == '36' and g in nyc: c['other_house_in_city'] += w
            elif st == '36': c['rest_of_state'] += w
            elif st == '72': c['puerto_rico'] += w
            elif st == '97': c['abroad'] += w
            elif st == '73': c['outlying_areas'] += w
            elif st == '00': c['not_applicable'] += w
            else: c['other_state'] += w
    return c


out = {}
for year, fn in ((1980, tab1980), (1990, tab1990)):
    c = fn()
    new = sum(c[k] for k in ('rest_of_state', 'other_state', 'puerto_rico', 'abroad', 'outlying_areas'))
    scale = CENSUS[year] / c['weighted_total']
    out[year] = dict(sample=dict(c), newcomers_sample=new, share_of_age5plus=round(new / c['age5plus'], 5),
                     scale_to_census=round(scale, 5), newcomers=round(new * scale),
                     source=URL80 if year == 1980 else URL90)
    print(year, out[year]['newcomers'], out[year]['share_of_age5plus'], dict(c))
json.dump(out, open(OUT, 'w'), indent=1)
print('wrote', OUT)
