"""Compaction records summary.
Usage: python compaction_summary.py compaction-records-20261107.csv
Columns used: session_masked, seconds, status.
"""
import csv, sys, statistics, collections

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
status = collections.Counter(r["status"] for r in rows)
done = [float(r["seconds"]) for r in rows if r["status"] == "completed"]
sessions = collections.Counter(r["session_masked"] for r in rows)
print(f"{len(rows)} records: {dict(status)}")
print(f"median completed seconds: {statistics.median(done):.1f}")
print(f"largest single session: {sessions.most_common(1)[0][1]} of {len(rows)} records")
