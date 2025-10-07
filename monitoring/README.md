# Sentio Monitoring & Alerting

## Prometheus Setup
- Use `prometheus_config.py` to expose metrics on port 8001.
- Add `prometheus_alerts.yml` to your Prometheus config for error rate and latency alerts.

## Grafana Setup
- Import `grafana_dashboard.json` for system health and error rate panels.

## Alerting
- Alerts for high error rate and latency are defined in `prometheus_alerts.yml`.
- Integrate with Slack, email, or PagerDuty for notifications.

## Sentry
- Sentry is integrated in both backend and frontend for error tracking.
- Configure your DSN in `sentry_init.py` and `sentry.js`.
