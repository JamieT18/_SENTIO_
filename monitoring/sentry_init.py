"""
Sentry error tracking integration for Sentio backend
"""
import sentry_sdk

def init_sentry():
    sentry_sdk.init(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        traces_sample_rate=1.0,
    )
