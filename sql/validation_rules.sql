-- Every query returns the records that FAIL the rule. build.py counts them.

-- RULE R1: Required fields are present (name, address, setting, type, agent, start date)
SELECT * FROM outbreaks
WHERE institution_name = '' OR address = '' OR setting = ''
   OR outbreak_type = '' OR agent_1 = '' OR date_began = '';

-- RULE R2: Outbreak setting is one of the seven published values
SELECT * FROM outbreaks
WHERE setting NOT IN ('LTCH', 'Retirement Home', 'Hospital-Acute Care', 'Hospital-Chronic Care',
                      'Hospital-Psychiatric', 'Transitional Care', 'Shelter');

-- RULE R3: Outbreak type is Respiratory, Enteric, or Other
SELECT * FROM outbreaks
WHERE outbreak_type NOT IN ('Respiratory', 'Enteric', 'Other');

-- RULE R4: Date declared over is not before the date the outbreak began
SELECT * FROM outbreaks
WHERE date_over IS NOT NULL AND date_over < date_began;

-- RULE R5: Outbreak start year matches the yearly file it came from
SELECT * FROM outbreaks
WHERE CAST(substr(date_began, 1, 4) AS INTEGER) <> source_year;

-- RULE R6: Active flag agrees with the end date (active = no end date, closed = has end date)
SELECT * FROM outbreaks
WHERE (active = 'Y' AND date_over IS NOT NULL)
   OR (active = 'N' AND date_over IS NULL);

-- RULE R7: No duplicate records (same institution, start date, type, and agent)
SELECT o.* FROM outbreaks o
JOIN (SELECT institution_name, date_began, outbreak_type, agent_1
      FROM outbreaks
      GROUP BY institution_name, date_began, outbreak_type, agent_1
      HAVING COUNT(*) > 1) d
  ON  o.institution_name = d.institution_name AND o.date_began = d.date_began
  AND o.outbreak_type = d.outbreak_type AND o.agent_1 = d.agent_1;

-- RULE R8: Duration is plausible (90 days or less)
SELECT * FROM outbreaks
WHERE duration_days > 90;

-- RULE R9: Causative agent was identified (not 'Unable to identify' or 'Pending')
SELECT * FROM outbreaks
WHERE agent_group = 'Not identified';

-- RULE R10: First agent field names a single agent (no comma-separated or 'and' lists)
SELECT * FROM outbreaks
WHERE agent_1 LIKE '%,%' OR agent_1 LIKE '% and %';

-- RULE R11: Outbreak type agrees with the agent (norovirus is enteric; flu, COVID-19, RSV are respiratory)
SELECT * FROM outbreaks
WHERE (agent_group = 'Norovirus' AND outbreak_type <> 'Enteric')
   OR (agent_group IN ('COVID-19', 'Influenza A', 'Influenza B', 'RSV') AND outbreak_type <> 'Respiratory');

-- RULE R12: Institution name is complete (does not end with a dangling hyphen)
SELECT * FROM outbreaks
WHERE institution_name LIKE '%-';
