import pytest

from alphaforge_shared.chains import (
    ChainFamily,
    all_chains,
    evm_chains,
    get_chain,
    get_chain_by_evm_id,
    supports_chain,
)


def test_known_chain_lookup():
    eth = get_chain("eth")
    assert eth.chain_id == 1
    assert eth.family is ChainFamily.EVM
    assert "uniswap-v3" in eth.dexes


def test_evm_lookup_by_numeric_id():
    assert get_chain_by_evm_id(56).id == "bsc"


def test_unknown_chain_raises():
    with pytest.raises(KeyError):
        get_chain("doge")


def test_all_chains_includes_solana_and_cosmos():
    ids = {c.id for c in all_chains()}
    assert {"sol", "cosmos"}.issubset(ids)


def test_evm_chains_excludes_solana():
    assert all(c.family is ChainFamily.EVM for c in evm_chains())


def test_supports_chain():
    assert supports_chain("eth")
    assert not supports_chain("unknown")
