"""
Performance Benchmark Suite for Collection Storage Systems.
Compares SQLite vs File-based collection managers for performance validation.
"""
import time
import statistics
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from contextlib import contextmanager

from tools.collection_manager import CollectionFileManager
from tools.sqlite_collection_manager import SQLiteCollectionFileManager


class PerformanceBenchmark:
    """Benchmark suite for collection storage systems."""
    
    def __init__(self, num_iterations: int = 10):
        """Initialize benchmark with number of test iterations."""
        self.num_iterations = num_iterations
        self.results = {}
    
    @contextmanager
    def measure_time(self):
        """Context manager to measure execution time."""
        start_time = time.perf_counter()
        yield
        end_time = time.perf_counter()
        self.last_measurement = end_time - start_time
    
    def run_operation_benchmark(self, operation_name: str, operation_func, *args, **kwargs) -> float:
        """Run a benchmark operation multiple times and return average time."""
        times = []
        
        for _ in range(self.num_iterations):
            with self.measure_time():
                operation_func(*args, **kwargs)
            times.append(self.last_measurement)
        
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        self.results[operation_name] = {
            "avg_time": avg_time,
            "std_dev": std_dev,
            "min_time": min(times),
            "max_time": max(times),
            "all_times": times
        }
        
        return avg_time
    
    def benchmark_collection_creation(self, manager, collection_name: str) -> float:
        """Benchmark collection creation operation."""
        def create_operation():
            # Clean up if exists
            manager.delete_collection(collection_name)
            result = manager.create_collection(collection_name, "Benchmark collection")
            if not result["success"]:
                raise Exception(f"Collection creation failed: {result.get('error')}")
        
        return self.run_operation_benchmark("create_collection", create_operation)
    
    def benchmark_file_operations(self, manager, collection_name: str, num_files: int = 50) -> Dict[str, float]:
        """Benchmark file save/read operations."""
        # Ensure collection exists
        manager.create_collection(collection_name, "Benchmark collection")
        
        # Generate test data
        test_files = []
        for i in range(num_files):
            test_files.append({
                "filename": f"test_file_{i:03d}.md",
                "content": f"# Test File {i}\n\nThis is test content for file {i}.\n" + "A" * (100 + i * 10),
                "folder": f"folder_{i % 5}" if i % 3 == 0 else ""
            })
        
        # Benchmark save operations
        def save_files():
            for file_data in test_files:
                result = manager.save_file(
                    collection_name, 
                    file_data["filename"], 
                    file_data["content"], 
                    file_data["folder"]
                )
                if not result["success"]:
                    raise Exception(f"File save failed: {result.get('error')}")
        
        save_time = self.run_operation_benchmark("save_files", save_files)
        
        # Benchmark read operations
        def read_files():
            for file_data in test_files:
                result = manager.read_file(
                    collection_name, 
                    file_data["filename"], 
                    file_data["folder"]
                )
                if not result["success"]:
                    raise Exception(f"File read failed: {result.get('error')}")
        
        read_time = self.run_operation_benchmark("read_files", read_files)
        
        return {"save_time": save_time, "read_time": read_time}
    
    def benchmark_metadata_operations(self, manager, collection_name: str) -> Dict[str, float]:
        """Benchmark metadata-heavy operations."""
        # Ensure collection exists with some files
        manager.create_collection(collection_name, "Benchmark collection")
        
        # Add files to make metadata operations meaningful
        for i in range(20):
            manager.save_file(
                collection_name, 
                f"meta_test_{i}.md", 
                f"Content {i}", 
                f"folder_{i % 3}"
            )
        
        # Benchmark list collections
        list_collections_time = self.run_operation_benchmark(
            "list_collections", 
            lambda: manager.list_collections()
        )
        
        # Benchmark get collection info
        get_info_time = self.run_operation_benchmark(
            "get_collection_info", 
            lambda: manager.get_collection_info(collection_name)
        )
        
        # Benchmark list files in collection
        list_files_time = self.run_operation_benchmark(
            "list_files_in_collection",
            lambda: manager.list_files_in_collection(collection_name)
        )
        
        return {
            "list_collections": list_collections_time,
            "get_collection_info": get_info_time,
            "list_files_in_collection": list_files_time
        }
    
    def run_full_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete benchmark comparing SQLite vs File managers."""
        results = {
            "sqlite": {},
            "file": {},
            "performance_comparison": {},
            "benchmark_config": {
                "iterations": self.num_iterations,
                "test_files_count": 50
            }
        }
        
        # Create temporary directories for testing
        with tempfile.TemporaryDirectory() as sqlite_dir:
            with tempfile.TemporaryDirectory() as file_dir:
                
                # Initialize managers
                sqlite_manager = SQLiteCollectionFileManager(Path(sqlite_dir))
                file_manager = CollectionFileManager(Path(file_dir))
                
                try:
                    # Test SQLite manager
                    print("Benchmarking SQLite manager...")
                    
                    # Collection creation
                    results["sqlite"]["create_collection"] = self.benchmark_collection_creation(
                        sqlite_manager, "sqlite_benchmark"
                    )
                    
                    # File operations
                    file_ops = self.benchmark_file_operations(sqlite_manager, "sqlite_benchmark")
                    results["sqlite"].update(file_ops)
                    
                    # Metadata operations
                    meta_ops = self.benchmark_metadata_operations(sqlite_manager, "sqlite_benchmark")
                    results["sqlite"].update(meta_ops)
                    
                    # Reset results for file manager
                    self.results = {}
                    
                    # Test File manager
                    print("Benchmarking File manager...")
                    
                    # Collection creation
                    results["file"]["create_collection"] = self.benchmark_collection_creation(
                        file_manager, "file_benchmark"
                    )
                    
                    # File operations
                    file_ops = self.benchmark_file_operations(file_manager, "file_benchmark")
                    results["file"].update(file_ops)
                    
                    # Metadata operations
                    meta_ops = self.benchmark_metadata_operations(file_manager, "file_benchmark")
                    results["file"].update(meta_ops)
                    
                    # Calculate performance improvements
                    for operation in results["sqlite"]:
                        if operation in results["file"]:
                            sqlite_time = results["sqlite"][operation]
                            file_time = results["file"][operation]
                            
                            improvement_percent = ((file_time - sqlite_time) / file_time) * 100
                            speedup_factor = file_time / sqlite_time if sqlite_time > 0 else float('inf')
                            
                            results["performance_comparison"][operation] = {
                                "sqlite_time": sqlite_time,
                                "file_time": file_time,
                                "improvement_percent": improvement_percent,
                                "speedup_factor": speedup_factor,
                                "target_met": improvement_percent >= 20.0
                            }
                    
                    # Overall performance summary
                    improvements = [
                        comp["improvement_percent"] 
                        for comp in results["performance_comparison"].values()
                    ]
                    
                    results["performance_summary"] = {
                        "average_improvement_percent": statistics.mean(improvements),
                        "median_improvement_percent": statistics.median(improvements),
                        "min_improvement_percent": min(improvements),
                        "max_improvement_percent": max(improvements),
                        "target_met_overall": statistics.mean(improvements) >= 20.0,
                        "operations_meeting_target": sum(
                            1 for comp in results["performance_comparison"].values() 
                            if comp["target_met"]
                        )
                    }
                    
                finally:
                    # Clean up
                    sqlite_manager.close()
        
        return results
    
    def print_benchmark_results(self, results: Dict[str, Any]) -> None:
        """Print benchmark results in a readable format."""
        print("\n" + "="*80)
        print("COLLECTION STORAGE PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        summary = results["performance_summary"]
        print(f"\nOVERALL PERFORMANCE SUMMARY:")
        print(f"Average Improvement: {summary['average_improvement_percent']:.1f}%")
        print(f"Median Improvement:  {summary['median_improvement_percent']:.1f}%")
        print(f"Target Met (≥20%):   {'✅ YES' if summary['target_met_overall'] else '❌ NO'}")
        print(f"Operations Meeting Target: {summary['operations_meeting_target']}/{len(results['performance_comparison'])}")
        
        print(f"\nDETAILED OPERATION COMPARISON:")
        print(f"{'Operation':<25} {'SQLite (ms)':<12} {'File (ms)':<12} {'Improvement':<12} {'Target Met'}")
        print("-" * 75)
        
        for operation, comparison in results["performance_comparison"].items():
            sqlite_ms = comparison["sqlite_time"] * 1000
            file_ms = comparison["file_time"] * 1000
            improvement = comparison["improvement_percent"]
            target_met = "✅" if comparison["target_met"] else "❌"
            
            print(f"{operation:<25} {sqlite_ms:<12.2f} {file_ms:<12.2f} {improvement:<12.1f}% {target_met}")
        
        print(f"\nBENCHMARK CONFIGURATION:")
        config = results["benchmark_config"]
        print(f"Iterations per test: {config['iterations']}")
        print(f"Test files count: {config['test_files_count']}")
        
        print("\n" + "="*80)


def run_performance_benchmark(iterations: int = 10, save_results: bool = True) -> Dict[str, Any]:
    """Run the performance benchmark and optionally save results."""
    benchmark = PerformanceBenchmark(iterations)
    results = benchmark.run_full_benchmark_suite()
    benchmark.print_benchmark_results(results)
    
    if save_results:
        # Save results to file
        results_file = Path("performance_benchmark_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    # Run benchmark with default settings
    results = run_performance_benchmark(iterations=5)
    
    # Print summary
    summary = results["performance_summary"]
    if summary["target_met_overall"]:
        print(f"\n🎉 Performance target achieved! Average improvement: {summary['average_improvement_percent']:.1f}%")
    else:
        print(f"\n⚠️  Performance target not met. Average improvement: {summary['average_improvement_percent']:.1f}%")