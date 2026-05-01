# Security policy

## Reporting a vulnerability

Please email `security@alphaforge.local` with details. We aim to
acknowledge any report within 48 hours.

If the vulnerability is in a third-party dependency, please file a
ticket with that project as well.

## Supported versions

| Version | Status     |
|---------|------------|
| `main`  | supported  |
| `0.1.x` | supported  |

## Cryptographic primitives

* Passwords stored as `argon2id` hashes (`passlib`)
* JWTs signed with `HS256` using `JWT_SECRET_KEY`
* API keys hashed with SHA-256 (the only stored form)
* Webhook signatures use HMAC-SHA256 with per-channel secrets

See `docs/SECURITY.md` for the full security model.
