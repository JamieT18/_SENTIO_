"""
Sentry error tracking config for Sentio
"""
import sentry_sdk

def init_sentry(dsn):
    sentry_sdk.init(dsn=dsn)
