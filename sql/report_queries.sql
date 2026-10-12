-- Q1. Outbreaks per year by setting.
SELECT source_year,
       COUNT(*)                                       AS outbreaks,
       SUM(setting = 'LTCH')                          AS long_term_care,
       SUM(setting = 'Retirement Home')               AS retirement_home,
       SUM(setting LIKE 'Hospital%')                  AS hospital,
       SUM(setting IN ('Transitional Care', 'Shelter')) AS other_setting
FROM outbreaks
GROUP BY source_year
ORDER BY source_year;

-- Q2. Outbreaks by agent group, with share of all records and average duration.
SELECT agent_group,
       COUNT(*)                                       AS outbreaks,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM outbreaks), 1) AS pct_of_outbreaks,
       ROUND(AVG(duration_days), 1)                   AS avg_duration_days
FROM outbreaks
GROUP BY agent_group
ORDER BY outbreaks DESC;

-- Q3. Duration by setting for closed outbreaks.
SELECT setting,
       COUNT(duration_days)                           AS closed_outbreaks,
       ROUND(AVG(duration_days), 1)                   AS avg_duration_days,
       MAX(duration_days)                             AS longest_days,
       ROUND(100.0 * SUM(duration_days > 30) / COUNT(duration_days), 1) AS pct_over_30_days
FROM outbreaks
WHERE duration_days IS NOT NULL
GROUP BY setting
ORDER BY closed_outbreaks DESC;

-- Q4. COVID-19 share of outbreaks per year.
SELECT source_year,
       COUNT(*)                                       AS outbreaks,
       SUM(agent_group = 'COVID-19')                  AS covid_outbreaks,
       ROUND(100.0 * SUM(agent_group = 'COVID-19') / COUNT(*), 1) AS pct_covid
FROM outbreaks
GROUP BY source_year
ORDER BY source_year;

-- Q5. The ten sites with the most recorded outbreaks.
SELECT site_name,
       MIN(address)                                   AS address,
       MIN(setting)                                   AS setting,
       COUNT(*)                                       AS outbreaks,
       COUNT(DISTINCT facility_name)                  AS name_spellings
FROM outbreaks
GROUP BY site_key
ORDER BY outbreaks DESC
LIMIT 10;

-- Q6. Outbreaks by calendar month the outbreak began (all years combined).
SELECT substr(date_began, 6, 2)                       AS month,
       COUNT(*)                                       AS outbreaks,
       SUM(outbreak_type = 'Respiratory')             AS respiratory,
       SUM(outbreak_type = 'Enteric')                 AS enteric
FROM outbreaks
GROUP BY month
ORDER BY month;
