"""Tests for CLI subcommands."""

from __future__ import annotations

from click.testing import CliRunner
import pytest

from redteam.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ISP Red Team Operations" in result.output


def test_cli_scope_show(runner):
    result = runner.invoke(cli, ["scope", "show"])
    assert result.exit_code == 0
    assert "RT-YNET-001" in result.output


def test_cli_scope_validate(runner):
    result = runner.invoke(cli, ["scope", "validate"])
    assert result.exit_code == 0


def test_cli_safety_check(runner):
    result = runner.invoke(cli, ["safety", "check"])
    assert result.exit_code == 0
    assert "Kill switch" in result.output


def test_cli_scenario_list(runner):
    result = runner.invoke(cli, ["scenario", "list"])
    assert result.exit_code == 0
    assert "SC-ACC-001" in result.output


def test_cli_scenario_show(runner):
    result = runner.invoke(cli, ["scenario", "show", "SC-ACC-001"])
    assert result.exit_code == 0
    assert "SC-ACC-001" in result.output
    assert "Accounting" in result.output


def test_cli_mission(runner):
    result = runner.invoke(cli, ["mission"])
    assert result.exit_code == 0
    assert "RT-YNET-001" in result.output


def test_cli_run_dry_run(runner):
    result = runner.invoke(cli, ["run", "dry-run", "--scenario", "SC-ACC-001"])
    assert result.exit_code == 0
    assert "passed" in result.output.lower() or "completed" in result.output.lower() or "dry-run" in result.output.lower()
