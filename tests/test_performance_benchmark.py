"""Performance benchmarking and load testing for the MCP server."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
from typing import List, Dict, Any

from fastmcp import FastMCP, Client
from mcp.types import TextContent


class TestPerformanceBenchmarks:
    """Test performance benchmarks for the MCP server."""
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self):
        """Test performance of single request processing."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Performance test content"
        mock_result.title = "Performance Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Warm up
                await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/warmup"
                })
                
                # Benchmark single request
                start_time = time.perf_counter()
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/performance-test"
                })
                end_time = time.perf_counter()
                
                # Verify result
                assert result.isError is False
                assert result.content[0].text == "Performance test content"
                
                # Performance assertion
                execution_time = end_time - start_time
                assert execution_time < 0.1, f"Single request took {execution_time:.3f}s, expected < 0.1s"
                
                return execution_time
    
    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self):
        """Test performance under concurrent load."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent performance test"
        mock_result.title = "Concurrent Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test different concurrency levels
                concurrency_levels = [1, 5, 10, 20, 50]
                performance_results = {}
                
                for concurrency in concurrency_levels:
                    # Create concurrent tasks
                    tasks = []
                    start_time = time.perf_counter()
                    
                    for i in range(concurrency):
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/concurrent-{i}"
                            })
                        )
                        tasks.append(task)
                    
                    # Wait for all tasks
                    results = await asyncio.gather(*tasks)
                    end_time = time.perf_counter()
                    
                    # Verify all succeeded
                    for result in results:
                        assert result.isError is False
                        assert result.content[0].text == "Concurrent performance test"
                    
                    # Calculate performance metrics
                    total_time = end_time - start_time
                    requests_per_second = concurrency / total_time
                    avg_time_per_request = total_time / concurrency
                    
                    performance_results[concurrency] = {
                        'total_time': total_time,
                        'requests_per_second': requests_per_second,
                        'avg_time_per_request': avg_time_per_request
                    }
                    
                    # Performance assertions
                    assert total_time < 5.0, f"Concurrency {concurrency} took {total_time:.2f}s"
                    assert requests_per_second > 10, f"Only {requests_per_second:.1f} RPS for concurrency {concurrency}"
                
                # Verify performance scaling
                assert performance_results[50]['requests_per_second'] > performance_results[1]['requests_per_second']
                return performance_results
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Test maximum throughput under sustained load."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Throughput test content"
        mock_result.title = "Throughput Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Sustained load test
                duration = 2.0  # 2 seconds
                concurrency = 25
                
                start_time = time.perf_counter()
                end_time = start_time + duration
                
                completed_requests = 0
                active_tasks = set()
                
                while time.perf_counter() < end_time:
                    # Remove completed tasks
                    active_tasks = {task for task in active_tasks if not task.done()}
                    
                    # Add new tasks to maintain concurrency
                    while len(active_tasks) < concurrency and time.perf_counter() < end_time:
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/throughput-{completed_requests}"
                            })
                        )
                        active_tasks.add(task)
                        completed_requests += 1
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.001)
                
                # Wait for remaining tasks
                await asyncio.gather(*active_tasks, return_exceptions=True)
                
                actual_duration = time.perf_counter() - start_time
                throughput = completed_requests / actual_duration
                
                # Performance assertions (adjusted for realistic expectations)
                assert throughput > 40, f"Throughput was {throughput:.1f} RPS, expected > 40 RPS"
                assert completed_requests > 100, f"Only completed {completed_requests} requests in {actual_duration:.2f}s"
                
                return {
                    'throughput': throughput,
                    'completed_requests': completed_requests,
                    'duration': actual_duration
                }
    
    @pytest.mark.asyncio
    async def test_memory_usage_benchmark(self):
        """Test memory usage under load."""
        from server import mcp
        
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        mock_result = MagicMock()
        mock_result.markdown = "Memory test content"
        mock_result.title = "Memory Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Execute many requests to test memory usage
                tasks = []
                for i in range(100):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/memory-test-{i}"
                        })
                    )
                    tasks.append(task)
                
                # Wait for all tasks
                await asyncio.gather(*tasks)
                
                # Check memory usage after load
                peak_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = peak_memory - baseline_memory
                
                # Memory assertions (should not increase significantly)
                assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB, expected < 100MB"
                
                return {
                    'baseline_memory': baseline_memory,
                    'peak_memory': peak_memory,
                    'memory_increase': memory_increase
                }
    
    @pytest.mark.asyncio
    async def test_latency_distribution(self):
        """Test latency distribution under various loads."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Latency test content"
        mock_result.title = "Latency Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Collect latency measurements
                latencies = []
                
                for i in range(100):
                    start_time = time.perf_counter()
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/latency-test-{i}"
                    })
                    end_time = time.perf_counter()
                    
                    assert result.isError is False
                    latencies.append(end_time - start_time)
                
                # Calculate distribution statistics
                mean_latency = statistics.mean(latencies)
                median_latency = statistics.median(latencies)
                p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
                p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
                max_latency = max(latencies)
                
                # Latency assertions
                assert mean_latency < 0.05, f"Mean latency {mean_latency:.3f}s, expected < 0.05s"
                assert median_latency < 0.03, f"Median latency {median_latency:.3f}s, expected < 0.03s"
                assert p95_latency < 0.1, f"95th percentile latency {p95_latency:.3f}s, expected < 0.1s"
                assert p99_latency < 0.2, f"99th percentile latency {p99_latency:.3f}s, expected < 0.2s"
                assert max_latency < 0.5, f"Max latency {max_latency:.3f}s, expected < 0.5s"
                
                return {
                    'mean': mean_latency,
                    'median': median_latency,
                    'p95': p95_latency,
                    'p99': p99_latency,
                    'max': max_latency
                }


