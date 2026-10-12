# Data dictionary: `outbreaks`

One row per declared outbreak. Table in `outbreaks.db`; same columns in `data/outbreaks_clean.csv`.

| Field | Type | Source | Description | Allowed values / rule |
|---|---|---|---|---|
| `outbreak_id` | integer | derived | Row number assigned after combining the files | Unique, 1 to 7,029 |
| `source_year` | integer | file name | Year of the file the record came from | 2016 to 2026; equals the year of `date_began` |
| `institution_name` | text | Institution Name | Name exactly as published, spaces tidied | Required |
| `facility_name` | text | derived | Part of `institution_name` before the first ` - ` | Required |
| `unit` | text | derived | Part of `institution_name` after the first ` - ` (ward, floor) | Empty when no unit is given |
| `address` | text | Institution Address | Street address as published | Required |
| `site_key` | text | derived | Address in lowercase with spaces and punctuation removed | Identifies a physical site |
| `site_name` | text | derived | Most common `facility_name` at that `site_key` | One name per site |
| `setting` | text | Outbreak Setting | Type of institution | LTCH, Retirement Home, Hospital-Acute Care, Hospital-Chronic Care, Hospital-Psychiatric, Transitional Care, Shelter |
| `outbreak_type` | text | Type of Outbreak | Category of illness | Respiratory, Enteric, Other |
| `agent_1` | text | Causative Agent-1 | First causative agent as published | Required; 66 distinct labels |
| `agent_2` | text | Causative Agent-2 | Second causative agent | Empty when none (source uses blank or `None`) |
| `agent_group` | text | derived | `agent_1` grouped by keyword rule | 13 groups, including `Not identified` and `Other` |
| `date_began` | date (YYYY-MM-DD) | Date Outbreak Began | Date the outbreak started | Required |
| `date_over` | date (YYYY-MM-DD) | Date Declared Over | Date the outbreak was declared over | Empty while active; not before `date_began` |
| `duration_days` | integer | derived | `date_over` minus `date_began` | Empty while active; over 90 is flagged for review |
| `active` | text | Active | Whether the outbreak is still active | `Y` (no `date_over`) or `N` (has `date_over`) |

LTCH means long-term care home. CPE means carbapenemase-producing Enterobacteriaceae.
