"""Median load and generation seconds per model from a job-timing CSV.
Usage: python cold_vs_warm.py image-job-timings-20261106.csv
Columns used: model, load_seconds, generation_seconds.
'Cold' = a job whose load_seconds was above 0.
"""
import csv, sys, statistics, collections

by = collections.defaultdict(list)
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    by[r["model"]].append(r)
for model, rs in sorted(by.items()):
    gen = [float(r["generation_seconds"]) for r in rs]
    cold = [float(r["load_seconds"]) for r in rs if float(r["load_seconds"] or 0) > 0]
    load = f"{statistics.median(cold):.1f}" if cold else "n/a"
    print(f"{model}: {len(rs)} jobs, median generation {statistics.median(gen):.1f} s, "
          f"{len(cold)} cold, median cold load {load} s")
