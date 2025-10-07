"""
Example: Custom analysis plugin for Sentio
"""
from sentio.analysis.plugin import analysis_plugins

def my_custom_analysis(data, regime=None, external_context=None, diagnostics=None):
    # Simple custom analysis logic with regime/context/diagnostics support
    result = {'mean_close': sum(x['close'] for x in data) / len(data)}
    result['regime'] = regime
    result['external_context'] = external_context
    result['diagnostics'] = diagnostics
    return result

analysis_plugins.register('my_custom_analysis', my_custom_analysis, regime='bull', external_context={'macro': 'positive'}, diagnostics={'error_rate': 0.01})
