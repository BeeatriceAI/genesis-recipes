"""Idle hours per day for one GPU from a daily summary CSV.
Usage: python idle_hours.py gpu_daily_usage_UTC.csv GPU_INDEX FIRST_DATE LAST_DATE
Columns used: date_utc, gpu_index, samples, minutes_util_ge_50 (one sample about once a minute).
'Under 50 percent' = samples minus minutes with utilisation at or above 50 percent.
"""
import csv, sys

path, gpu, first, last = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
rows = [r for r in csv.DictReader(open(path, encoding="utf-8"))
        if r["gpu_index"] == gpu and first <= r["date_utc"] <= last]
under = [int(r["samples"]) - int(r["minutes_util_ge_50"]) for r in rows]
print(f"GPU {gpu}, {first} to {last}: {len(rows)} dates")
print(f"minutes under 50 percent: {sum(under)}")
print(f"mean hours per day under 50 percent: {sum(under) / 60 / len(rows):.2f}")
print(f"lowest day {min(under) / 60:.2f} h, highest day {max(under) / 60:.2f} h")
