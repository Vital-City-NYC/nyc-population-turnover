# How this graphic was built: the prompts, in order

A record of what Josh Greenman asked Claude Code (Anthropic's coding agent) to do, and what each request produced. The queries are verbatim. Everything was done in one working session on September 15, 2026, from a folder on his laptop that had earlier Vital City and personal data projects in it, which the agent could read for style and data conventions.

Live result: https://vital-city-nyc.github.io/nyc-population-turnover/

---

## 1. The original request

> inspired by/related to this article https://www.vitalcitynyc.org/how-nyc-changed-since-9-11/ — and drawing on closely related work you did for me already — build a sophisticated graphic in vital city style that shows how new york city's population has changed over the past 50 years. who's been born, who's died, who's moved here, who's moved away. total numbers, demographics, etc. If possible/doable with the data, let someone enter in a beginning point and end point to determine approximately what percent of the city has turned over between those two dates. use ONLY official data and be transparent about all calculations.

What happened: the agent read the linked article (Harry Siegel's "A City Forgets," which cites a City Planning back-of-the-envelope figure that half the city had turned over since 2001), reread its own notes on earlier projects (a 9/11 then-and-now infographic, a population atlas, a births-and-deaths page, a race-by-decade chart), and then assembled the data: Census Bureau county estimates for each decade, the decennial counts, the city Health Department's births and deaths table back to 1898, the Census migration-flow files, the American Community Survey mobility tables, Census age files, and City Planning's foreign-born history. It wrote a build script, a page in the Vital City chart-card style with seven figures and a turnover calculator, a methodology page, and published to a Vital City GitHub Pages site. The first version was a stack of bordered cards.

## 2. Redesign and fact check

> Knit this into a single presentation that feels like it holds together a bit more. now it's a series of boxes.
>
> double check all facts.

What happened: the page became one continuous document in numbered chapters. Every time chart moved onto a shared 1970-2025 axis in a single column, with a short headline in the left margin, so the panels line up year for year, and the calculator's chosen window is shaded across all of them. The fact pass recomputed every number and claim from the built data and turned up four corrections: the headline totals were re-windowed to the 55 years whose yearly figures actually sum to the population change (6.6 million births, not 6.7; net migration −2.2 million, not −2.3); the year of City Planning's "fully half" figure was corrected to 2013; an unverifiable claim about the 1970 foreign-born count was removed; and the state overcount claim was sourced to the Census Bureau's own page and quoted.

### 2a. Sent while that was in progress

> include direct links as embedded hyperlinks to sources wherever possible.

What happened: a numbered notes section at the bottom links each series to its exact file at census.gov, nyc.gov or the Census API, and the methodology got the same links. Every link was checked to resolve.

## 3. Hover

> make it show exact numbers when hovering over.

What happened: hovering any chart puts a dashed guide through every panel at that year, switches each panel's margin readout to that year's exact figures (with the arithmetic behind derived numbers, such as net migration), and shows a tooltip at the cursor. Touch works the same way.

### 3a. Sent while that was in progress

> "sources and notes" should't take a roman numeral; it should just be listed at the bottom.

What happened: the chapters now run I to III and the notes are an unnumbered section at the end.

## 4. Fitting the story page

Sent with a screenshot of a published Vital City story ("She Buys It, He Fires It") to show where the graphic would sit.

> when it's published on our site, it'll be embedded in a story page with a headline and a bit of text (see image of another story. Imagine the graphic appearing where the body text is. which is to say, it shouldn't begin with its own bold headline. change the lead-in to regular halyard text that says
>
> Since 1970, New York City has recorded 6.6 million births and 3.7 million deaths, and lost a net 2.2 million people to migration. It is about 690,000 people bigger than it was 56 years ago. The charts and graphs below detail who was born, who died, who moved in and who moved away over the decades, from the Census Bureau and the city's own birth and death registry, with an estimate of how much of the city has changed hands between any two years.

What happened: the headline and dek were replaced by that paragraph as plain body text.

### 4a. Sent while that was in progress

> and make sure you're really using the right census numbers. I know there's a whole thing with vintages I don't fully understand. are you looking at NYC DCP data too?

What happened: this caught a real problem. The agent had believed the Census Bureau never published a reconciled ("intercensal") 2010-2020 county series and had stretched the older vintage 2020 estimates itself to land on the 2020 count. The intercensal table does exist, in a different directory from the other decades' files, and the page now uses it. The agent also pulled City Planning's July 2026 population estimates report and confirmed that its 2020-2025 figures match the page county by county, and that City Planning likewise measures change from the 2020 count rather than the estimates base. The report is now cited on the page and in the methodology, along with a plain-language explanation of vintages and intercensal series.

## 5. Hover stability

> when I hover over and move cursor left to right, the charts jump up and down a little. can they be fixed in place so that doesn't happen?

What happened: the readout text under each chart's heading changed length as the cursor moved, resizing the row. The page now measures the longest possible readout for each panel on load and reserves that height, so nothing moves. Tested by sweeping across six years in all eight panels: zero pixel shift.

## 6. The walkthrough

> produce a walkthrough of how I queried you, with all follow-up queries, for someone who's asking.

What happened: this document.

## 7. Remove the AI caution

> remove the AI caution button please

What happened: the button and its pop-up were removed; the quality-control list remains in the methodology.

## 8. A second fact check

> now do another really rigorous fact-check as though you're a skeptical demographer.

What happened: the agent re-derived every input from the raw files with fresh code, checked each variable's meaning against the publisher's documentation, and compared the page against outside benchmarks. That found one substantive error: the city Health Department's historical births-and-deaths table counts events that occurred in the city regardless of residence (12,701 of 2023's 98,389 births were to non-residents), so the ledger was rebuilt on residence-based counts from the National Center for Health Statistics as carried in Census Bureau files, with the state Health Department's resident counts as an independent check. The headline totals changed (births 6.4 million, deaths 3.6 million, net migration −2.0 million). Smaller fixes: the 2000 age file's under-1 group had been dropped; the 2020 Asian and Pacific Islander share now includes Pacific Islanders as the earlier decades do; the 1970 Hispanic and non-Hispanic white figures are labeled as sample-based estimates.

## 9. Households, and the boroughs

> is there anything from fully verified sources that can be added on how the shape of the city's poopulation has chagned vis-a-vis families? what % is part of families, what % is single, etc.? or is that already in here?
>
> yeah please do that. add it all the way back.

Sent while that was in progress:

> last, can you also add in the shift in borough population over these years?

What happened: two panels were added to the timeline. Households by type (family, married-couple, living alone) runs 1970 to 2024: the 2000-2024 figures come from the Census API, and the 1970, 1980 and 1990 figures were taken from the Bureau's printed state volumes, which for 1970 and 1980 are image scans that had to be read by eye (the page images are saved in the repository, and each year's parts add exactly to its household total). One-person households were not tabulated for cities in those two volumes, so that line starts in 1990. The borough panel uses the county detail already in the population files.

## 10. Layout fixes and wording

> can you fix this so it fits in the box and doesn't require a scrollbar?

> should there be two separate panels under here or just one? it confused me slightly.

> please put the third item, the calculator, first.

> this summary isn't right... math doesn't work. be more specific.

> you have footnote markers and footnotes below. is it possible to have elegant links to the source notes instead, so if you click them it jumps right down, and no traditional footnotes?

> "A quarter of a million people a year move in from somewhere else" is present tense. should be past tense. review the language.

What happened: the decade table was compressed to fit the column; the calculator's two result boxes became one; the calculator moved to the top; the key numbers went to two decimals so births, deaths and net migration reconcile with the population change; footnote numbers were replaced by "Sources for this chart" links that jump to titled notes and back; and every historical claim was put in the past tense with its dates. That language pass also caught two errors: the foreign-born share "nearly doubled" rather than doubled, and a note had misstated what City Planning challenged in the Census estimates.

## 11. A third, independent research pass

> Take a deep look at this. Do a rigorous research pass to ensure that everything holds up to scrutiny.

What happened: four independent checkers re-derived every series from freshly downloaded primary sources without using the project's processed data, and a fifth read the 1970s federal vital statistics volumes. The population series and most figures held up exactly. The corrections: the 1970s births and deaths are now federal resident counts for each year instead of scaled five-year averages; four periods where the Census files hold modeled births and deaths now use state resident counts; arrivals now come from a more direct survey table, aligned to the year of the moves, with the Census Bureau's net international migration as a floor and the pre-2005 rate calibrated to the 2000 census; a chart that was drawn a year off was realigned; a decade sentence that ignored the 2010s' small migration gain was fixed; census-year borough and age figures now use the published counts and official median ages; the living-alone line now starts in 1970; and the calculator now rounds its outputs and shows a plausible range. The full list is in section 4 of the methodology.


> do an independent check of the turnover calculator to make sure it's 100% solid in how it yields a figure.

What happened: the calculator was rebuilt separately in a second language using a different formulation. It matched the page exactly for all 1,540 pairs of years. Its inputs rebuilt exactly from the raw Census files. It was then tested against official counts it never uses: immigrants who arrived since 2010 and children born in the state. The model came within 2 to 7 percent. Letting newcomers leave faster, or weighting deaths toward older residents, kept every result inside the stated range. Two display fixes followed. The legend's rounded percentages now always add up to the headline. The calculator now says whether a year means April 1 (census) or July 1 (estimate). The results are in section 2.5 of the methodology.

---

## Where things live

- Page: `docs/index.html` (one self-contained file that can be pasted into a Ghost HTML card)
- Methodology: `METHODOLOGY.md`, rendered to `docs/methodology.html`
- Raw official files, kept verbatim: `data/raw/`
- Build: `python3 scripts/build_data.py` then `python3 scripts/build_page.py`
- Repository: https://github.com/Vital-City-NYC/nyc-population-turnover
