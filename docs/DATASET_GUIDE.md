# Dataset Guide — real sources + a worked test case for your scoring engine

You (Antigravity) are building the data layer for Development Priority Intelligence. This file tells you exactly which real datasets to pull per category, one important correction to a common false assumption, and a worked numeric example to sanity-check your Priority Score logic against before wiring the full dashboard.

## Real datasets, verified — not assumed

### Healthcare (build this category first — it has the strongest confirmed sources)
- **National Hospital Directory with Geo Code and additional parameters** (data.gov.in, mirrored on aikosh.indiaai.gov.in) — confirmed live: hospital locations (lat/long), facility type, ownership (public/private), services. Use this as your primary infrastructure-inventory source for healthcare.
- **All India Health Centres Directory** (data.gov.in) — PHCs, sub-centres, CHCs, district/state hospitals with geo-location. Combine with the hospital directory above for a fuller per-district facility count.
- **NFHS-5** (National Family Health Survey, 2019–21, district-level fact sheets, MoHFW/IIPS) — district health/demographic indicators. This is the standard reference dataset in Indian health policy work.
- **HMIS** (Health Management Information System, nhm.gov.in) — district/state facility performance data. Confirm the current export format before writing a parser — government portal export options change without notice.

### Education
- **UDISE+** (Unified District Information System for Education, Ministry of Education) — school/district-level facility counts (schools, teachers, classrooms).

### Water/Sanitation
- **Jal Jeevan Mission dashboard data** — district-level tap water connection coverage, actively maintained.

### Roads/transport
- **PMGSY** (Pradhan Mantri Gram Sadak Yojana) district-wise rural road connectivity data, or MoRTH road network datasets via data.gov.in.

### Government projects / investment
- Don't look for one master "investment" dataset — it doesn't exist. Search data.gov.in for scheme-wise expenditure (PMGSY financial data is a reasonable starting point) and normalize multiple scheme-specific sources into your own project/investment schema, same as every other category.

### Population/demographics — important correction, read this before building
Do **not** assume fresh "2026 Census" data is available or usable. As of now, India's decennial census (originally due 2021, delayed by COVID) is **still being conducted in two phases, concluding March 1, 2027** — it has not been released as a usable dataset. Using it as a live source would be building on a false assumption. Instead:
- Use **Census 2011** (the last actually published full census) for baseline population/village/district counts, and
- Use **NFHS-5** district estimates as a more recent demographic proxy where 2011 figures are too stale for a specific indicator.
- State this honestly in the README: *"Population figures sourced from Census 2011 (last published) and NFHS-5 district estimates; India's next census is in progress as of 2026 and not yet released."* This is a more credible statement than most teams will make, not a weakness — say it plainly rather than implying you have current census data.

## What to actually do with these

Don't hunt for one dataset containing everything — there isn't one. Pull 5–8 of the sources above, enough to cover **2–3 pilot districts across at least 2 states**, normalize them into your own schema (see the data model in the main build prompt), and tag every record with its real `source`, `source_url`, `retrieved_at`. Healthcare is the easiest category to start with, given the two confirmed geo-coded directories above — build that vertical slice end-to-end before adding education/water/roads.

## Worked example — feed this into your scoring engine as a sanity check

Before wiring the full dashboard, run this exact synthetic table through your Priority Score logic. These are illustrative numbers, not a spec to hardcode — the point is checking that your weighting produces sensible relative ordering:

| District | Population | Hospitals | Health infra gap | Investment | Citizen requests |
|---|---|---|---|---|---|
| District A | 12 lakh | 8 | High | ₹10 Cr | 185 |
| District B | 8 lakh | 12 | Low | ₹18 Cr | 42 |
| District C | 15 lakh | 5 | High | ₹6 Cr | 231 |

**Expected relative behavior:** District C should score highest — large population, fewest hospitals, high infra gap, highest citizen demand, lowest investment. District B should score lowest — low gap, high investment, low demand. District A sits in between. If your engine doesn't produce this ordering, adjust the weights before trusting it on real data.

**Gemini's explanation for District C**, grounded in these exact numbers, should read something like:
*"District C is prioritized because it combines a large affected population (15 lakh), a severe infrastructure shortfall (5 hospitals), high citizen-reported demand (231 requests), and comparatively low existing investment (₹6 Cr) — no equivalent major project currently addresses this gap."*
That specific-numbers, no-invented-claims tone is what every explanation panel should hit — use this as the reference example when prompting Gemini for the explanation layer.

## Synthetic citizen-request dataset — generation rules

- 150–300 requests total, spread across the same 2–3 pilot districts / 2+ states used for the real data above — don't generate synthetic demand for a district you have no real infrastructure data for, since that breaks the data-fusion story.
- Languages: English + Hindi + Marathi at minimum.
- Every record tagged `data_quality: synthetic`, visibly labeled "SYNTHETIC DEMO DATA" in the UI badge (see the main build prompt).
- Vary the phrasing for the same underlying need — e.g. "no proper hospital nearby," "PHC too far," "need government hospital," "no medical facility in our village" — so the Gemini clustering step actually has something to demonstrate. Identical wording for every healthcare request doesn't test clustering at all.
