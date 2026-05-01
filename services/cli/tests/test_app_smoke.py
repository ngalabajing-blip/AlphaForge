from alphaforge_cli.app import app
from typer.testing import CliRunner

runner = CliRunner()


def test_root_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "alphaforge" in result.stdout.lower()


def test_subcommands_registered():
    result = runner.invoke(app, ["--help"])
    for cmd in (
        "auth",
        "strategies",
        "backtests",
        "signals",
        "audits",
        "market",
        "chains",
    ):
        assert cmd in result.stdout
