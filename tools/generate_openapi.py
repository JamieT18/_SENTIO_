#!/usr/bin/env python3
"""
Generate OpenAPI specification from FastAPI app

This script extracts the OpenAPI spec from the Sentio API and saves it to a file.
"""
import json
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from sentio.ui.api import app
    
    # Get OpenAPI specification
    openapi_spec = app.openapi()
    
    # Save to file
    output_file = os.path.join(os.path.dirname(__file__), '..', 'openapi.json')
    with open(output_file, 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    
    print(f"✅ OpenAPI specification generated successfully!")
    print(f"📄 Saved to: {output_file}")
    print(f"📊 {len(openapi_spec.get('paths', {}))} endpoints documented")
    
except Exception as e:
    print(f"❌ Error generating OpenAPI spec: {e}", file=sys.stderr)
    print("\nNote: This requires the API dependencies to be installed.", file=sys.stderr)
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)
