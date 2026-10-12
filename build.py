"""Combine, clean, and validate Toronto healthcare outbreak records.

Run:  python3 build.py
Reads   data/raw/ob_report_<year>.csv       (11 yearly files, never edited)
Writes  data/outbreaks_clean.csv            (one row per outbreak, for Excel)
        outbreaks.db                        (SQLite table `outbreaks`)
        reports/data_quality_report.md      (result of every validation rule)
        reports/q*.csv                      (results of sql/report_queries.sql)
        reports/summary.json
"""

import csv
import json
import re
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "outbreaks_clean.csv"
DB = ROOT / "outbreaks.db"
REPORTS = ROOT / "reports"

# The 2020 file spells two column names differently from every other year.
COLUMN_FIXES = {
    "Causative Agent - 1": "Causative Agent-1",
    "Causative Agent - 2": "Causative Agent-2",
}

# Ordered keyword rules that reduce 66 free-text agent labels to 12 groups.
# 'parainfluenza' must be checked before 'influenza' because it contains it.
AGENT_RULES = [
    ("covid", "COVID-19"),
    ("parainfluenza", "Parainfluenza"),
    ("influenza a", "Influenza A"),
    ("influenza b", "Influenza B"),
    ("respiratory syncytial", "RSV"),
    ("rhinovirus", "Rhinovirus / Enterovirus"),
    ("enterovirus", "Rhinovirus / Enterovirus"),
    ("coronavirus", "Coronavirus (other)"),
    ("metapneumovirus", "Metapneumovirus"),
    ("norovirus", "Norovirus"),
    ("clostridium", "C. difficile"),
    ("cpe", "CPE"),
]
NOT_IDENTIFIED = {"", "unable to identify", "pending"}


def tidy(text):
    """Trim the ends and collapse repeated spaces."""
    return re.sub(r"\s+", " ", text or "").strip()


def agent_group(label):
    lowered = label.lower()
    if lowered in NOT_IDENTIFIED:
        return "Not identified"
    for keyword, group in AGENT_RULES:
        if keyword in lowered:
            return group
    return "Other"


def address_key(address):
    """Make '2701 St. Clair Ave E' and '2701 St.Clair Ave E' compare equal."""
    return re.sub(r"[^a-z0-9]", "", address.lower())


def split_institution(name):
    """Split 'Michael Garron Hospital - H6' into facility and unit."""
    parts = re.split(r"\s+-\s+", name, maxsplit=1)
    return parts[0], (parts[1] if len(parts) > 1 else None)


def read_raw():
    rows = []
    for path in sorted(RAW_DIR.glob("ob_report_*.csv")):
        source_year = int(path.stem[-4:])
        with open(path, encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                row = {COLUMN_FIXES.get(key, key): tidy(value) for key, value in raw.items()}
                row["source_year"] = source_year
                rows.append(row)
    return rows


def clean(raw_rows):
    # The same site is written many ways ('Rekai Centre', 'The Rekai Centre At
    # Sherbourne Place'). Names are not merged by guesswork: records are grouped
    # by address, and each address is labelled with its most common facility name.
    names_at_address = defaultdict(Counter)
    for row in raw_rows:
        facility, _ = split_institution(row["Institution Name"])
        names_at_address[address_key(row["Institution Address"])][facility] += 1

    rows = []
    for number, row in enumerate(raw_rows, start=1):
        facility, unit = split_institution(row["Institution Name"])
        key = address_key(row["Institution Address"])
        began = row["Date Outbreak Began"]
        ended = row["Date Declared Over"] or None
        duration = (date.fromisoformat(ended) - date.fromisoformat(began)).days if ended else None
        second = row["Causative Agent-2"]
        rows.append({
            "outbreak_id": number,
            "source_year": row["source_year"],
            "institution_name": row["Institution Name"],
            "facility_name": facility,
            "unit": unit,
            "address": row["Institution Address"],
            "site_key": key,
            "site_name": names_at_address[key].most_common(1)[0][0],
            "setting": row["Outbreak Setting"],
            "outbreak_type": row["Type of Outbreak"],
            "agent_1": row["Causative Agent-1"],
            # Blank and the text 'None' both mean no second agent.
            "agent_2": second if second not in ("", "None") else None,
            "agent_group": agent_group(row["Causative Agent-1"]),
            "date_began": began,
            "date_over": ended,
            "duration_days": duration,
            "active": row["Active"],
        })
    return rows


def load(rows):
    columns = list(rows[0].keys())
    with open(CLEAN, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    DB.unlink(missing_ok=True)
    db = sqlite3.connect(DB)
    db.execute(f"CREATE TABLE outbreaks ({', '.join(columns)})")
    db.executemany(
        f"INSERT INTO outbreaks VALUES ({', '.join('?' for _ in columns)})",
        [tuple(row.values()) for row in rows],
    )
    db.commit()
    return db


def run_validation(db):
    """Each rule in sql/validation_rules.sql returns the rows that FAIL it."""
    text = (ROOT / "sql" / "validation_rules.sql").read_text()
    results = []
    for block in text.split("-- RULE ")[1:]:
        header, query = block.split("\n", 1)
        rule_id, description = header.split(": ", 1)
        failing = db.execute(f"SELECT COUNT(*) FROM ({query.strip().rstrip(';')})").fetchone()[0]
        results.append((rule_id, description, failing))
    return results


def run_reports(db):
    queries = (ROOT / "sql" / "report_queries.sql").read_text().split(";")
    number = 0
    for query in queries:
        if "SELECT" not in query:
            continue
        number += 1
        cursor = db.execute(query)
        with open(REPORTS / f"q{number}.csv", "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor.fetchall())


def main():
    raw_rows = read_raw()
    rows = clean(raw_rows)
    db = load(rows)
    REPORTS.mkdir(exist_ok=True)
    results = run_validation(db)
    run_reports(db)

    total = len(rows)
    lines = [
        "# Data quality report",
        "",
        f"{total:,} outbreak records from {len({r['source_year'] for r in rows})} yearly files. "
        "Each rule counts the records that fail it. Failing records are flagged, not deleted.",
        "",
        "| Rule | Check | Failing records | % of records |",
        "|---|---|---|---|",
    ]
    for rule_id, description, failing in results:
        lines.append(f"| {rule_id} | {description} | {failing:,} | {100 * failing / total:.2f}% |")
    (REPORTS / "data_quality_report.md").write_text("\n".join(lines) + "\n")

    durations = [r["duration_days"] for r in rows if r["duration_days"] is not None]
    summary = {
        "source_files": len({r["source_year"] for r in rows}),
        "records": total,
        "raw_institution_names": len({r["institution_name"] for r in rows}),
        "facility_names_after_removing_unit": len({r["facility_name"] for r in rows}),
        "raw_addresses": len({r["address"] for r in rows}),
        "sites_by_address": len({r["site_key"] for r in rows}),
        "sites_with_more_than_one_facility_name": sum(
            1 for key in {r["site_key"] for r in rows}
            if len({r["facility_name"] for r in rows if r["site_key"] == key}) > 1),
        "raw_agent_labels": len({r["agent_1"] for r in rows}),
        "agent_groups": len({r["agent_group"] for r in rows}),
        "second_agent_blank": sum(1 for r in raw_rows if r["Causative Agent-2"] == ""),
        "second_agent_text_none": sum(1 for r in raw_rows if r["Causative Agent-2"] == "None"),
        "median_duration_days": statistics.median(durations),
        "mean_duration_days": round(statistics.mean(durations), 1),
        "validation": {rule_id: failing for rule_id, _, failing in results},
    }
    (REPORTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
