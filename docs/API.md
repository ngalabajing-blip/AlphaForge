# AlphaForge — API reference

The API service exposes three concurrent surfaces:

* **REST** under `/api/v1/...`
* **GraphQL** at `/graphql`
* **WebSocket subscriptions** under `/ws/...`

OpenAPI is served at `/api/v1/openapi.json` and the Swagger UI at
`/docs` (only when `app_env != production`).

## Authentication

| Mechanism      | Header                       | Where used                      |
|----------------|------------------------------|---------------------------------|
| OAuth2 access  | `Authorization: Bearer <jwt>`| End users, browser clients      |
| API key        | `X-API-Key: afk_<token>`     | Server-to-server, CLI, scripts  |

```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secret
```

Returns `{ access_token, refresh_token, expires_in, token_type: "bearer" }`.

## REST endpoints

### Strategies

| Method | Path                                        | Roles                |
|--------|---------------------------------------------|----------------------|
| GET    | `/strategies`                               | any                  |
| POST   | `/strategies`                               | researcher, admin    |
| GET    | `/strategies/{id}`                          | any                  |
| PATCH  | `/strategies/{id}`                          | researcher, admin    |
| DELETE | `/strategies/{id}`                          | researcher, admin    |
| POST   | `/strategies/{id}/versions`                 | researcher, admin    |
| GET    | `/strategies/{id}/versions/{version}`       | any                  |
| POST   | `/strategies/{id}/dry-run`                  | researcher, admin    |

### Backtests

| Method | Path                            | Notes                                  |
|--------|---------------------------------|----------------------------------------|
| GET    | `/backtests`                    | filter by strategy_id, status, paging  |
| POST   | `/backtests`                    | enqueue a new backtest job             |
| GET    | `/backtests/{id}`               | full result + trades                   |
| DELETE | `/backtests/{id}`               | cancel a queued/running backtest       |

### Signals, alerts, audits, market, chains

* `GET /signals?strategy_id=…&limit=…`
* `GET /alerts`, `POST /alerts`, `PATCH /alerts/{id}`, `DELETE /alerts/{id}`
* `GET /audits`, `POST /audits`, `GET /audits/{id}`
* `GET /market/ticker/{symbol}`, `GET /market/candles/{symbol}`,
  `GET /market/dominance`, `GET /market/movers`
* `GET /chains`

## GraphQL schema (excerpt)

```graphql
type Query {
  me: User!
  strategies(limit: Int = 50, offset: Int = 0): [Strategy!]!
  strategy(id: ID!): Strategy
  backtests(strategyId: ID, limit: Int = 50): [Backtest!]!
  backtest(id: ID!): Backtest
  signals(strategyId: ID, limit: Int = 100): [Signal!]!
  audits(limit: Int = 50): [Audit!]!
}

type Subscription {
  signals(strategyId: ID): Signal!
  backtestProgress(jobId: ID!): BacktestProgress!
  anomalies: Anomaly!
}
```

## WebSocket subscriptions

| URL                         | Payload                              |
|-----------------------------|--------------------------------------|
| `/ws/signals?token=…`       | `{symbol, action, strength, ts}`     |
| `/ws/anomalies?token=…`     | `{window, score, factors}`           |
| `/ws/backtests/{id}?token=…`| `{candles_processed, equity, pnl}`   |

## Error format

All errors return:

```json
{
  "type": "validation_error|auth_error|not_found|rate_limited|internal",
  "message": "human readable",
  "request_id": "01H…"
}
```