class TestLoadTesting:
    """Test system behavior under various load conditions."""
    
    @pytest.mark.asyncio
    async def test_gradual_load_increase(self):
        """Test system behavior under gradually increasing load."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Load test content"
        mock_result.title = "Load Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Gradually increase load
                load_levels = [1, 5, 10, 25, 50, 100]
                performance_metrics = {}
                
                for load_level in load_levels:
                    # Execute requests at this load level
                    start_time = time.perf_counter()
                    tasks = []
                    
                    for i in range(load_level):
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/load-{load_level}-{i}"
                            })
                        )
                        tasks.append(task)
                    
                    # Wait for all tasks
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.perf_counter()
                    
                    # Count successes and failures
                    successes = sum(1 for r in results if not isinstance(r, Exception) and not r.isError)
                    failures = len(results) - successes
                    
                    total_time = end_time - start_time
                    success_rate = successes / len(results) * 100
                    
                    performance_metrics[load_level] = {
                        'total_time': total_time,
                        'success_rate': success_rate,
                        'successes': successes,
                        'failures': failures
                    }
                    
                    # Performance assertions
                    assert success_rate > 95, f"Success rate {success_rate:.1f}% at load {load_level}"
                    assert total_time < 10.0, f"Load {load_level} took {total_time:.2f}s"
                
                return performance_metrics
    
    @pytest.mark.asyncio
    async def test_burst_load_handling(self):
        """Test system behavior under burst load conditions."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Burst test content"
        mock_result.title = "Burst Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test burst scenarios
                burst_sizes = [50, 100, 200]
                burst_results = {}
                
                for burst_size in burst_sizes:
                    # Create burst of requests
                    start_time = time.perf_counter()
                    tasks = []
                    
                    # All requests created simultaneously (burst)
                    for i in range(burst_size):
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/burst-{burst_size}-{i}"
                            })
                        )
                        tasks.append(task)
                    
                    # Wait for all tasks
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.perf_counter()
                    
                    # Analyze results
                    successes = sum(1 for r in results if not isinstance(r, Exception) and not r.isError)
                    failures = len(results) - successes
                    
                    total_time = end_time - start_time
                    success_rate = successes / len(results) * 100
                    
                    burst_results[burst_size] = {
                        'total_time': total_time,
                        'success_rate': success_rate,
                        'successes': successes,
                        'failures': failures
                    }
                    
                    # Burst handling assertions
                    assert success_rate > 90, f"Burst success rate {success_rate:.1f}% for size {burst_size}"
                    assert total_time < 15.0, f"Burst {burst_size} took {total_time:.2f}s"
                
                return burst_results
    
    @pytest.mark.asyncio
    async def test_sustained_load_endurance(self):
        """Test system endurance under sustained load."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Endurance test content"
        mock_result.title = "Endurance Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Sustained load test
                duration = 5.0  # 5 seconds
                concurrency = 20
                
                start_time = time.perf_counter()
                end_time = start_time + duration
                
                completed_requests = 0
                failed_requests = 0
                active_tasks = set()
                
                while time.perf_counter() < end_time:
                    # Process completed tasks
                    completed_tasks = {task for task in active_tasks if task.done()}
                    
                    for task in completed_tasks:
                        try:
                            result = await task
                            if result.isError:
                                failed_requests += 1
                            else:
                                completed_requests += 1
                        except Exception:
                            failed_requests += 1
                    
                    active_tasks -= completed_tasks
                    
                    # Add new tasks to maintain concurrency
                    while len(active_tasks) < concurrency and time.perf_counter() < end_time:
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/endurance-{completed_requests + failed_requests}"
                            })
                        )
                        active_tasks.add(task)
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)
                
                # Wait for remaining tasks
                remaining_results = await asyncio.gather(*active_tasks, return_exceptions=True)
                
                for result in remaining_results:
                    if isinstance(result, Exception) or result.isError:
                        failed_requests += 1
                    else:
                        completed_requests += 1
                
                actual_duration = time.perf_counter() - start_time
                total_requests = completed_requests + failed_requests
                success_rate = completed_requests / total_requests * 100
                average_throughput = total_requests / actual_duration
                
                # Endurance assertions
                assert success_rate > 95, f"Endurance success rate {success_rate:.1f}%"
                assert average_throughput > 30, f"Average throughput {average_throughput:.1f} RPS"
                assert completed_requests > 150, f"Only {completed_requests} requests completed"
                
                return {
                    'duration': actual_duration,
                    'total_requests': total_requests,
                    'completed_requests': completed_requests,
                    'failed_requests': failed_requests,
                    'success_rate': success_rate,
                    'average_throughput': average_throughput
                }
    
    @pytest.mark.asyncio
    async def test_connection_pool_stress(self):
        """Test connection pool behavior under stress."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Connection pool test"
        mock_result.title = "Connection Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Test multiple concurrent clients
            async def client_workload(client_id: int, requests_per_client: int):
                async with Client(mcp) as client:
                    tasks = []
                    for i in range(requests_per_client):
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/client-{client_id}-req-{i}"
                            })
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    successes = sum(1 for r in results if not isinstance(r, Exception) and not r.isError)
                    return successes, len(results)
            
            # Create multiple concurrent clients
            num_clients = 10
            requests_per_client = 20
            
            start_time = time.perf_counter()
            client_tasks = []
            
            for client_id in range(num_clients):
                task = asyncio.create_task(
                    client_workload(client_id, requests_per_client)
                )
                client_tasks.append(task)
            
            # Wait for all client workloads
            client_results = await asyncio.gather(*client_tasks)
            end_time = time.perf_counter()
            
            # Analyze results
            total_successes = sum(successes for successes, _ in client_results)
            total_requests = sum(total for _, total in client_results)
            
            success_rate = total_successes / total_requests * 100
            total_time = end_time - start_time
            
            # Connection pool assertions
            assert success_rate > 95, f"Connection pool success rate {success_rate:.1f}%"
            assert total_time < 10.0, f"Connection pool test took {total_time:.2f}s"
            assert total_requests == num_clients * requests_per_client
            
            return {
                'num_clients': num_clients,
                'requests_per_client': requests_per_client,
                'total_requests': total_requests,
                'total_successes': total_successes,
                'success_rate': success_rate,
                'total_time': total_time
            }


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    @pytest.mark.asyncio
    async def test_baseline_performance_metrics(self):
        """Test baseline performance metrics for regression detection."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Baseline test content"
        mock_result.title = "Baseline Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Baseline performance test
                baseline_metrics = {
                    'single_request_time': None,
                    'concurrent_10_time': None,
                    'concurrent_50_time': None,
                    'throughput_1s': None
                }
                
                # Single request baseline
                start_time = time.perf_counter()
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/baseline-single"
                })
                baseline_metrics['single_request_time'] = time.perf_counter() - start_time
                assert result.isError is False
                
                # Concurrent 10 baseline
                start_time = time.perf_counter()
                tasks = []
                for i in range(10):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/baseline-concurrent-10-{i}"
                        })
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)
                baseline_metrics['concurrent_10_time'] = time.perf_counter() - start_time
                
                # Concurrent 50 baseline
                start_time = time.perf_counter()
                tasks = []
                for i in range(50):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/baseline-concurrent-50-{i}"
                        })
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)
                baseline_metrics['concurrent_50_time'] = time.perf_counter() - start_time
                
                # Throughput baseline (1 second)
                start_time = time.perf_counter()
                end_time = start_time + 1.0
                completed = 0
                
                while time.perf_counter() < end_time:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/baseline-throughput-{completed}"
                    })
                    if not result.isError:
                        completed += 1
                
                baseline_metrics['throughput_1s'] = completed
                
                # Baseline assertions (these define our performance contract)
                assert baseline_metrics['single_request_time'] < 0.1, "Single request baseline too slow"
                assert baseline_metrics['concurrent_10_time'] < 2.0, "Concurrent 10 baseline too slow"
                assert baseline_metrics['concurrent_50_time'] < 5.0, "Concurrent 50 baseline too slow"
                assert baseline_metrics['throughput_1s'] > 20, "Throughput baseline too low"
                
                return baseline_metrics
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Memory leak test"
        mock_result.title = "Memory Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Monitor memory usage over time
                process = psutil.Process(os.getpid())
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                memory_samples = []
                
                # Run requests in batches and monitor memory
                for batch in range(5):
                    # Execute batch of requests
                    tasks = []
                    for i in range(50):
                        task = asyncio.create_task(
                            client.call_tool_mcp("web_content_extract", {
                                "url": f"https://example.com/memleak-batch-{batch}-{i}"
                            })
                        )
                        tasks.append(task)
                    
                    await asyncio.gather(*tasks)
                    
                    # Sample memory usage
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_samples.append(current_memory)
                    
                    # Small delay between batches
                    await asyncio.sleep(0.1)
                
                # Analyze memory trend
                final_memory = memory_samples[-1]
                memory_increase = final_memory - initial_memory
                
                # Calculate memory growth rate
                if len(memory_samples) > 1:
                    memory_growth_rate = (memory_samples[-1] - memory_samples[0]) / len(memory_samples)
                else:
                    memory_growth_rate = 0
                
                # Memory leak assertions
                assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB, possible leak"
                assert memory_growth_rate < 5, f"Memory growth rate {memory_growth_rate:.1f}MB/batch too high"
                
                return {
                    'initial_memory': initial_memory,
                    'final_memory': final_memory,
                    'memory_increase': memory_increase,
                    'memory_growth_rate': memory_growth_rate,
                    'memory_samples': memory_samples
                }
    
    @pytest.mark.asyncio
    async def test_performance_under_errors(self):
        """Test performance behavior when errors occur."""
        from server import mcp
        
        # Mix of successful and failing requests
        call_count = 0
        
        def mock_arun_with_errors(url, config=None):
            nonlocal call_count
            call_count += 1
            
            if call_count % 5 == 0:  # Every 5th request fails
                raise Exception(f"Simulated error on call {call_count}")
            
            mock_result = MagicMock()
            mock_result.markdown = f"Success content {call_count}"
            mock_result.title = "Success Test"
            mock_result.success = True
            return mock_result
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_arun_with_errors
            
            async with Client(mcp) as client:
                # Test performance with mixed success/error responses
                start_time = time.perf_counter()
                tasks = []
                
                for i in range(100):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/error-perf-{i}"
                        })
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.perf_counter()
                
                # Analyze results
                successes = 0
                app_errors = 0
                exceptions = 0
                
                for result in results:
                    if isinstance(result, Exception):
                        exceptions += 1
                    elif result.isError:
                        app_errors += 1
                    else:
                        # Check if it's an application-level error
                        if "Error extracting content" in result.content[0].text:
                            app_errors += 1
                        else:
                            successes += 1
                
                total_time = end_time - start_time
                
                # Performance under errors assertions
                assert total_time < 10.0, f"Error scenario took {total_time:.2f}s"
                assert successes > 70, f"Only {successes} successes out of 100 requests"
                assert app_errors > 15, f"Expected ~20 errors, got {app_errors}"
                
                return {
                    'total_time': total_time,
                    'successes': successes,
                    'app_errors': app_errors,
                    'exceptions': exceptions
                }