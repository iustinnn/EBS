import time
import psutil
import matplotlib.pyplot as plt
from generator import DataGenerator
from values import GENERAL_CONFIG, SUB_VALUES
from collections import Counter


def verify_field_distribution(subscriptions):
    """Verify and display the actual percentage distribution of fields in subscriptions."""
    total_subs = len(subscriptions)
    field_counts = Counter()
    
    # Count fields in all subscriptions
    for sub in subscriptions:
        for field in sub.keys():
            field_counts[field] += 1
    
    # Get expected weights from config
    expected_weights = SUB_VALUES["field_weights"]
    
    # Display results
    print("\nField Distribution Analysis:")
    print(f"{'Field':<10} {'Count':<8} {'Actual %':<10} {'Expected %':<10} {'Difference':<10}")
    print("-" * 50)
    
    for field, count in field_counts.items():
        actual_percent = (count / total_subs) * 100
        expected_percent = expected_weights.get(field, 0) * 100
        difference = actual_percent - expected_percent
        
        print(f"{field:<10} {count:<8} {actual_percent:6.2f}%    {expected_percent:6.2f}%    {difference:+6.2f}%")


def get_system_info():
    info = {
        "cpu_frequency": f"{psutil.cpu_freq().current:.2f} MHz" if hasattr(psutil, 'cpu_freq') else "Unknown",
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram": round(psutil.virtual_memory().total / (1024**3), 2)
    }
    return info


def run_test(num_processes, num_items):
    # Update the number of processes in the config
    GENERAL_CONFIG["parallelization"]["num_threads"] = num_processes
    GENERAL_CONFIG["num_publications"] = num_items
    GENERAL_CONFIG["num_subscriptions"] = num_items
    
    generator = DataGenerator()
    start_time = time.time()
    publications, subscriptions = generator.generate_data()
    total_time = time.time() - start_time
    
    # Save the generated data to JSON files
    generator.save_data(publications, subscriptions)
    print(f"Saved {len(publications)} publications to publications.json")
    print(f"Saved {len(subscriptions)} subscriptions to subscriptions.json")
    
    # Verify the field distribution
    verify_field_distribution(subscriptions)
    
    return total_time


def main():
    system_info = get_system_info()
    print("\nSystem Information:")
    print(f"CPU Frequency: {system_info['cpu_frequency']}")
    print(f"CPU Cores: {system_info['cpu_cores']}")
    print(f"CPU Threads: {system_info['cpu_threads']}")
    print(f"RAM: {system_info['ram']} GB")

    # Test parameters
    #data_sizes = [10, 100, 1000, 10000]
    data_sizes = [10000]
    #process_counts = [1, 8]  # Testing with 1 and 8 processes
    process_counts = [8]  # Testing with 1 and 8 processes
    results = {8: []}
    #results = {1: [], 8: []}  # Store results for each process count

    print("\nRunning tests for different data sizes...")
    for num_items in data_sizes:
        print(f"\nTesting with {num_items} items...")
        for num_processes in process_counts:
            print(f"  Using {num_processes} process{'es' if num_processes > 1 else ''}...")
            execution_time = run_test(num_processes, num_items)
            results[num_processes].append(execution_time)
            print(f"  Time taken: {execution_time:.2f} seconds")

    # Create and save the plot
    plt.figure(figsize=(12, 7))
    
    # Plot lines for each process count with different colors
    #plt.plot(data_sizes, results[1], 'b-', label='1 Process', marker='o')
    plt.plot(data_sizes, results[8], 'g-', label='8 Processes', marker='^')
    
    plt.xlabel('Number of Publications and Subscriptions')
    plt.ylabel('Time (seconds)')
    plt.title('Execution Time vs Data Size\nComparison of 1 vs 8 Processes')
    plt.grid(True)
    plt.legend()
    
    # Use logarithmic scale for x-axis
    plt.xscale('log')
    plt.xticks(data_sizes, [str(x) for x in data_sizes])
    
    # Save the plot
    plt.savefig('test.png')
    print("\nPlot saved as 'process_comparison_1v8.png'")

    # Print results in a table format
    print("\nResults Summary:")
    print("Data Size | 8 Processes (s)")
    print("-" * 30)
    for i, size in enumerate(data_sizes):
        print(f"{size:^9} | {results[8][i]:^12.2f}")


if __name__ == "__main__":
    main()