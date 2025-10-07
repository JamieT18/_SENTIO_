"""
Performance and scalability utilities for Sentio 2.0
"""
import numpy as np
import concurrent.futures
from typing import Callable, List, Any
import multiprocessing
import time
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
# Performance and scalability utilities for Sentio

class ParallelExecutor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def run_parallel(self, func: Callable, data: List[Any]) -> List[Any]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(func, data))
        return results

class BatchProcessor:
    def process_batches(self, func: Callable, data: np.ndarray, batch_size: int = 100) -> List[Any]:
        results = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            results.append(func(batch))
        return results

class ProcessParallelExecutor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def run_parallel(self, func: Callable, data: List[Any]) -> List[Any]:
        with multiprocessing.Pool(self.max_workers) as pool:
            results = pool.map(func, data)
        return results

class GPUBatchProcessor:
    def process_batches(self, func: Callable, data: np.ndarray, batch_size: int = 100):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available for GPU processing.")
        results = []
        for i in range(0, len(data), batch_size):
            batch = torch.tensor(data[i:i+batch_size]).cuda()
            results.append(func(batch))
        return results

class Benchmark:
    @staticmethod
    def timeit(func: Callable, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return {'result': result, 'elapsed': end - start}
