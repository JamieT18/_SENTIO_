#!/usr/bin/env python3
"""
Generate Postman collection for Sentio API

This script creates a Postman collection with all API endpoints for easy testing.
"""
import json
import os


def create_postman_collection():
    """Create Postman collection for Sentio API"""
    
    collection = {
        "info": {
            "name": "Sentio Trading API",
            "description": "Complete collection of Sentio Trading API endpoints",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "version": "2.0.0"
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "token",
                "value": "",
                "type": "string"
            }
        ],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{token}}",
                    "type": "string"
                }
            ]
        },
        "item": [
            {
                "name": "Authentication",
                "item": [
                    {
                        "name": "Login",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "if (pm.response.code === 200) {",
                                        "    const response = pm.response.json();",
                                        "    pm.collectionVariables.set('token', response.access_token);",
                                        "    pm.environment.set('token', response.access_token);",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "username": "admin",
                                    "password": "admin123"
                                }, indent=2),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/auth/login",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "auth", "login"]
                            },
                            "description": "Login and obtain JWT token"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "General",
                "item": [
                    {
                        "name": "Health Check",
                        "request": {
                            "auth": {"type": "noauth"},
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/health",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "health"]
                            },
                            "description": "Check API health status"
                        },
                        "response": []
                    },
                    {
                        "name": "System Status",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/status",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "status"]
                            },
                            "description": "Get system status and metrics"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Trading",
                "item": [
                    {
                        "name": "Analyze Symbol",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"symbol": "AAPL"}, indent=2),
                                "options": {"raw": {"language": "json"}}
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/analyze",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "analyze"]
                            },
                            "description": "Analyze a stock symbol"
                        },
                        "response": []
                    },
                    {
                        "name": "Execute Trade",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "symbol": "AAPL",
                                    "action": "buy",
                                    "quantity": 100,
                                    "price": 150.00
                                }, indent=2),
                                "options": {"raw": {"language": "json"}}
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/trade",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "trade"]
                            },
                            "description": "Execute a trade"
                        },
                        "response": []
                    },
                    {
                        "name": "Get Positions",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/positions",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "positions"]
                            },
                            "description": "Get open positions"
                        },
                        "response": []
                    },
                    {
                        "name": "Get Performance",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/performance",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "performance"]
                            },
                            "description": "Get performance metrics"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Strategies",
                "item": [
                    {
                        "name": "Get Strategies",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/strategies",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "strategies"]
                            },
                            "description": "Get list of available strategies"
                        },
                        "response": []
                    },
                    {
                        "name": "Toggle Strategy",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"enabled": True}, indent=2),
                                "options": {"raw": {"language": "json"}}
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/strategies/momentum/toggle",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "strategies", "momentum", "toggle"]
                            },
                            "description": "Enable or disable a strategy"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Market Intelligence",
                "item": [
                    {
                        "name": "Insider Trades",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/insider-trades/AAPL?limit=10",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "insider-trades", "AAPL"],
                                "query": [{"key": "limit", "value": "10"}]
                            },
                            "description": "Get insider trades for a symbol"
                        },
                        "response": []
                    },
                    {
                        "name": "Top Insider Symbols",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/insider-trades/top?limit=10",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "insider-trades", "top"],
                                "query": [{"key": "limit", "value": "10"}]
                            },
                            "description": "Get top insider-traded symbols"
                        },
                        "response": []
                    },
                    {
                        "name": "Fundamental Analysis",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/fundamental/AAPL",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "fundamental", "AAPL"]
                            },
                            "description": "Get fundamental analysis for a symbol"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Dashboard",
                "item": [
                    {
                        "name": "Trade Signals",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/trade-signals?symbols=AAPL,GOOGL,MSFT",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "trade-signals"],
                                "query": [{"key": "symbols", "value": "AAPL,GOOGL,MSFT"}]
                            },
                            "description": "Get trade signals for multiple symbols"
                        },
                        "response": []
                    },
                    {
                        "name": "Earnings Summary",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/earnings?user_id=user_123",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "earnings"],
                                "query": [{"key": "user_id", "value": "user_123"}]
                            },
                            "description": "Get earnings summary for a user"
                        },
                        "response": []
                    },
                    {
                        "name": "AI Summary",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/ai-summary?symbol=AAPL",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "ai-summary"],
                                "query": [{"key": "symbol", "value": "AAPL"}]
                            },
                            "description": "Get AI-generated trade summary"
                        },
                        "response": []
                    },
                    {
                        "name": "Strength Signal",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/strength-signal",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "strength-signal"]
                            },
                            "description": "Get market strength signal"
                        },
                        "response": []
                    },
                    {
                        "name": "Trade Journal - Get",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/trade-journal?user_id=user_123&limit=50",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "trade-journal"],
                                "query": [
                                    {"key": "user_id", "value": "user_123"},
                                    {"key": "limit", "value": "50"}
                                ]
                            },
                            "description": "Get trade journal entries"
                        },
                        "response": []
                    },
                    {
                        "name": "Trade Journal - Add",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "user_id": "user_123",
                                    "symbol": "AAPL",
                                    "action": "buy",
                                    "quantity": 100,
                                    "price": 150.00,
                                    "notes": "Strong buy signal"
                                }, indent=2),
                                "options": {"raw": {"language": "json"}}
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/trade-journal",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "trade-journal"]
                            },
                            "description": "Add trade journal entry"
                        },
                        "response": []
                    },
                    {
                        "name": "Performance Cards",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/dashboard/performance-cards?user_id=user_123",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "dashboard", "performance-cards"],
                                "query": [{"key": "user_id", "value": "user_123"}]
                            },
                            "description": "Get performance cards"
                        },
                        "response": []
                    }
                ]
            },
            {
                "name": "Subscription",
                "item": [
                    {
                        "name": "Get Pricing",
                        "request": {
                            "auth": {"type": "noauth"},
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/subscription/pricing",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "subscription", "pricing"]
                            },
                            "description": "Get subscription pricing information"
                        },
                        "response": []
                    },
                    {
                        "name": "Get Subscription",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/subscription/user_123",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "subscription", "user_123"]
                            },
                            "description": "Get user subscription details"
                        },
                        "response": []
                    },
                    {
                        "name": "Calculate Profit Sharing",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "user_id": "user_123",
                                    "profit": 1000.00
                                }, indent=2),
                                "options": {"raw": {"language": "json"}}
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/subscription/profit-sharing/calculate",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "subscription", "profit-sharing", "calculate"]
                            },
                            "description": "Calculate profit sharing fee"
                        },
                        "response": []
                    },
                    {
                        "name": "Get Profit Sharing Balance",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/subscription/profit-sharing/user_123",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "subscription", "profit-sharing", "user_123"]
                            },
                            "description": "Get profit sharing balance"
                        },
                        "response": []
                    }
                ]
            }
        ]
    }
    
    return collection


def main():
    """Generate and save Postman collection"""
    try:
        collection = create_postman_collection()
        
        # Save to file
    output_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'postman_collection.json')
        with open(output_file, 'w') as f:
            json.dump(collection, f, indent=2)
        
        print("✅ Postman collection generated successfully!")
        print(f"📄 Saved to: {output_file}")
        
        # Count endpoints
        total_endpoints = sum(len(folder['item']) for folder in collection['item'])
        print(f"📊 {total_endpoints} endpoints included")
        
        print("\n📖 Import Instructions:")
        print("1. Open Postman")
        print("2. Click 'Import' button")
        print("3. Select 'postman_collection.json'")
        print("4. The collection will be ready to use!")
        print("\n💡 Tip: Update the 'base_url' variable if your API is not at localhost:8000")
        
    except Exception as e:
        print(f"❌ Error generating Postman collection: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
