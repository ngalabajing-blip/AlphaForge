# Deployment

## Local development

```bash
# bring up Postgres, Redis, Kafka, ClickHouse + all services
docker-compose -f docker-compose.dev.yml up --build

# initialise the database
docker-compose exec api alembic upgrade head

# run the frontend separately for hot-reload
cd frontend && npm install && npm run dev
```

The frontend dev server proxies `/api`, `/graphql`, and `/ws` to the
API container.

## Production via Helm

```bash
kubectl create namespace alphaforge
helm upgrade --install alphaforge infra/helm/alphaforge \
  --namespace alphaforge \
  --set secrets.jwtSecretKey=$(openssl rand -hex 32) \
  --set config.databaseUrl=postgresql+asyncpg://… \
  --set services.frontend.ingress.host=app.example.com \
  --set services.api.ingress.host=api.example.com
```

The chart provisions every backend service, the frontend, ConfigMap,
Secret, Ingress, and HPA. Postgres / Redis / Kafka / ClickHouse can
either be enabled in-cluster (default) or pointed at managed services
via `config.databaseUrl` / `config.redisUrl`.

## Cloud (AWS) via Terraform

```bash
cd infra/terraform
terraform init
terraform apply -var "db_password=$(openssl rand -hex 24)"
aws eks update-kubeconfig --name alphaforge-production
```

The Terraform stack provisions:

* VPC with 3 AZ public/private subnets and NAT gateways
* EKS 1.30 + managed node group
* RDS Postgres (multi-AZ, encrypted)
* ElastiCache Redis (multi-AZ, encrypted at-rest + in-flight)
* S3 bucket for artefacts (versioning + SSE)

After `terraform apply` completes, run the Helm command above pointing
at the freshly provisioned RDS endpoint.

## Database migrations

Migrations live in `services/api/alembic`. The initial revision
`20260101_0001_init.py` creates every table required by all services.

```bash
alembic -c services/api/alembic.ini upgrade head
alembic -c services/api/alembic.ini revision -m "add_new_column"
```

## Backups

* RDS: automated 7-day backups + a daily manual snapshot
* ClickHouse: filesystem-level snapshots (`clickhouse-backup` recommended)
* S3 versioning is enabled so build artefacts are recoverable
