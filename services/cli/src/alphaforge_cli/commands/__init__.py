"""CLI subcommand groups."""
from alphaforge_cli.commands.auth import auth_app
from alphaforge_cli.commands.audits import audits_app
from alphaforge_cli.commands.backtests import backtests_app
from alphaforge_cli.commands.market import market_app
from alphaforge_cli.commands.signals import signals_app
from alphaforge_cli.commands.strategies import strategies_app
from alphaforge_cli.commands.chains import chains_app

__all__ = [
    "auth_app",
    "audits_app",
    "backtests_app",
    "market_app",
    "signals_app",
    "strategies_app",
    "chains_app",
]
