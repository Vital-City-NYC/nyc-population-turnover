# Who came, who went: New York City's population since 1970

A Vital City graphic on how the city's population has changed since 1970: births, deaths, moves in and out, age, race and Hispanic origin, and the foreign-born share, with a calculator that estimates how much of the city turned over between any two years.

- Page: `docs/index.html` (self-contained; can be pasted whole into a Ghost HTML card)
- Methodology: `METHODOLOGY.md`, rendered to `docs/methodology.html`
- Data: `docs/data.json`, built from the verbatim official files in `data/raw/`

Rebuild:

```
python3 scripts/build_data.py
python3 scripts/build_page.py
```

Only official sources are used: U.S. Census Bureau (population estimates, decennial census, American Community Survey, migration flows), the NYC Department of Health and Mental Hygiene (births and deaths) and the NYC Department of City Planning (foreign-born history). See the methodology for every calculation and assumption.
