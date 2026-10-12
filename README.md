# Toronto healthcare outbreak records: data quality and reporting

Toronto Public Health publishes outbreaks in hospitals, long-term care homes, and retirement homes as one file per year. This project combines 11 yearly files into one validated table, documents every field, measures data quality with SQL rules, and produces reporting extracts.

## Findings

**Data quality**

- **7,029 outbreak records** from **11 yearly files** (January 2016 to 5 October 2026) combine without losing a row. The 2020 file names two columns differently and is aligned on load.
- The same site is written many ways: **4,199** distinct institution names reduce to **603** sites when grouped by address. **195** sites appear under more than one facility name.
- **66** free-text causative agent labels reduce to **13** groups using ordered keyword rules.
- "No second agent" is recorded two ways: blank in **5,711** records and the text `None` in **1,018**.
- Of **12** validation rules, **7** pass with no failures. The rest flag **671** records (9.5%) with no identified agent, **100** with a truncated institution name, **18** lasting over 90 days, **6** apparent duplicates, and **4** with several agents in one field. See [reports/data_quality_report.md](reports/data_quality_report.md).

**Reporting**

- Recorded outbreaks rose from **317** in 2019 to **1,133** in 2022 and have stayed near 1,000 a year since.
- COVID-19 accounts for **47.7%** of all records. Its share of each year's outbreaks peaked at **89.6%** in 2021 and fell to **26.1%** in 2025.
- The median closed outbreak lasted **13 days** (mean 16.5). Long-term care homes had the highest share lasting over 30 days (**10.2%**).
- **31.9%** of outbreaks began in December or January.

## Run

Python 3.10 or newer, standard library only.

```bash
python3 build.py
python3 -m unittest -v
```

`build.py` reads the raw files, writes `data/outbreaks_clean.csv`, loads `outbreaks.db`, runs the 12 rules in `sql/validation_rules.sql` and the 6 queries in `sql/report_queries.sql`, and writes the results to `reports/`.

## Cleaning decisions

| Issue in the source | Decision |
|---|---|
| 2020 file uses `Causative Agent - 1` instead of `Causative Agent-1` | Column names aligned before combining |
| Unit is appended to the institution name (`Michael Garron Hospital - H6`) | Split into `facility_name` and `unit`; original kept in `institution_name` |
| One site under many names | Not merged by guesswork. Records are grouped by normalized address (`site_key`) and labelled with the most common facility name at that address (`site_name`) |
| Address punctuation and case vary (`St. Clair`, `St.Clair`, `Mcnicoll`) | Compared with punctuation, spaces, and case removed |
| Agent labels vary (`Enterovirus/Rhinovirus`, `Enterovirus/ Rhinovirus`) | Grouped by keyword into `agent_group`; original kept in `agent_1` |
| Second agent blank or `None` | Both stored as empty |
| Active outbreaks have no end date | `duration_days` left empty, not zero |

Records that fail a validation rule are flagged in the report and kept in the table. Nothing is deleted.

## Limits

- Counts are reported outbreaks, not cases. The data has no number of people affected and no facility size, so it cannot compare risk between facilities.
- Changes over time partly reflect reporting practice: COVID-19 outbreak definitions and testing changed between 2020 and 2026.
- Grouping by address is imperfect. A few addresses host units of several hospitals, and a facility that moved appears as two sites.
- 2026 is a partial year.

## Files

- [data_dictionary.md](data_dictionary.md): every field in the clean table.
- `outbreak_report.xlsx`: Excel report built from the clean table with Power Query, with PivotTables and charts by year and setting, by causative agent group, and COVID-19 share by year.
- `data/raw/`: the 11 source files as downloaded on 11 October 2026.

## Data source

[Outbreaks in Toronto Healthcare Institutions](https://open.toronto.ca/dataset/outbreaks-in-toronto-healthcare-institutions/), Toronto Public Health, City of Toronto Open Data. Contains information licensed under the Open Government Licence – Toronto. This independent analysis is not endorsed by the City of Toronto.
