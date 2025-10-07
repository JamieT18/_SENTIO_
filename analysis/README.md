# Sentio Analysis Plugin System

## Overview
Sentio supports custom analytics plugins for extensibility. Register your own analysis functions and use them in dashboards or reports.

## Usage Example
```python
from sentio.analysis.plugin import analysis_plugins

def my_custom_analysis(data):
    # Custom analysis logic
    return {'mean_close': sum(x['close'] for x in data) / len(data)}

analysis_plugins.register('my_custom_analysis', my_custom_analysis)
```

## Listing Plugins
```python
print(analysis_plugins.list_plugins())
```
