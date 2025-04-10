import os
import matplotlib.pyplot as plt

process_counts = [1, 4, 8]
data_sizes = [10, 100, 1000, 10000, 100000]

results = {p: [] for p in process_counts}

for p in process_counts:
    for size in data_sizes:
        filename = f"{p}_{size}.txt"
        try:
            with open(filename, "r") as f:
                times = [float(line.strip()) for line in f.readlines() if line.strip()]
                avg_time = sum(times) / len(times)
                results[p].append(avg_time)
        except FileNotFoundError:
            print(f"File not found: {filename}")
            results[p].append(None)  

plt.figure(figsize=(10, 6))
for p in process_counts:
    if all(time is not None for time in results[p]):
        plt.plot(data_sizes, results[p], marker='o', label=f'{p} Processes')

plt.xlabel("Data Size")
plt.ylabel("Average Execution Time (s)")
plt.title("Execution Time vs Data Size for Different Process Counts")
plt.xscale("log")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("graph.png")
