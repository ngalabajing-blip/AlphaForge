# Security model

## Authentication

* OAuth2 password grant for users (JWT access + opaque refresh)
* API keys (`afk_<token>`) for service-to-service & CLI; SHA-256 hashed at rest
* Tokens carry `sub` (user id), `scope`, `exp`; verified on every request

## Authorisation

Role enum (Postgres):

| Role         | Capabilities                                                          |
|--------------|-----------------------------------------------------------------------|
| `admin`      | full access (user management, RBAC changes, dangerous actions)        |
| `researcher` | create strategies + run backtests, read all data                      |
| `viewer`     | read-only, can subscribe to live signals                              |
| `service`    | machine accounts: scoped scopes only (`read`, `ingest`, `notify`)     |

Each FastAPI route declares `dependencies=[Depends(require_role("..."))]`.

## Transport

* TLS termination at ingress (Helm chart configurable)
* Inter-service traffic stays inside the cluster network
* Optional mTLS via Linkerd / Istio (out of scope for this skeleton)

## Secrets

* Never commit `.env` files or production secrets.
* Helm reads from a Kubernetes `Secret`; Terraform writes RDS / Redis
  credentials to AWS Secrets Manager (left to operators).
* JWT signing key is rotated by setting `JWT_SECRET_KEY` and
  re-deploying — outstanding tokens expire naturally.

## Audit logging

* Every sensitive route writes a row to `audit_log` (user, action,
  resource, IP, ts).
* Notifier records every delivery attempt in `alert_deliveries`.
* Auditor service publishes findings to `T_AUDIT_REPORT` for downstream
  archival.

## Smart contract scanner heuristics

The auditor service intentionally returns conservative findings only;
the categories of detected issues include:

* **Critical** — `selfdestruct`, direct balance writes
* **High** — `delegatecall`, `tx.origin` auth, blocklists, hidden mint
* **Medium** — fee mutators, pausable transfer, `keccak256(packed(...))`
* **Low** — owner views, hard-coded transfers, oversize bytecode
* **Info** — onlyOwner, encodePacked, fallback / receive defined

False-positive rate is non-zero — surface findings to humans, never
auto-block on findings alone.
