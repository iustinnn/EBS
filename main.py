import time
import psutil
from generator import DataGenerator
from values import GENERAL_CONFIG


def get_system_info():
    info = {
        "cpu_frequency": f"{psutil.cpu_freq().current:.2f} MHz" if hasattr(psutil, 'cpu_freq') else "Unknown",
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram": round(psutil.virtual_memory().total / (1024 ** 3), 2)
    }
    return info


def main():
    system_info = get_system_info()
    print("\nSystem Information:")
    print(f"CPU Frequency: {system_info['cpu_frequency']}")
    print(f"CPU Cores: {system_info['cpu_cores']}")
    print(f"CPU Threads: {system_info['cpu_threads']}")
    print(f"RAM: {system_info['ram']} GB")

    num_processes = GENERAL_CONFIG['parallelization']['num_processes']

    generator = DataGenerator()
    sample_publications, _ = generator.generate_data()
    num_publications = len(sample_publications)

    filename = f"{num_processes}_{num_publications}.txt"

    with open(filename, "w") as file:
        for i in range(5):
            generator = DataGenerator()

            print(f"\nRun {i + 1}: Generating data...")
            start_time = time.time()

            publications, subscriptions = generator.generate_data()

            total_time = time.time() - start_time
            print(f"Run {i + 1} completed in {total_time:.2f} seconds")

            file.write(f"{total_time:.2f}\n")

            print("Data generation done.")

    print(f"\nExecution times written to {filename}")


if __name__ == "__main__":
    main()