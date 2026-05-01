"""
Canonical chain registry.

Every supported network is described by a single :class:`ChainSpec`. Other
services consume the registry through helpers in this module — they MUST NOT
hard-code chain metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ChainFamily(str, Enum):
    EVM = "evm"
    SOLANA = "solana"
    COSMOS = "cosmos"


@dataclass(frozen=True)
class ChainSpec:
    id: str                       # short canonical id ("eth", "bsc", "sol")
    name: str                     # human name ("Ethereum", "Binance Smart Chain")
    family: ChainFamily
    chain_id: int | None          # EVM chain id (numeric); None for non-EVM
    native_symbol: str            # "ETH", "BNB", "SOL", …
    explorer: str
    block_time_seconds: float     # average block time
    finality_blocks: int          # safe number of confirmations
    rpc_http_env: str             # name of env var holding HTTP RPC
    rpc_ws_env: str               # name of env var holding WS  RPC
    explorer_api_env: str | None  # explorer API key env var (optional)
    dexes: tuple[str, ...]        # known DEXes for venue resolution


CHAINS: tuple[ChainSpec, ...] = (
    ChainSpec(
        id="eth", name="Ethereum", family=ChainFamily.EVM,
        chain_id=1, native_symbol="ETH",
        explorer="https://etherscan.io",
        block_time_seconds=12.0, finality_blocks=12,
        rpc_http_env="ETH_RPC_HTTP", rpc_ws_env="ETH_RPC_WS",
        explorer_api_env="ETHERSCAN_API_KEY",
        dexes=("uniswap-v2", "uniswap-v3", "uniswap-v4", "sushiswap", "curve", "balancer"),
    ),
    ChainSpec(
        id="bsc", name="Binance Smart Chain", family=ChainFamily.EVM,
        chain_id=56, native_symbol="BNB",
        explorer="https://bscscan.com",
        block_time_seconds=3.0, finality_blocks=15,
        rpc_http_env="BSC_RPC_HTTP", rpc_ws_env="BSC_RPC_WS",
        explorer_api_env="BSCSCAN_API_KEY",
        dexes=("pancakeswap-v2", "pancakeswap-v3", "biswap"),
    ),
    ChainSpec(
        id="polygon", name="Polygon", family=ChainFamily.EVM,
        chain_id=137, native_symbol="MATIC",
        explorer="https://polygonscan.com",
        block_time_seconds=2.0, finality_blocks=128,
        rpc_http_env="POLYGON_RPC_HTTP", rpc_ws_env="POLYGON_RPC_WS",
        explorer_api_env="POLYGONSCAN_API_KEY",
        dexes=("quickswap", "uniswap-v3", "curve"),
    ),
    ChainSpec(
        id="arbitrum", name="Arbitrum One", family=ChainFamily.EVM,
        chain_id=42161, native_symbol="ETH",
        explorer="https://arbiscan.io",
        block_time_seconds=0.25, finality_blocks=20,
        rpc_http_env="ARBITRUM_RPC_HTTP", rpc_ws_env="ARBITRUM_RPC_WS",
        explorer_api_env="ARBISCAN_API_KEY",
        dexes=("uniswap-v3", "camelot", "gmx"),
    ),
    ChainSpec(
        id="base", name="Base", family=ChainFamily.EVM,
        chain_id=8453, native_symbol="ETH",
        explorer="https://basescan.org",
        block_time_seconds=2.0, finality_blocks=20,
        rpc_http_env="BASE_RPC_HTTP", rpc_ws_env="BASE_RPC_WS",
        explorer_api_env="BASESCAN_API_KEY",
        dexes=("uniswap-v3", "aerodrome"),
    ),
    ChainSpec(
        id="optimism", name="Optimism", family=ChainFamily.EVM,
        chain_id=10, native_symbol="ETH",
        explorer="https://optimistic.etherscan.io",
        block_time_seconds=2.0, finality_blocks=20,
        rpc_http_env="OPTIMISM_RPC_HTTP", rpc_ws_env="OPTIMISM_RPC_WS",
        explorer_api_env=None,
        dexes=("uniswap-v3", "velodrome"),
    ),
    ChainSpec(
        id="avalanche", name="Avalanche C-Chain", family=ChainFamily.EVM,
        chain_id=43114, native_symbol="AVAX",
        explorer="https://snowtrace.io",
        block_time_seconds=2.0, finality_blocks=20,
        rpc_http_env="AVALANCHE_RPC_HTTP", rpc_ws_env="AVALANCHE_RPC_WS",
        explorer_api_env="SNOWTRACE_API_KEY",
        dexes=("traderjoe", "pangolin", "uniswap-v3"),
    ),
    ChainSpec(
        id="sol", name="Solana", family=ChainFamily.SOLANA,
        chain_id=None, native_symbol="SOL",
        explorer="https://solscan.io",
        block_time_seconds=0.4, finality_blocks=32,
        rpc_http_env="SOLANA_RPC_HTTP", rpc_ws_env="SOLANA_RPC_WS",
        explorer_api_env="SOLSCAN_API_KEY",
        dexes=("raydium", "orca", "jupiter"),
    ),
    ChainSpec(
        id="cosmos", name="Cosmos Hub", family=ChainFamily.COSMOS,
        chain_id=None, native_symbol="ATOM",
        explorer="https://www.mintscan.io/cosmos",
        block_time_seconds=6.0, finality_blocks=1,
        rpc_http_env="COSMOS_RPC_HTTP", rpc_ws_env="COSMOS_RPC_HTTP",
        explorer_api_env=None,
        dexes=("osmosis",),
    ),
)


_BY_ID: dict[str, ChainSpec] = {c.id: c for c in CHAINS}
_BY_CHAIN_ID: dict[int, ChainSpec] = {c.chain_id: c for c in CHAINS if c.chain_id is not None}


def get_chain(chain_id: str) -> ChainSpec:
    """Look up a chain by short id ("eth", "bsc"). Raises KeyError if unknown."""
    if chain_id not in _BY_ID:
        raise KeyError(f"Unknown chain id: {chain_id!r}. Known ids: {sorted(_BY_ID)}")
    return _BY_ID[chain_id]


def get_chain_by_evm_id(chain_id: int) -> ChainSpec:
    """Look up an EVM chain by numeric chain id."""
    if chain_id not in _BY_CHAIN_ID:
        raise KeyError(f"Unknown EVM chain id: {chain_id}")
    return _BY_CHAIN_ID[chain_id]


def all_chains() -> Iterable[ChainSpec]:
    return CHAINS


def evm_chains() -> Iterable[ChainSpec]:
    return tuple(c for c in CHAINS if c.family is ChainFamily.EVM)


def supports_chain(chain_id: str) -> bool:
    return chain_id in _BY_ID
