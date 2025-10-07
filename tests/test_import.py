"""
Simple import test to verify package structure
"""
import sys
import os

print("Testing Sentio package structure...")
print("=" * 60)

# Test basic imports
try:
    print("\n✅ Testing core modules...")
    from sentio.core import config
    print("   ✓ sentio.core.config")
    from sentio.core import logger
    print("   ✓ sentio.core.logger")
    
    print("\n✅ Testing strategy modules...")
    from sentio.strategies import base
    print("   ✓ sentio.strategies.base")
    
    print("\n✅ Testing other modules...")
    from sentio import risk
    print("   ✓ sentio.risk")
    from sentio import execution
    print("   ✓ sentio.execution")
    from sentio import analysis
    print("   ✓ sentio.analysis")
    from sentio import data
    print("   ✓ sentio.data")
    from sentio import ai
    print("   ✓ sentio.ai")
    from sentio import longtermInvestment
    print("   ✓ sentio.longtermInvestment")
    from sentio import political
    print("   ✓ sentio.political")
    from sentio import ui
    print("   ✓ sentio.ui")
    from sentio import billing
    print("   ✓ sentio.billing")
    from sentio import utils
    print("   ✓ sentio.utils")
    
    print("\n" + "=" * 60)
    print("✅ All package imports successful!")
    print("=" * 60)
    print("\n📦 Package structure is correctly set up")
    print("📝 Dependencies need to be installed: pip install -r requirements.txt")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
