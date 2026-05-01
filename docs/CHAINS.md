# Supported chains

The ingestor service understands three protocol families:

| Chain        | Family   | RPC type            | Block time |
|--------------|----------|---------------------|------------|
| Ethereum     | EVM      | JSON-RPC + WS       | 12s        |
| BSC          | EVM      | JSON-RPC + WS       | 3s         |
| Polygon      | EVM      | JSON-RPC + WS       | 2s         |
| Arbitrum One | EVM      | JSON-RPC            | 0.25s      |
| Optimism     | EVM      | JSON-RPC            | 2s         |
| Base         | EVM      | JSON-RPC            | 2s         |
| Avalanche    | EVM      | JSON-RPC            | 2s         |
| Solana       | Solana   | JSON-RPC + WS       | 0.4s       |
| Cosmos Hub   | Cosmos   | Tendermint RPC      | 6s         |

For each chain the ingestor tracks:

* New blocks → `T_BLOCKS`
* Decoded transactions → `T_TRANSACTIONS`
* Logs of interest (DEX trades, transfers, oracle updates) → `T_LOGS`
* DEX trade reconstructions → `T_DEX_TRADES`
* Liquidity deltas (mints / burns / swaps) → `T_LIQUIDITY_DELTAS`

## Adding a new chain

1. Add a new entry to `services/ingestor/src/alphaforge_ingestor/chains.py`
   with `chain_id`, `rpc_url`, family, and finality delay.
2. Pick the right adapter: `evm_adapter`, `solana_adapter`, or
   `cosmos_adapter` — write a new one only if the protocol differs.
3. Update `shared/src/alphaforge_shared/chains.py` so the API and
   workers know about the new chain.
4. Add example fixtures under `examples/chains/` and a test under
   `services/ingestor/tests/`.

## Rate-limit strategy

Every adapter wraps RPC calls in an exponential-backoff `tenacity`
retry. JSON-RPC providers are rotated when 429s exceed
`INGESTOR_RPC_BACKOFF_THRESHOLD` over a 60s window — the next call
goes to the secondary endpoint.
