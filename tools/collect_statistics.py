"""
Sentio System Statistics Collector
Collects module, class, function, and file statistics for diagnostics and health check.
"""
import os
import sys
import importlib
import pkgutil
import inspect
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENTIO_DIR = os.path.join(BASE_DIR, "sentio")

stats = {
    "modules": 0,
    "classes": 0,
    "functions": 0,
    "files": 0,
    "lines": 0,
    "top_modules": [],
    "top_classes": [],
    "top_functions": [],
}

module_class_counter = Counter()
module_func_counter = Counter()
file_line_counter = Counter()

for root, dirs, files in os.walk(SENTIO_DIR):
    for file in files:
        if file.endswith(".py"):
            stats["files"] += 1
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                stats["lines"] += len(lines)
                file_line_counter[file_path] = len(lines)
            # Try to import module and inspect
            rel_path = os.path.relpath(file_path, SENTIO_DIR)
            mod_name = rel_path.replace(os.sep, ".")[:-3]
            try:
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                stats["modules"] += 1
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    stats["classes"] += 1
                    module_class_counter[mod_name] += 1
                for name, obj in inspect.getmembers(mod, inspect.isfunction):
                    stats["functions"] += 1
                    module_func_counter[mod_name] += 1
            except Exception:
                continue

stats["top_modules"] = module_class_counter.most_common(5)
stats["top_classes"] = module_class_counter.most_common(5)
stats["top_functions"] = module_func_counter.most_common(5)
stats["largest_files"] = file_line_counter.most_common(5)

if __name__ == "__main__":
    print("Sentio System Statistics:")
    for k, v in stats.items():
        print(f"{k}: {v}")
