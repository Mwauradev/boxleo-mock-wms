import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from integrate import main

results = main()
labels = [f"{r[0][:10]}\n({r[1].split()[0]})" for r in results if r[3] is not None]
stored = [r[2] for r in results if r[3] is not None]
calculated = [r[3] for r in results if r[3] is not None]

x = range(len(labels))
fig, ax = plt.subplots(figsize=(13, 6))
width = 0.35
ax.bar([i - width/2 for i in x], stored, width, label="Stored ROP (arbitrary, Day 18)", color="#FF7F0E")
ax.bar([i + width/2 for i in x], calculated, width, label="Calculated ROP (from real demand history)", color="#1F77B4")
ax.set_xticks(list(x))
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Reorder point (units)")
ax.set_title("Auditing stored reorder points against actual demand data")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("/mnt/user-data/outputs/rop_audit_chart.png", dpi=150)
print("saved")
