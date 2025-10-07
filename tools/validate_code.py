#!/usr/bin/env python3
"""
Code quality validation script for Sentio
Checks for common issues without requiring external dependencies
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple


def check_syntax(directory: Path = Path("sentio")) -> List[str]:
    """Check all Python files for syntax errors"""
    errors = []
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            errors.append(f"{py_file}: Line {e.lineno}: {e.msg}")
    return errors


def check_imports(directory: Path = Path("sentio")) -> List[str]:
    """Check for wildcard imports (bad practice)"""
    issues = []
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        with open(py_file) as f:
            content = f.read()
            if "import *" in content and "from __future__" not in content:
                for i, line in enumerate(content.split("\n"), 1):
                    if "import *" in line and not line.strip().startswith("#"):
                        issues.append(f"{py_file}: Line {i}: Wildcard import detected")
    return issues


def check_mutable_defaults(directory: Path = Path("sentio")) -> List[str]:
    """Check for mutable default arguments"""
    issues = []
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        with open(py_file) as f:
            try:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for default in node.args.defaults:
                            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                                issues.append(
                                    f"{py_file}: Line {node.lineno}: "
                                    f"Function '{node.name}' has mutable default argument"
                                )
            except SyntaxError:
                pass  # Already caught by syntax check
    return issues


def check_todos(directory: Path = Path("sentio")) -> List[Tuple[str, int, str]]:
    """Find TODO/FIXME comments"""
    todos = []
    keywords = ["TODO", "FIXME", "XXX", "HACK", "BUG"]
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        with open(py_file) as f:
            for i, line in enumerate(f, 1):
                for keyword in keywords:
                    if keyword in line and "#" in line:
                        todos.append((str(py_file), i, line.strip()))
                        break
    return todos


def main():
    """Run all code quality checks"""
    print("=" * 70)
    print("SENTIO - CODE QUALITY VALIDATION")
    print("=" * 70)
    
    all_passed = True
    
    # Check syntax
    print("\n1️⃣  Checking Python syntax...")
    syntax_errors = check_syntax()
    if syntax_errors:
        print("   ❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"      {error}")
        all_passed = False
    else:
        print("   ✅ All Python files have valid syntax")
    
    # Check imports
    print("\n2️⃣  Checking for wildcard imports...")
    import_issues = check_imports()
    if import_issues:
        print("   ⚠️  Wildcard imports found (consider being explicit):")
        for issue in import_issues:
            print(f"      {issue}")
    else:
        print("   ✅ No wildcard imports detected")
    
    # Check mutable defaults
    print("\n3️⃣  Checking for mutable default arguments...")
    mutable_issues = check_mutable_defaults()
    if mutable_issues:
        print("   ⚠️  Mutable default arguments found:")
        for issue in mutable_issues:
            print(f"      {issue}")
    else:
        print("   ✅ No mutable default arguments detected")
    
    # Check TODOs
    print("\n4️⃣  Checking for TODO/FIXME comments...")
    todos = check_todos()
    if todos:
        print(f"   ℹ️  Found {len(todos)} TODO/FIXME comments:")
        for file, line, content in todos[:5]:  # Show first 5
            print(f"      {file}:{line}: {content[:60]}")
        if len(todos) > 5:
            print(f"      ... and {len(todos) - 5} more")
    else:
        print("   ✅ No TODO/FIXME comments found")
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ CODE QUALITY VALIDATION PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ CODE QUALITY VALIDATION FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
