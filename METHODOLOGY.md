# Methodology: New York City's population since 1970, and the turnover calculator

Built September 15, 2026; revised September 23, 2026 after an independent audit that re-derived every series from primary sources (section 4). Every figure comes from the U.S. Census Bureau, the National Center for Health Statistics (NCHS), the New York State Department of Health, the New York City Department of Health and Mental Hygiene or the New York City Department of City Planning. The raw files are kept in `data/raw/` (page images of scanned volumes included). `scripts/build_data.py` turns them into `docs/data.json`, and `scripts/build_page.py` inlines that into `docs/index.html`. Re-running the two scripts reproduces the page.

## 1. Sources

### Population

| Series | Source | File in `data/raw/` | Notes |
|---|---|---|---|
| Census counts | 1970: 7,894,862; 1980: 7,071,639; 1990: 7,322,564; 2000: 8,008,278; 2010: 8,175,133; 2020: 8,804,190 (April 1) | | Borough counts for 1970-1990 from City Planning's [historical table](https://www.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/historical-population/nyc_total_pop_1900-2010.pdf) (`fix/dcp_nyc_total_pop_1900-2010.pdf`); 2000 and 2010 from Summary File 1; 2020 from the P.L. 94-171 file (`fix/pl_2020_county_pop.json`). |
| 1971-79 | Census Bureau, [Preliminary Estimates of the Intercensal Population of Counties 1970-1979](https://www2.census.gov/programs-surveys/popest/tables/1900-1980/counties/totals/e7079co.txt) | `e7079co.txt` | The Bureau's only county series for the decade; rounded to hundreds. Its 1970 county base includes later corrections (Queens +701). |
| 1981-89 | Census Bureau, [Intercensal Estimates, 1980-1989](https://www2.census.gov/programs-surveys/popest/tables/1980-1990/counties/totals/e8089co.txt) | `e8089co.txt` | Its 1980 base shifts 92 people from Staten Island to Brooklyn relative to the published counts. |
| 1991-99 | Census Bureau, [CO-EST2001-12-36](https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/co-est2001-12-36.pdf) intercensal county estimates, pulled via the [API](https://api.census.gov/data/1990/pep/int_charagegroups.html) | `int_charagegroups_1990s.json` | Values identical to the published table. |
| 2001-09 | Census Bureau, [intercensal county estimates 2000-2010](https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-tot.csv) | `co-est00int-tot.csv` | |
| 2011-19 | Census Bureau, [intercensal county estimates 2010-2020](https://www2.census.gov/programs-surveys/popest/tables/2010-2020/intercensal/county/co-est2020int-pop-36.xlsx) (released November 2024) | `co-est2020int-pop-36.xlsx` | Its April 2020 column differs from the official 2020 count by a few people per borough, so census years use the official count. |
| 2021-25 | Census Bureau, [vintage 2025 county estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv) (file dated March 26, 2026) | `co-est2025-alldata.csv` | Identical to City Planning's [July 2026 release](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/population/population-estimates/new-york-city-population-estimates-and-trends-july-2026.pdf), county by county. |

### Births and deaths (residents of the five boroughs)

| Period | Source | Notes |
|---|---|---|
| 1970-1980, calendar years | NCHS, [Vital Statistics of the United States](https://www.cdc.gov/nchs/products/vsus.htm): natality Table 2-1 (births by place of residence) and mortality Part B Table 7-1 or 8-1 (deaths by place of residence), "New York City" rows | Read from the scanned volumes (`fix/nchs_vsus_1970s/`, with URL, PDF page and table for each value in `nchs_nyc_resident_1970_1980.json`). In every year the five borough rows, and the white and all-other rows, sum exactly to the city figure. Births for 1970-71 and several later years, and 1972 deaths, rest on NCHS's 50-percent sample of records. |
| April 1980-March 1990 | Census Bureau [comp8090](https://www2.census.gov/programs-surveys/popest/datasets/1980-1990/counties/totals/comp8090.zip) record B, ten estimate periods | State vital records compiled through the Federal-State Cooperative Program. |
| July 1990-June 1999, and the April-June 1990 stub | [CO-2000-8](https://www2.census.gov/programs-surveys/popest/tables/1990-2000/estimates-and-change-1990-2000/2000c8_36.txt) | July 1999-March 2000 uses 9/12 of the July 1999-June 2000 figure. |
| April 2000-June 2008 | Vintage 2010 county components, [co-est2010-alldata.csv](https://www2.census.gov/programs-surveys/popest/datasets/2010/2010-eval-estimates/co-est2010-alldata.csv) (`fix/co-est2010-alldata.csv`) | The last vintage of the decade, with final vital data through 2008. |
| July 2008-June 2009; July 2009-March 2010; July 2018-June 2019; July 2019-March 2020 | New York State Department of Health, resident [births (Table 7)](https://www.health.ny.gov/statistics/vital_statistics/2023/table07.htm) and [deaths (Table 35)](https://www.health.ny.gov/statistics/vital_statistics/2023/table35.htm) by calendar year (`nysdoh/`) | The Census files hold modeled figures for these periods (the Bureau's [methodology](https://www2.census.gov/programs-surveys/popest/technical-documentation/methodology/2010-2020/methods-statement-v2020-final.pdf): "the births and deaths data we receive from NCHS have a two-year lag"). July-June = the mean of the two calendar years; July-March = half the first year plus a quarter of the second, except deaths for July 2019-March 2020, which use each year's share from NCHS weekly death counts ([2019](https://data.cdc.gov/resource/3yf8-kanr.json), [2020](https://data.cdc.gov/resource/muzy-jte6.json)): 49.3 percent of 2019 deaths fell in July-December and 20.5 percent of 2020 deaths in January-March, so the spring 2020 spike stays in the next row. |
| April 2010-June 2018 | [Vintage 2020](https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv) components | |
| April 2020-June 2025 | Vintage 2025 components | July 2023-June 2025 are Bureau estimates pending final counts. |

The city Health Department's long historical series ([Summary of Vital Statistics 2023](https://www.nyc.gov/assets/doh/downloads/pdf/vs/2023sum.pdf), Table PC1) is not used: it counts every birth and death that occurred in the city, including 12,701 births to non-residents among 98,389 in 2023 (Table PO7), and omits residents' events elsewhere. Its technical notes say so (pages 114, 118 and 124).

### Migration, age, households, race, foreign-born

| Series | Source | File | Notes |
|---|---|---|---|
| Arrivals 2006-2024 surveys | ACS 1-year [table B07204](https://data.census.gov/table/ACSDT1Y2024.B07204?g=160XX00US3651000), New York city: line 7 ("Different house in United States 1 year ago: Elsewhere") + line 16 ("Abroad 1 year ago"), with margins of error | `fix/b07204/acs1_YYYY.json` | Population aged 1 and over. No standard 2020 release. |
| 2000 census arrivals | [County-to-county flows](https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/2000/county-to-county-flows/) and SF3 table P24 (residence in 1995) | `c2c2000_*.txt`, `sf3_2000_nyc_mobility_nativity.json` | 448,970 from elsewhere in the U.S. (ties exactly to SF3's 301,243 from other states plus 147,727 from the rest of the state) + 521,643 from abroad, Puerto Rico and the island areas = 970,613 residents aged 5+. |
| Bureau migration split | CO-2000-8 (July 1990-June 2000), [vintage 2009](https://www2.census.gov/programs-surveys/popest/datasets/2000-2009/counties/totals/co-est2009-alldata.csv) (July 2000-June 2009), vintage 2020 (July 2010-June 2020), vintage 2025 (July 2020-June 2025) | | None covers July 2009-June 2010. |
| Age, census years | 1970: Table 24, [PC(1)-B34](https://www2.census.gov/prod2/decennial/documents/1970a_ny1-02.pdf), page 34-108; 1980: Table 26, [PC80-1-B34](https://www2.census.gov/library/publications/decennial/1980/volume-1/new-york/1980censusofpopu80134unse_bw.pdf), page 34-124 (both read from scans; each column sums exactly to the census total); 2000 and 2010: SF1 P12; 2020: DHC [P12](https://data.census.gov/table/DECENNIALDHC2020.P12?g=160XX00US3651000) | `fix/census_age_1970_1980.json`, `fix/sf1_*_P012.json`, `fix/dhc2020_P12.json` | 1990 uses the Bureau's July 1990 estimate because the city's 1990 census age table is only in a scanned volume with different groupings. |
| Median age | Published: 1970 32.4, 1980 32.6, 1990 33.6 ([CP-1-34](https://www2.census.gov/library/publications/decennial/1990/cp-1/cp-1-34-1.pdf), Table 1), 2000 34.2, 2010 35.5, 2020 36.8 (P13) | | 2025: no city median is published. Computed from the Bureau's [single-year-of-age county file](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/asrh/cc-est2025-syasex-36.csv) by linear interpolation within the single year containing the midpoint; the same method reproduces the Bureau's published medians for all five boroughs exactly (Bronx 36.4, Brooklyn 36.5, Manhattan 37.7, Queens 40.3, Staten Island 41.0). Result: 37.9. |
| Age, 2025 | [cc-est2025-alldata-36](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/asrh/cc-est2025-alldata-36.csv), July 1, 2025 | | |
| Households 1970 | PC(1)-B34 Table 25, page **34-115**, New York City column (households 2,836,872; family heads 1,690,073 + 353,692; wife of head 1,603,387; primary individuals 304,448 + 488,659; 2.74 per household); one-person households from the [1970 Census of Housing HC(1)-A34](https://www2.census.gov/library/publications/decennial/1970/housing-volume-1/38133719v1p34ch1.pdf), Table 9, page 34-21 (owner 80,270 + renter 634,114 = 714,384; owner plus renter units by size sum exactly to 2,836,872) | `hh/`, `fix/scans/` | |
| Households 1980 | PC80-1-B34 Table 27, page 34-132 (householders 2,788,530; family 1,202,278 + 555,286; spouses 1,203,135; nonfamily 430,244 + 600,722; 2.49) | `hh/scans/` | The 1980 housing volume with one-person households was not found online, so the living-alone line skips 1980. |
| Households 1990-2024 | 1990 CP-1-34 Table 2, page 36; SF1 P18 (2000, 2010); DHC P16 (2020); ACS 1-year B11001, B25010, B11002 (2006-2024) | `hh/` | Shares are computed from counts, not from rounded percentages. |
| Race and Hispanic origin | 1970-1990: Gibson and Jung, [Working Paper 76](https://www.census.gov/library/working-papers/2005/demo/POP-twps0076.html), New York city table; 2000: SF1 [P3 and P8](https://data.census.gov/table/DECENNIALSF12000.P008?g=160XX00US3651000); 2010: SF1 P5; 2020: P5 | `../nyc-demographics-horserace/data/data.json` | 2020 Asian and Pacific Islander = Asian alone 1,385,144 + NHPI alone 6,874. |
| Foreign-born | 1970-1990: [Working Paper 29](https://www.census.gov/library/working-papers/1999/demo/POP-twps0029.html), Table 22, and City Planning's The Newest New Yorkers 2013, Table 2-1 (identical); 2000: SF3 P21; 2006-2024: ACS B05002 | `dcp_nny2013_table2-1_page20.txt`, `acs/` | |

All files were downloaded September 15-23, 2026. nyc.gov refuses the default curl user agent; cdc.gov refuses scripted requests but loads in a browser.

## 2. Calculations

### 2.1 The yearly ledger

Each row runs between two population dates: July 1 to July 1, except that census years anchor on April 1, so a row that starts at a census covers 15 months (April to the following June) and a row that ends at one covers 9 months (July to March). Births and deaths are counted over exactly those intervals. For each row:

`net migration = population at the end − population at the start − (births − deaths)`

It is a residual. It absorbs every error in the counts, estimates and vital statistics, and it cannot be split into international and domestic parts; the Census Bureau's own split is shown beside it. Charts show 15- and 9-month rows at an annual rate; the hover readout gives both.

The headline totals cover April 1970 to July 2025: births 6,351,553, deaths 3,644,252, net migration −2,017,534. The population change is +689,767. At two decimals the four reconcile (6.35 − 3.64 − 2.02 = 0.69 million).

### 2.2 Vintages and intercensal series

During a decade the Census Bureau issues postcensal estimates, one "vintage" a year, each revising every year back to the last census. After the next census it issues an intercensal series reconciling the decade to the counts at both ends. The page uses intercensal series for every completed decade and vintage 2025 for 2021-25.

Postcensal estimates for the city have missed the next census badly. The Bureau's July 2000 estimate, made before the 2000 count, was 7,469,322, against a count of 8,008,278. Its July 2020 estimate was 8,253,213, against a count of 8,804,190. Vintage 2025 raised July 2024 from 8,478,072 to 8,596,825, mostly through higher international migration. The city's [challenge](https://www.census.gov/programs-surveys/popest/about/challenge-program/results.html) to vintage 2023, over uncounted shelter residents, raised July 2023 by 36,489. The 2020-25 decline of 219,561 rests entirely on postcensal estimates.

The page measures change from the April 2020 census count (8,804,190), as City Planning does, rather than from the Bureau's estimates base (8,805,594). The Bureau's April 2000 and 2010 bases also differ slightly from the counts (+907 and −203).

The [2020 Post-Enumeration Survey](https://www.census.gov/library/stories/2022/05/2020-census-undercount-overcount-rates-by-state.html) estimated a statewide net overcount of New York's household population of 3.44 percent (standard error 0.94; [report](https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/census-coverage-estimates-for-people-in-the-united-states-by-state-and-census-operations.pdf)). It measures household population only. The Bureau says it cannot publish county or place estimates. If the city was overcounted too, the 2020 peak, the 2010s growth and the 2010s net migration (+19,027) are overstated, and the 2020-25 decline is overstated.

### 2.3 Decade ledger

Sums of the yearly rows between census dates, plus 2020-25. The Bureau's international and domestic columns are its own estimates for the July-to-June years named in the table. The 2000s column covers nine years, because no estimate exists for July 2009-June 2010. The 1990s and 2000s series undershot the growth the censuses later found. They are shown for the split, not the level.

### 2.4 Gross arrivals

- **2006-2024 surveys.** Arrivals = B07204 line 7 (from elsewhere in the U.S., outside the city) + line 16 (from abroad). A survey year's answers describe moves in the 12 months before interviews held during that year, so survey year y is assigned to the ledger row running July y−1 to July y. Earlier versions of this page used table B07001 and estimated what share of in-state movers came from outside the city; B07204 measures that directly. The 90 percent margins of error run ±10,546 to ±15,363, and most year-to-year changes are not statistically significant.
- **Floor from the Bureau's international figure.** Gross arrivals from abroad cannot be smaller than net arrivals from abroad. Where the Bureau's net international migration for the same July-June year exceeds the survey's count of arrivals from abroad, the model uses the Bureau's figure. That happened in 2022-23 (155,131 against 104,808) and 2023-24 (219,578 against 98,492), when the Bureau revised its methods to capture humanitarian migrants.
- **Gaps.** The July 2019-March 2020 row has no survey (no standard 2020 release) and takes the mean of the neighboring rates. The July 2024-July 2025 row, whose survey is not yet out, carries the previous row's survey rate forward, with the same floor applied using the Bureau's 2024-25 international figure.
- **Row length.** Rows spanning 15 or 9 months get 15/12 or 9/12 of a year's arrivals.
- **1995-1999.** No annual series exists. The 2000 census counted 970,613 residents aged 5 and over who had lived outside the city in April 1995. The 1995-99 arrival rate is calibrated so that the model's count of people who arrived between April 1995 and April 2000 and were still in the city in 2000 equals that figure. Result: 2.663 percent of the population a year. Dividing the five-year count by five would understate annual arrivals badly, because a five-year question misses people who arrived and left again, or moved more than once. The 2000 census's domestic arrivals divided by five come to about 90,000 a year, while the 2006-10 surveys found about 166,000 a year.
- **1970-1994.** The calibrated 1995-99 rate is assumed. Every calculator window that includes these years says so.
- **2000-2004.** Interpolated between the calibrated rate and the first survey-based rate (2.994 percent).

Out-moves each row = arrivals − net migration, so arrivals, out-moves, births, deaths and population changes are consistent by construction. Out-moves include emigration, which no source measures.

### 2.5 The turnover calculator

Start with the population in year A as one stock. For each row t from A to B−1:

1. exit rate `e(t) = (deaths(t) + out-moves(t)) / population(t)`;
2. every stock is multiplied by `1 − e(t)`;
3. `births(t)` join the "born since A" stock and `arrivals(t)` join the "moved in since A" stock.

The three stocks sum exactly to the population in B, for every window (checked in `build_data.py`). The headline is `1 − stayers / population(B)`: the share of the end-year city that was not here in A. The second line is `1 − stayers / population(A)`: the share of A's residents gone by B. Model outputs are rounded to three significant figures.

**Range.** The largest uncertainty is the level of gross moves. The range shown reruns the model with arrivals 15 percent lower and 25 percent higher, with out-moves moving with them so net migration is unchanged. The upper bound is wider because independent measures point upward: the ACS county-to-county flows put domestic out-migration alone 1 to 16 percent above the page's total out-moves in the 2006-2020 windows (14-16 percent in the 2010s), IRS [Statistics of Income](https://www.irs.gov/statistics/soi-tax-stats-migration-data) data show domestic outflows of about 284,000 to 385,000 a year for the filing years 2016-17 through 2020-21, and the page's total also has to cover emigration.

| Window | Low | Central | High | Share of start-year residents gone |
|---|---|---|---|---|
| 2001-2025 | 62.3% | 66.5% | 72.5% | 64.3% |
| 2001-2013 | 38.9% | 42.3% | 47.5% | 38.7% |
| 2020-2025 | 20.2% | 22.6% | 26.4% | 24.5% |
| 1970-2025 | 88.9% | 91.3% | 94.3% | 90.6% |

**Equal exit rates.** Newcomers leave at higher rates than long-settled residents, a pattern well established in migration research (e.g., [Morrison, Demography, 1967](https://pubmed.ncbi.nlm.nih.gov/21318669/)); the model ignores that, which overstates the newcomers still present and so overstates turnover. Deaths fall mostly on older, long-settled residents; the model spreads them evenly, which understates the loss of the original cohort and so understates turnover. The audit's simulations, run on the version of the model it examined, put the first effect at −1.5 to −6.6 points on the 2001-2025 result (newcomers leaving at two to four times the base rate in their first years) and the second at about +3.5 points; together they changed the result by about 3 points or less. Heterogeneity within the original cohort, mobile renters against rooted owners, is not modeled; over long windows it would push the model toward overstating turnover. Former New Yorkers who return count as newcomers, which also pushes turnover up.

**Independent check of the calculator (September 23, 2026).** A second implementation, written separately, computes each stock as a product of yearly survival factors instead of carrying running totals. It reproduces the page's figures for all 1,540 pairs of start and end years at all three arrival levels, to within floating-point error (about one part in a quadrillion). Every other check also passed:

- The three stocks sum to the end-year population in every window.
- Every yearly exit rate falls between 0 and 10 percent.
- Every out-move figure stays positive, even at the low end of the range.
- The range is ordered correctly in every window.
- The share gone never falls as a window lengthens.
- Every survey-based arrivals figure rebuilds exactly from the raw B07204 files.
- The 2000 target of 970,613 rebuilds from SF3 table P024 and the county-to-county file. That file's out-of-state total ties exactly to SF3's (301,243).

Three tests against official figures the model never uses:

| Test | Official figure | Model | Ratio |
|---|---|---|---|
| Born outside the U.S., entered 2010 or later, living in the city, 2019 ACS (B05005) | 758,970 | 733,755 arrivals from abroad since April 2010 still present | 0.97 |
| Same, 2024 ACS | 1,137,841 | 1,110,438 | 0.98 |
| Children under 5 born in New York State, 2019 ACS (B06001) | 485,111 | 520,221 born in the city in the prior five years, still present | 1.07 |
| Children 5-17 born in New York State, 2019 ACS | 1,003,136 | 1,038,889 | 1.04 |
| Children under 5 born in New York State, 2024 ACS | 413,371 | 427,367 | 1.03 |
| Children 5-17 born in New York State, 2024 ACS | 993,361 | 939,438 | 0.95 |

The comparisons are approximate, for four reasons:

- The survey's year-of-entry count includes immigrants who settled elsewhere in the country first, and it leaves out U.S.-born people returning from abroad.
- The New York State count includes children born outside the city who later moved in.
- Survey interviews are spread across the year.
- The 2019 survey is weighted to the Bureau's vintage 2019 estimate, 5.5 percent below the intercensal figure the model uses.

Without the floor at the Bureau's net international migration, the 2024 abroad figure would be 941,022, or 0.83 of the survey count. The survey count therefore supports the floor.

Rerunning the model with the two main departures from equal exit rates gives these results:

| Window | Page | Newcomers leave at 2x in first 3 years | 3x | Deaths weighted to original residents | 2x + deaths | 3x + deaths |
|---|---|---|---|---|---|---|
| 2001-2025 | 66.5% | 64.9% | 63.5% | 68.6% | 67.0% | 65.6% |
| 2001-2013 | 42.3% | 41.1% | 40.1% | 43.1% | 41.9% | 40.9% |
| 2010-2020 | 35.5% | 34.6% | 33.7% | 36.1% | 35.1% | 34.3% |
| 2020-2025 | 22.6% | 21.8% | 21.2% | 22.8% | 22.0% | 21.3% |
| 1970-2025 | 91.3% | 90.4% | 89.6% | 94.2% | 93.6% | 93.0% |

The death weighting assumes the original residents have a relative death rate of 1, newcomers 0.4 and children born since 0.15. Every variant stays inside the page's range.

The pre-2005 calibration probably errs slightly low. The model's stock of arrivals after 1995 includes children under 5 and returning New Yorkers. The census target excludes both. Children aged 1 to 4 were 3 to 4 percent of arrivals from out of state or abroad in the 2010, 2015 and 2019 surveys. So the calibrated rate is, if anything, a little low, and so are turnover figures for windows before 2005.

The check led to two display fixes:

- The legend's rounded shares now always add to 100 and to the headline, using largest-remainder rounding. Before the fix, 367 of the 1,540 windows were off by a point.
- The calculator now names the population date: April 1 in census years, July 1 otherwise.

**City Planning's 2013 figure.** In 2013 City Planning gave Harry Siegel a back-of-the-envelope estimate that "fully half" of the city had turned over since 2001 ([Vital City, 2026](https://www.vitalcitynyc.org/how-nyc-changed-since-9-11/)). Its method was not published. For 2001-2013 the model gives 42 percent (share of the 2013 city new since 2001) and 39 percent (share of 2001 residents gone). The simple tally, births plus arrivals divided by the 2013 population, gives 51 percent. That tally overstates turnover, because it counts newcomers who later left or died, so its closeness to "fully half" is not corroboration. The same Vital City article says "more than three-quarters of the city has turned over" since 9/11. The model's figures for 2001-2025 are 66 percent new and 64 percent gone, with an upper bound near 72 percent.

### 2.6 Households and families

Shares are of all households, computed from counts. "Family" and "married couple" follow the census definitions in each year. Unmarried partners count as nonfamily households. 2020 married couples include 27,151 same-sex spouse households. The 1970 volume reports married couples as "wife of head," because the 1970 census made the husband the head of a married-couple household. The 1970 and 1980 figures were read from scanned pages, and each year's parts sum exactly to its household total.

The ACS runs somewhat differently from the census in the same year: 2010 ACS household size was 2.64, against 2.57 in the census. Its levels also move with the population controls; the 2024 survey is weighted to a total the Bureau later raised by about 119,000. The page therefore compares household size census to census, 2.74 in 1970 to 2.55 in 2020, and gives the 2024 survey figure (2.44) separately.

### 2.7 Age, race and foreign-born

Age shares come from census counts in census years, except 1990 (July 1990 estimate), and from the Bureau's estimate for 2025. Medians are the published census figures, and the 2025 median is computed as described above.

Race shares are as published. Black and Asian/Pacific Islander are race alone and include Hispanic members, so the lines are not additive. The 1970 Hispanic figure (16.2 percent) is the Spanish-language population in the 15-percent sample, and the Bureau estimated 1970 non-Hispanic white (62.9 percent) for cities from state proportions. The self-identified 5-percent sample gives 15.2 percent Hispanic and 64.0 percent non-Hispanic white. The 1970 Asian share is understated, because some groups were classified as white or not shown for cities.

For 2020, the Census Bureau attributes the national drop in the race-alone white count largely to changes in how it asked and coded race ([Census Bureau](https://www.census.gov/library/stories/2021/08/improved-race-ethnicity-measures-reveal-united-states-population-much-more-multiracial.html)). It makes no such statement about Black counts. In the city, Hispanic white alone fell from 874,437 to 281,089 while non-Hispanic white fell 0.1 percent. Race-alone Black fell 6.9 percent, and Black alone or in combination rose 2.0 percent. Post-2020 estimates use a "modified race" scheme and are not shown.

Foreign-born shares are foreign-born residents divided by total population. People born in Puerto Rico are native-born.

## 3. Limitations

- Net migration is a residual and carries every error in the counts, estimates and vital statistics. Several annual values are within that error, and the 2010s yearly pattern partly reflects how the intercensal method spread the 2020 correction.
- The 2020-25 population and the 2023-25 births and deaths are postcensal estimates and will be revised.
- Arrivals before 2005 are calibrated (1995-99), interpolated (2000-04) or assumed (1970-94). Windows that start in the 1970s are sensitive to the assumed rate: 1970-2001 ranges from about 65 to 79 percent for assumed rates of 1.5 to 3.5 percent a year, while 1970-2025 stays between 88 and 93 percent.
- The turnover figures are model estimates meant to answer "roughly how much." They should be quoted with their range.
- The 1971-79 population estimates are preliminary and rounded to hundreds.
- Race categories changed in 1980 (Hispanic write-ins), 2000 (multiple races) and 2020 (coding of write-ins).

## 4. Audit, September 23, 2026

Four independent checkers re-derived every series from freshly downloaded primary sources without using this project's processed data; a fifth read the 1970s federal vital statistics. Their findings and scripts are summarized below; corrections were applied before republishing.

**Confirmed.**
- All 56 city population values and all borough values match their Census sources exactly.
- All 45 births-and-deaths rows from 1980 to 2024 match the Census components files.
- All ACS survey rows match the API.
- The 1970, 1980 and 1990 household and foreign-born figures match the census volumes.
- All race shares match the census.
- The vintage figures, the 36,489 challenge increase and the 7,469,322 pre-census estimate check out.
- The turnover model's stocks sum to the end-year population in all 1,540 windows.
- The model's count of people born in the city since 2001 who were still there in July 2024 (1.62 million) is within about 5 percent of the 2024 ACS count of New York State-born residents under about 23 (about 1.7 million).

**Corrected.**
1. The 1970s births and deaths had been five-year averages of in-city occurrences, scaled by a 1980s ratio. They are now NCHS resident counts for each year. The 1970s natural increase fell from 339,320 to 298,739.
2. The Census files' final one or two years in each vintage are modeled. Four periods now use state resident counts: July 2008-June 2009, July 2009-March 2010, July 2018-June 2019 and July 2019-March 2020. The 2000s now use vintage 2010, which carries final data through 2008.
3. July 2019-March 2020 had double-counted part of the spring 2020 death spike. It is now split by weekly death counts.
4. Arrivals now come from ACS table B07204 instead of B07001 plus an estimated in-state share. Survey years are aligned to the moves they describe, 15- and 9-month rows are prorated, the Bureau's net international migration sets a floor, and the pre-2005 rate is calibrated to the 2000 census rather than divided by five.
5. The Bureau's migration chart was drawn one year late on the shared axis. It is now aligned.
6. The net migration chart now shows annual rates, as the methodology had said it did.
7. The decade sentence said the city lost people to migration "in every decade but the 1990s." The 2010s were a small gain too.
8. Census-year borough rows now use published counts. The 2000 row had used July estimates, and the 2020 row had used a column a few people off the official count.
9. Median ages are now the published figures, and the age bars use census counts. The 2020 bars had used the Bureau's estimates base, which puts under-15 at 16.8 percent against 16.4 percent in the count.
10. The 2024 married-couple share is 34 percent, not 35. The earlier figure rounded a rounded number.
11. The 1970 household page is 34-115, not 34-114. A 1970 one-person household count exists and now starts the living-alone line.
12. The 2000 race link pointed to a table without race data.
13. The 2020 race note wrongly implied the Bureau attributed a drop in Black counts to coding.
14. The 1970 Hispanic note now explains the Spanish-language definition.
15. "26% below their 2006-07 peak" is replaced with comparisons to the series high and the late-2000s high.
16. The "within about 1 percent" comparison is restated for multiyear totals.
17. The footer is corrected: it had said the only modeled figures were the turnover estimates.
18. The claim that the simple tally "matches" City Planning's figure is withdrawn.
19. "The ACS shows this" is replaced with a research citation.
20. Model outputs are rounded, and a range is shown.
21. This document had said the build uses only the standard library. It also needs openpyxl.

## 5. Reproducing the page

```
python3 scripts/build_data.py   # parses data/raw/ into docs/data.json and prints the cross-checks
python3 scripts/build_page.py   # inlines data.json into build/template.html -> docs/index.html
```

Python 3.11 or later with openpyxl (for the 2010-2020 intercensal table). The Census API key is needed only to re-download API tables, and the saved copies are in `data/raw/`.
