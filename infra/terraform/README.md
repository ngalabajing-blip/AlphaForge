# AlphaForge Terraform (AWS)

Skeleton stack provisioning the cloud foundations needed for AlphaForge:

* VPC with public + private subnets across 3 AZs and NAT gateways
* EKS cluster (1.30) with managed node group
* RDS Postgres (multi-AZ, encrypted)
* ElastiCache Redis (cluster mode disabled, multi-node, in-flight + at-rest encryption)
* S3 bucket for build artefacts and backtest equity dumps

## Usage

```bash
cd infra/terraform
terraform init
terraform apply -var "db_password=<secret>"
```

Then point the Helm chart at the new EKS cluster:

```bash
aws eks update-kubeconfig --name alphaforge-production --region us-east-1
helm upgrade --install alphaforge ../helm/alphaforge \
  --namespace alphaforge --create-namespace \
  --set config.databaseUrl="postgresql+asyncpg://alphaforge:<secret>@<rds-endpoint>:5432/alphaforge"
```
