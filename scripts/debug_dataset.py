# Quick code to debug datasets
from config.dijet_2025_new import config

d = config.datasets.get("DataDijet")
print(f"Dataset: {d}")

print("")
print(d.get_files()[:2])