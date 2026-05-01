# Runbook

## SLA targets

| Service     | p99 latency | uptime |
|-------------|-------------|--------|
| api         | < 250 ms    | 99.9%  |
| ingestor    | n/a         | 99.5%  |
| ml          | < 1 s       | 99.5%  |
| worker      | n/a         | 99.5%  |
| notifier    | < 5 s       | 99.5%  |
| auditor     | < 60 s/job  | 99.0%  |

## Common alerts

### `api_error_rate_high`

`rate(alphaforge_api_requests_total{status=~"5.."}[5m]) > 0.01`

1. Check pod logs: `kubectl logs -l app=alphaforge-api -n alphaforge --since 10m`
2. Inspect Postgres connection pool: `SELECT * FROM pg_stat_activity`
3. If pool is full → bump `app.api_pool_size` and rollout

### `worker_celery_backlog`

`celery_queue_length{queue="alphaforge"} > 1000`

1. Verify Redis health: `redis-cli -h redis ping`
2. Scale workers: `kubectl scale deploy alphaforge-worker --replicas=8`
3. Drain offenders: `celery -A alphaforge_worker.celery_app:celery_app inspect reserved`

### `kafka_consumer_lag`

Per-consumer-group lag from Burrow / `kafka-consumer-groups.sh`.
Investigate per service; common culprit is the ML service falling
behind — restart pods if memory limits are being hit.

### `auditor_job_timeout`

Audit jobs taking longer than `AUDITOR_DEEP_MAX_SECONDS`.

1. Check explorer rate limits — Etherscan returns `Max rate limit reached`
2. Re-issue with `--shallow` to skip source-code fetch
3. Verify the contract address is actually deployed on the requested chain

## Disaster recovery

* RDS: PITR for 7 days, snapshots restored via `aws rds restore-db-instance-to-point-in-time`
* ClickHouse: `clickhouse-backup restore` from S3
* Kafka: replay from earliest is safe — events are idempotent on the consumer side
* Frontend: stateless, redeploy any time

## On-call playbook

* Pager → check `dashboards/alphaforge-overview` first
* If suspect Kafka, check broker logs & consumer lag dashboard
* If suspect Postgres, check `pg_stat_activity` for long-running queries
* If suspect ML accuracy → flip `ML_FEATURE_FLAG_BACKEND=naive` and
  rollback to last good model from S3
