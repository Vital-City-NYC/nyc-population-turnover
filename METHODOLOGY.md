# Methodology: New York City's population since 1970, and the turnover calculator

Built September 15, 2026. Every figure on the page comes from the U.S. Census Bureau, the New York City Department of Health and Mental Hygiene or the New York City Department of City Planning. The raw files are kept verbatim in `data/raw/`. `scripts/build_data.py` turns them into `docs/data.json`; `scripts/build_page.py` inlines that into `docs/index.html`. Re-running the two scripts reproduces the page.

## 1. Sources

| Series | Source | File in `data/raw/` | Notes |
|---|---|---|---|
| Population 1970-79 | Census Bureau, [Preliminary Estimates of the Intercensal Population of Counties 1970-1979](https://www2.census.gov/programs-surveys/popest/tables/1900-1980/counties/totals/e7079co.txt) (issued April 1982), five NYC counties summed | `e7079co.txt` | Rounded to hundreds. The 1970 figure in the file is a modified count of 7,895,563; the page uses the published 1970 count of 7,894,862. |
| Population 1980-89 | Census Bureau, [Intercensal Estimates of the Resident Population of States and Counties 1980-1989](https://www2.census.gov/programs-surveys/popest/tables/1980-1990/counties/totals/e8089co.txt) (issued March 1992) | `e8089co.txt` | |
| Population 1990-99 | Census Bureau, 1990-2000 intercensal county estimates by age, sex, race and Hispanic origin, via [`api.census.gov/data/1990/pep/int_charagegroups`](https://api.census.gov/data/1990/pep/int_charagegroups.html), summed over all cells | `int_charagegroups_1990s.json` | Consistent with both the 1990 and 2000 counts. |
| Population 2000-09 | Census Bureau, [Intercensal Estimates of the Resident Population for Counties, April 1, 2000 to July 1, 2010](https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-tot.csv) | `co-est00int-tot.csv` | Consistent with both the 2000 and 2010 counts. |
| Population 2010-19 | Census Bureau, [Intercensal Estimates of the Resident Population for Counties in New York: April 1, 2010 to April 1, 2020](https://www2.census.gov/programs-surveys/popest/tables/2010-2020/intercensal/county/co-est2020int-pop-36.xlsx) (table CO-EST2020INT-POP-36) | `co-est2020int-pop-36.xlsx` | Consistent with both the 2010 and 2020 counts. The vintage 2020 file (`co-est2020-alldata.csv`) is kept only for its components of change. |
| Population 2020-25 | Census Bureau, [vintage 2025 county estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv) (file dated March 26, 2026) | `co-est2025-alldata.csv` | Postcensal; 2020 uses the census count. Identical, county by county, to the figures in the NYC Department of City Planning's [New York City's Population Estimates and Trends, July 2026 release](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-july-2026.pdf) (`dcp_population_estimates_and_trends_july2026.pdf`). |
| Census counts | 1970: 7,894,862; 1980: 7,071,639; 1990: 7,322,564; 2000: 8,008,278; 2010: 8,175,133; 2020: 8,804,190 | | April 1 counts. |
| Births and deaths 1970-2023 | NYC DOHMH, [Summary of Vital Statistics 2023](https://www.nyc.gov/assets/doh/downloads/pdf/vs/2023sum.pdf), Table PC1 "Population, Live Births, Fertility Rates, Marriages, Deaths, and Infant Mortality, New York City, 1898-2023" | `dohmh_2023sum_tablePC1_page53.txt` (text of page 53 of `2023sum.pdf`) | Births and deaths to city residents. 1966-70, 1971-75 and 1976-80 are published as five-year averages; the page assigns each year in those spans the average (1970 uses the 1966-70 average). 2001 deaths include the World Trade Center deaths (62,964). |
| Births and deaths 2024-25 | Census Bureau vintage 2025 county components of change | `co-est2025-alldata.csv` | Years ending June 30. DOHMH has not published 2024 or 2025. |
| Census Bureau components of change | [CO-2000-8](https://www2.census.gov/programs-surveys/popest/tables/1990-2000/estimates-and-change-1990-2000/2000c8_36.txt) (1990-2000 county components, `2000c8_36.txt`); [vintage 2009](https://www2.census.gov/programs-surveys/popest/datasets/2000-2009/counties/totals/co-est2009-alldata.csv) (`co-est2009-alldata.csv`); vintage 2020; vintage 2025; [comp8090](https://www2.census.gov/programs-surveys/popest/datasets/1980-1990/counties/totals/comp8090.zip) (1980-90 county components, `comp8090.txt`) | | Used only for the international/domestic split and cross-checks. All are July-to-June years except comp8090. |
| Arrivals 2006-24 | Census Bureau, American Community Survey 1-year, [table B07001](https://data.census.gov/table/ACSDT1Y2024.B07001?g=160XX00US3651000) (Geographic Mobility in the Past Year by Age), New York city, plus [B05002](https://data.census.gov/table/ACSDT1Y2024.B05002?g=160XX00US3651000), B01001, B01002 | `acs/acs1_YYYY.json` | Population aged 1 and over. No 2020 1-year release. The 2005 ACS used a different table layout and is not used. |
| Inter-borough share of in-state movers | Census Bureau, [ACS county-to-county migration flows](https://www.census.gov/data/developers/data-sets/acs-migration-flows.html), vintages 2010 (2006-2010) through 2020 (2016-2020), five NYC counties | `flows/flows_YYYY.json` | Later vintages publish only state-level rows. |
| Arrivals 1995-2000 | 2000 census, [county-to-county migration flow files](https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/2000/county-to-county-flows/) (inflow and outflow), NYC rows only; 2000 Summary File 3 [table P24](https://api.census.gov/data/2000/dec/sf3/variables.html) (Residence in 1995), New York city | `c2c2000_inflow_nyc.txt`, `c2c2000_outflow_nyc.txt`, `sf3_2000_nyc_mobility_nativity.json` | People aged 5 and over. |
| Age structure | Census Bureau county estimates by age: [`co-asr-7079`](https://www2.census.gov/programs-surveys/popest/tables/1900-1980/counties/asrh/co-asr-7079.csv) (1970 modified count), [`pe-02`](https://www2.census.gov/programs-surveys/popest/datasets/1980-1990/counties/asrh/pe-02.csv) (July 1, 1980), the 1990s API file (July 1, 1990), [`co-est00int-alldata-36`](https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-alldata-36.csv) (April 1, 2000 count), [`cc-est2020-alldata-36`](https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/asrh/CC-EST2020-ALLDATA-36.csv) (April 1, 2010 count), [`cc-est2025-alldata-36`](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/asrh/cc-est2025-alldata-36.csv) (April 1, 2020 estimates base and July 1, 2025 estimate) | | |
| Race and Hispanic origin 1970-2020 | Decennial census: Gibson and Jung, [Census Bureau Population Division Working Paper 76](https://www.census.gov/library/working-papers/2005/demo/POP-twps0076.html) (2005) for 1970-1990; Summary File 1 and P.L. 94-171 files for 2000-2020, as compiled for the Vital City "Who lives here" chart | `../nyc-demographics-horserace/data/data.json` | Shares as published; race is "race alone." |
| Foreign-born 1970-2000 | NYC Department of City Planning, [The Newest New Yorkers, 2013 edition](https://www.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/nny2013/nny_2013.pdf), Table 2-1 (decennial census figures) | `dcp_nny2013_table2-1_page20.txt` | The 2000 figure (2,871,032) ties to 2000 SF3 table P21. |
| Foreign-born 2006-24 | ACS 1-year, table B05002 | `acs/acs1_YYYY.json` | |

Download locations: Census estimates files are under `https://www2.census.gov/programs-surveys/popest/`; the 2000 county-to-county flow files under `https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/2000/county-to-county-flows/`; the DOHMH summary at `https://www.nyc.gov/assets/doh/downloads/pdf/vs/2023sum.pdf`; The Newest New Yorkers 2013 at `https://www.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/nny2013/nny_2013.pdf`; ACS, decennial and flows tables from `https://api.census.gov`. All accessed September 15, 2026.

## 2. Calculations

### 2.1 Net migration each year

For year t: `net migration(t) = population(t+1) − population(t) − (births(t) − deaths(t))`.

Population is the July 1 estimate, except in census years (1970, 1980, 1990, 2000, 2010, 2020), where it is the April 1 count. Births and deaths are calendar-year counts. The mismatch of a few months at census years is accepted; it shifts a few thousand people between adjacent years and nothing between decades. Because the formula uses the census counts as anchors, "net migration" also absorbs any census undercount or overcount and any error in the birth and death counts. It is the residual, and the page says so.

### 2.2 Vintages and intercensal series: which Census numbers are used

The Census Bureau publishes two kinds of yearly population figures. During a decade it issues postcensal estimates, one "vintage" a year, each of which revises every year back to the last census; after the next census it issues an intercensal series that reconciles the decade's estimates to the counts at both ends. The page uses the intercensal series wherever one exists (1970-79, 1980-89, 1990-99, 2000-09, 2010-19) and the latest vintage (2025) for 2020-25. The vintage 2020 series had put July 2020 at 8,253,213 against a 2020 count of 8,804,190, which is why the intercensal reconciliation matters; the difference is spread across the 2010s by the Bureau's own method, not by this page.

For 2020-25, vintage 2025 (released March 2026) raised the July 2024 figure from 8,478,072 in vintage 2024 to 8,596,825, and vintage 2024 had already reversed vintage 2023's estimate of losses from July 2022 to July 2023. The Bureau attributes the revisions to better allocation of international migrants, including humanitarian migrants, and to more complete group-quarters data supplied by the city. The 2020-25 figures on the page are identical, county by county, to those in the Department of City Planning's July 2026 population estimates release, which also measures change from the 2020 census count rather than from the vintage 2025 estimates base (8,805,594); the page does the same. The 2020 Post-Enumeration Survey found New York State overcounted (its state list reads "New York (+3.44)" percent), so the 2020 anchor itself carries uncertainty, and future vintages will revise 2021-25 again.

### 2.3 Decade ledger

For each decade (and 2020-25), births and deaths are summed over the calendar years in the span; net migration is the census-to-census change minus that natural increase. The Census Bureau's international and domestic columns are its own estimates for the July-to-June years inside each span; they were produced before the census at the end of the decade and, for the 1990s and 2000s, missed much of the growth the count later found (for July 1990-June 2000 the Bureau's components sum to a July 2000 population of 7,469,322 against a count of 8,008,278). They are shown for the split, not the level.

### 2.4 Gross arrivals (used by the calculator and the arrivals chart)

- 2006-2024: `arrivals(y) = B07001 moved from a different state + moved from abroad + (moved from a different county in the same state × s)`, where s is the share of such movers who came from outside the five boroughs rather than from another borough. s is measured in each ACS county-to-county flows window (2006-2010: 0.238; 2016-2020: 0.276) and each ACS year uses the window centered nearest to it. 2020 has no ACS release and is the mean of 2019 and 2021. 2025 carries 2024's rate per resident forward.
- 1995-1999: `(domestic inflow to the five counties from outside them, 448,970 + arrivals from abroad, Puerto Rico and the island areas, 521,643) / 5 = 194,123 per year`, from the 2000 census. The inflow file ties exactly to the SF3 count of residents who lived in another state in 1995 (301,243). Because the census asks about residence five years earlier, people who arrived and left again within the window are missed, so this anchor slightly understates the true gross inflow.
- 2000-2005: the arrival rate per resident is interpolated between the 1995-99 rate and the 2006 rate.
- 1970-1994: no official gross-inflow series exists. The page assumes the 1995-99 rate per resident (2.54 percent a year). This is an assumption, flagged in the calculator whenever a chosen window includes those years. Immigration was lower in the 1970s than in the 1990s (The Newest New Yorkers documents the rise), so the assumption probably overstates arrivals in the 1970s and early 1980s, which in turn overstates turnover for windows that start then.

Out-moves each year are `arrivals − net migration`, so the two are consistent with the population series by construction. Out-moves include emigration abroad, which no survey measures directly.

### 2.5 The turnover calculator

Start with the population in the start year A as one stock. For each year t from A to B−1:

1. exit rate `e(t) = (deaths(t) + out-moves(t)) / population(t)`
2. every existing stock is multiplied by `1 − e(t)`
3. `births(t)` join the "born since A" stock and `arrivals(t)` join the "moved in since A" stock

Because out-moves are defined from net migration, the three stocks add up exactly to the population in B. Reported figures:

- share of B's residents who were not here in A: `1 − stayers / population(B)`
- share of A's residents gone by B: `1 − stayers / population(A)`
- the "back-of-the-envelope" version: `(births + arrivals over the window) / population(B)`, which is what a quick tally gives and which ignores newcomers who later left or died. For 2001-2013 it returns 51 percent, matching the "fully half" figure the Department of City Planning gave [Harry Siegel](https://www.vitalcitynyc.org/how-nyc-changed-since-9-11/) in 2013; the cohort version returns 42 percent. For 2001-2025 the simple tally exceeds 100 percent, which is why the cohort version is the headline.

The model's one big assumption is that everyone faces the same exit rate regardless of how long they have lived in the city. Recent arrivals move again at higher rates than long-settled residents (the ACS shows this), which means the model keeps too many newcomers and too few long-term residents, overstating turnover. Deaths, on the other hand, fall mostly on older, long-settled residents, which the model spreads across everyone, understating the departure of the original cohort. The two errors work in opposite directions; the page does not attempt to size them.

### 2.6 Age, race and foreign-born

Age groups are sums of five-year bins. Median age is interpolated linearly within the bin that contains the midpoint (85 and over is treated as a 15-year bin). Race shares are as published by the census; Black and Asian/Pacific Islander are race alone and include Hispanic members, so the four lines are not additive. Post-2020 population estimates use a "modified race" scheme in which "some other race" answers are reassigned to the standard categories, so they are not comparable with the census lines and are not shown. Foreign-born shares are foreign-born residents divided by total population. The page's headline totals (births, deaths, net migration) cover calendar years 1970-2024, the 55 years whose yearly residuals sum exactly to the April 1970 to July 2025 population change.

## 3. Cross-checks performed

- The 2000 county-to-county inflow file, filtered to the five NYC counties and origins outside them, ties exactly to the 2000 SF3 count of city residents who lived in another state in 1995 (301,243).
- The 2000 foreign-born figure in The Newest New Yorkers (2,871,032) ties to 2000 SF3 table P21.
- The 1980 and 1990 populations rebuilt from the estimate files equal the census counts (7,071,639 and 7,322,564); the 2010 population from the intercensal file equals 8,175,133.
- DOHMH births and deaths versus the Census Bureau's components (annual averages over full July-to-June years): 1980s births 119,171 vs 115,454, deaths 74,988 vs 74,143; 1990s 131,024 vs 125,591 and 68,528 vs 67,302; 2000s (through June 2009) 125,261 vs 119,618 and 57,374 vs 57,100; 2010s 119,738 vs 114,492 and 53,662 vs 55,085; 2020-25 97,719 vs 91,999 and 63,262 vs 57,567. DOHMH runs 3 to 6 percent higher on births throughout; the page uses DOHMH, the registry of record, and the gap goes into net migration as part of the residual.
- The calculator's three stocks sum to the end-year population for every window (checked in `build_data.py`).
- The 2020-25 population series (April 2020 count and July 2020-2025 estimates, all five boroughs) matches the table in City Planning's July 2026 release exactly; the 2010-2020 intercensal series rebuilt from the county table lands on the 2020 count (8,804,190).
- ACS arrivals for 2019 (253,116, after the inter-borough adjustment) agree with the 2016-2020 flows window (163,226 domestic plus 80,529 from abroad per year).

## 4. Limitations

- "Net migration" is a residual and carries every measurement error in the counts, births and deaths.
- The 2020-25 estimates are postcensal and will be revised in later vintages; vintages 2023, 2024 and 2025 each moved the 2022-24 figures by tens of thousands.
- Gross arrivals before 1995 are assumed, not measured; the calculator says so whenever it matters.
- The turnover figures are model estimates with the stated assumptions. They are meant to answer "roughly how much," not to be quoted to the decimal.
- 1971-80 births and deaths are five-year averages, so the annual chart is flat across those years by construction.
- Race categories changed in 2000 (multiple-race answers) and 2020 (coding of write-in answers).

## 5. Reproducing the page

```
python3 scripts/build_data.py   # parses data/raw/ into docs/data.json and prints the cross-checks
python3 scripts/build_page.py   # inlines data.json into build/template.html → docs/index.html
```

Python 3.11 or later, standard library only. The raw files were downloaded on September 15, 2026 with a browser user agent (nyc.gov refuses the default curl agent) and a Census API key for the API calls.
