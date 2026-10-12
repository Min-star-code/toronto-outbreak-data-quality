# Data quality report

7,029 outbreak records from 11 yearly files. Each rule counts the records that fail it. Failing records are flagged, not deleted.

| Rule | Check | Failing records | % of records |
|---|---|---|---|
| R1 | Required fields are present (name, address, setting, type, agent, start date) | 0 | 0.00% |
| R2 | Outbreak setting is one of the seven published values | 0 | 0.00% |
| R3 | Outbreak type is Respiratory, Enteric, or Other | 0 | 0.00% |
| R4 | Date declared over is not before the date the outbreak began | 0 | 0.00% |
| R5 | Outbreak start year matches the yearly file it came from | 0 | 0.00% |
| R6 | Active flag agrees with the end date (active = no end date, closed = has end date) | 0 | 0.00% |
| R7 | No duplicate records (same institution, start date, type, and agent) | 6 | 0.09% |
| R8 | Duration is plausible (90 days or less) | 18 | 0.26% |
| R9 | Causative agent was identified (not 'Unable to identify' or 'Pending') | 671 | 9.55% |
| R10 | First agent field names a single agent (no comma-separated or 'and' lists) | 4 | 0.06% |
| R11 | Outbreak type agrees with the agent (norovirus is enteric; flu, COVID-19, RSV are respiratory) | 0 | 0.00% |
| R12 | Institution name is complete (does not end with a dangling hyphen) | 100 | 1.42% |
