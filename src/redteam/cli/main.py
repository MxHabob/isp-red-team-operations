"""CLI — command-line interface for the Red Team platform.

Provides the ``redteam`` command with subcommands for all major operations:

    redteam scope validate
    redteam safety check
    redteam scenario list
    redteam run dry-run --scenario ACC-001
    redteam evidence verify
    redteam finding list
    redteam validate all
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from redteam.core.config import PlatformConfig
from redteam.core.errors import RedTeamError


def _setup_logging(verbose: bool) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """ISP Red Team Operations — Security Research Platform."""
    _setup_logging(verbose)
    ctx.ensure_object(dict)
    try:
        ctx.obj["config"] = PlatformConfig()
    except RedTeamError as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Scope commands
# ---------------------------------------------------------------------------


@cli.group()
def scope() -> None:
    """Scope management."""


@scope.command("validate")
@click.pass_context
def scope_validate(ctx: click.Context) -> None:
    """Validate the current scope definition."""
    from redteam.scope.engine import ScopeEngine

    config: PlatformConfig = ctx.obj["config"]
    engine = ScopeEngine()

    try:
        engine.load(config.scope_file)
        issues = engine.validate()

        if issues:
            click.echo("Scope validation issues:")
            for issue in issues:
                click.echo(f"  ⚠ {issue}")
        else:
            click.echo("✓ Scope validation passed")
    except RedTeamError as exc:
        click.echo(f"✗ Scope error: {exc}", err=True)
        sys.exit(1)


@scope.command("show")
@click.pass_context
def scope_show(ctx: click.Context) -> None:
    """Show the current scope definition."""
    from redteam.scope.engine import ScopeEngine

    config: PlatformConfig = ctx.obj["config"]
    engine = ScopeEngine()

    try:
        s = engine.load(config.scope_file)
        click.echo(f"Operation:  {s.operation_id}")
        click.echo(f"Name:       {s.name}")
        click.echo(f"Status:     {s.status}")
        click.echo(f"Environment: {s.environment.value}")
        click.echo(f"Assets:     {len(s.authorized_assets)}")
        click.echo(f"Networks:   {len(s.authorized_networks)}")
        click.echo(f"Allowed:    {len(s.allowed_activity)}")
        click.echo(f"Prohibited: {len(s.prohibited_activity)}")
    except RedTeamError as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Safety commands
# ---------------------------------------------------------------------------


@cli.group()
def safety() -> None:
    """Safety and kill switch management."""


@safety.command("check")
@click.pass_context
def safety_check(ctx: click.Context) -> None:
    """Run all safety checks."""
    from redteam.safety.engine import SafetyEngine
    from redteam.safety.killswitch import KillSwitch
    from redteam.scope.engine import ScopeEngine

    config: PlatformConfig = ctx.obj["config"]

    try:
        scope_engine = ScopeEngine()
        scope_engine.load(config.scope_file)

        ks = KillSwitch(config.runtime_dir / "killswitch.json")
        engine = SafetyEngine(ks)

        report = engine.run_checks(
            scope_engine.scope, config.environment, config.evidence_store
        )
        click.echo("Safety checks:")
        click.echo(report.summary())
        if report.passed:
            click.echo("\n✓ All safety checks passed")
        else:
            click.echo("\n✗ Safety checks FAILED")
            sys.exit(1)
    except RedTeamError as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)


@safety.command("killswitch")
@click.argument("action", type=click.Choice(["status", "activate", "pause", "stop", "abort"]))
@click.option("--operator", default="cli", help="Operator identity.")
@click.option("--reason", default="", help="Reason for the action.")
@click.pass_context
def safety_killswitch(ctx: click.Context, action: str, operator: str, reason: str) -> None:
    """Manage the kill switch."""
    config: PlatformConfig = ctx.obj["config"]
    config.ensure_runtime_dirs()

    ks = KillSwitch(config.runtime_dir / "killswitch.json")

    if action == "status":
        click.echo(f"Kill switch state: {ks.state.value}")
    elif action == "activate":
        ks.activate(operator, reason or "Activated via CLI")
        click.echo("✓ Kill switch activated — execution allowed")
    elif action == "pause":
        ks.pause(operator, reason or "Paused via CLI")
        click.echo("⏸ Kill switch paused")
    elif action == "stop":
        ks.stop(operator, reason or "Stopped via CLI")
        click.echo("⏹ Kill switch stopped")
    elif action == "abort":
        ks.abort(operator, reason or "ABORTED via CLI")
        click.echo("🛑 KILL SWITCH ABORTED — all execution must stop")


# ---------------------------------------------------------------------------
# Scenario commands
# ---------------------------------------------------------------------------


@cli.group()
def scenario() -> None:
    """Scenario management."""


@scenario.command("list")
@click.pass_context
def scenario_list(ctx: click.Context) -> None:
    """List all registered scenarios."""
    from redteam.scenarios.engine import ScenarioEngine

    config: PlatformConfig = ctx.obj["config"]
    engine = ScenarioEngine(config.scenarios_dir)
    count = engine.load_all()

    if count == 0:
        click.echo("No scenarios found.")
        return

    for s in engine.list_all():
        click.echo(f"  {s.scenario_id:20s} {s.status.value:12s} {s.objective}")


@scenario.command("show")
@click.argument("scenario_id")
@click.pass_context
def scenario_show(ctx: click.Context, scenario_id: str) -> None:
    """Show details of a scenario."""
    from redteam.scenarios.engine import ScenarioEngine

    config: PlatformConfig = ctx.obj["config"]
    engine = ScenarioEngine(config.scenarios_dir)
    engine.load_all()

    try:
        s = engine.get(scenario_id)
        click.echo(f"ID:          {s.scenario_id}")
        click.echo(f"Version:     {s.version}")
        click.echo(f"Status:      {s.status.value}")
        click.echo(f"Objective:   {s.objective}")
        click.echo(f"Hypothesis:  {s.hypothesis}")
        click.echo(f"Steps:       {len(s.steps)}")
        click.echo(f"Expected:    {s.expected_behavior}")

        issues = engine.validate(s)
        if issues:
            click.echo("\nValidation issues:")
            for issue in issues:
                click.echo(f"  ⚠ {issue}")
    except RedTeamError as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Run commands
# ---------------------------------------------------------------------------


@cli.group()
def run() -> None:
    """Test execution."""


@run.command("dry-run")
@click.option("--scenario", "scenario_id", required=True, help="Scenario ID to execute.")
@click.option("--operator", default="cli", help="Operator identity.")
@click.pass_context
def run_dryrun(ctx: click.Context, scenario_id: str, operator: str) -> None:
    """Execute a scenario in dry-run mode (no network actions)."""
    from redteam.runtime.runner import TestRunner
    from redteam.safety.engine import SafetyEngine
    from redteam.safety.killswitch import KillSwitch
    from redteam.scenarios.engine import ScenarioEngine
    from redteam.scope.engine import ScopeEngine

    config: PlatformConfig = ctx.obj["config"]
    config.ensure_runtime_dirs()

    try:
        # Initialize engines
        scope_engine = ScopeEngine()
        scope_engine.load(config.scope_file)

        ks = KillSwitch(config.runtime_dir / "killswitch.json")
        safety_engine = SafetyEngine(ks)

        scenario_engine = ScenarioEngine(config.scenarios_dir)
        scenario_engine.load_all()
        scenario_def = scenario_engine.get(scenario_id)

        runner = TestRunner(config, scope_engine, safety_engine, ks)
        result = runner.execute(scenario_def, operator=operator, dry_run=True)

        click.echo("\n" + "=" * 60)
        click.echo(f"DRY RUN: {scenario_id}")
        click.echo("=" * 60)
        click.echo(result.lifecycle.summary())
        click.echo("\nObservations:")
        for obs in result.observations:
            click.echo(f"  {obs}")

        if result.success:
            click.echo("\n✓ Dry run completed successfully")
        else:
            click.echo("\n✗ Dry run completed with errors:")
            for err in result.errors:
                click.echo(f"  ✗ {err}")
            sys.exit(1)

    except RedTeamError as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)


@run.command("execute")
@click.option("--scenario", "scenario_id", required=True, help="Scenario ID to execute.")
@click.option("--operator", default="cli", help="Operator identity.")
@click.pass_context
def run_execute(ctx: click.Context, scenario_id: str, operator: str) -> None:
    """Execute a scenario in the authorized lab environment."""
    from redteam.runtime.runner import TestRunner
    from redteam.safety.engine import SafetyEngine
    from redteam.safety.killswitch import KillSwitch
    from redteam.scenarios.engine import ScenarioEngine
    from redteam.scope.engine import ScopeEngine

    config: PlatformConfig = ctx.obj["config"]
    config.ensure_runtime_dirs()

    try:
        # Initialize engines
        scope_engine = ScopeEngine()
        scope_engine.load(config.scope_file)

        ks = KillSwitch(config.runtime_dir / "killswitch.json")
        safety_engine = SafetyEngine(ks)

        scenario_engine = ScenarioEngine(config.scenarios_dir)
        scenario_engine.load_all()
        scenario_def = scenario_engine.get(scenario_id)

        runner = TestRunner(config, scope_engine, safety_engine, ks)
        result = runner.execute(scenario_def, operator=operator, dry_run=False)

        click.echo("\n" + "=" * 60)
        click.echo(f"EXECUTION: {scenario_id}")
        click.echo("=" * 60)
        click.echo(result.lifecycle.summary())
        click.echo("\nObservations:")
        for obs in result.observations:
            click.echo(f"  {obs}")

        if result.evidence_ids:
            click.echo("\nEvidence:")
            for evid in result.evidence_ids:
                click.echo(f"  [+] {evid}")

        if result.success:
            click.echo("\n✓ Scenario executed successfully")
        else:
            click.echo("\n✗ Execution completed with errors:")
            for err in result.errors:
                click.echo(f"  ✗ {err}")
            sys.exit(1)

    except RedTeamError as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Evidence commands
# ---------------------------------------------------------------------------


@cli.group()
def evidence() -> None:
    """Evidence management."""


@evidence.command("verify")
@click.argument("evidence_id")
@click.pass_context
def evidence_verify(ctx: click.Context, evidence_id: str) -> None:
    """Verify the integrity of an evidence item."""
    click.echo(f"Evidence verification for {evidence_id}: TODO — implement after evidence registration")


# ---------------------------------------------------------------------------
# Finding commands
# ---------------------------------------------------------------------------


@cli.group()
def finding() -> None:
    """Finding management."""


@finding.command("list")
@click.pass_context
def finding_list(ctx: click.Context) -> None:
    """List all findings."""
    from redteam.findings.manager import FindingManager

    config: PlatformConfig = ctx.obj["config"]
    manager = FindingManager(config.project_root / "findings" / "records")
    count = manager.load_from_directory()

    if count == 0:
        click.echo("No findings recorded.")
        return

    for f in manager.list_all():
        click.echo(
            f"  {f.finding_id:15s} {f.severity.value:12s} {f.status.value:12s} {f.title}"
        )


# ---------------------------------------------------------------------------
# Validate commands
# ---------------------------------------------------------------------------


@cli.group()
def validate() -> None:
    """Validation and verification."""


@validate.command("all")
@click.pass_context
def validate_all(ctx: click.Context) -> None:
    """Run all validation checks."""
    config: PlatformConfig = ctx.obj["config"]
    errors: list[str] = []

    click.echo("Running validation checks...")

    # 1. Check required files
    required_files = [
        "AGENTS.md",
        "README.md",
        "SECURITY.md",
        "command/scope.yaml",
        "command/roe.md",
        "command/mission.yaml",
        "pyproject.toml",
    ]
    for f in required_files:
        path = config.project_root / f
        if path.exists():
            click.echo(f"  ✓ {f}")
        else:
            click.echo(f"  ✗ {f} — missing")
            errors.append(f"Missing required file: {f}")

    # 2. Check for forbidden files
    import glob

    forbidden_patterns = ["*.pem", "*.key", "*.p12", "*.pfx", "*.pcap", "*.pcapng"]
    for pattern in forbidden_patterns:
        matches = list(config.project_root.rglob(pattern))
        matches = [m for m in matches if ".git" not in str(m) and ".local" not in str(m)]
        if matches:
            for m in matches:
                click.echo(f"  ✗ Forbidden file: {m}")
                errors.append(f"Forbidden file in repo: {m}")

    # 3. Check .env files
    env_files = list(config.project_root.rglob(".env"))
    env_files += list(config.project_root.rglob(".env.*"))
    env_files = [
        f for f in env_files
        if ".git" not in str(f)
        and ".local" not in str(f)
        and f.name != ".env.example"
    ]
    if env_files:
        for f in env_files:
            click.echo(f"  ✗ Secret file: {f}")
            errors.append(f"Secret file in repo: {f}")

    if errors:
        click.echo(f"\n✗ Validation failed with {len(errors)} error(s)")
        sys.exit(1)
    else:
        click.echo("\n✓ All validation checks passed")


# ---------------------------------------------------------------------------
# Mission command
# ---------------------------------------------------------------------------


@cli.command("mission")
@click.pass_context
def mission_show(ctx: click.Context) -> None:
    """Show the current mission."""
    import yaml

    config: PlatformConfig = ctx.obj["config"]
    try:
        raw = yaml.safe_load(config.mission_file.read_text(encoding="utf-8"))
        click.echo(f"Operation:  {raw.get('operation_id', 'N/A')}")
        click.echo(f"Name:       {raw.get('name', 'N/A')}")
        click.echo(f"Phase:      {raw.get('phase', 'N/A')}")
        click.echo(f"Status:     {raw.get('status', 'N/A')}")
        objectives = raw.get("objectives", [])
        if objectives:
            click.echo("Objectives:")
            for obj in objectives:
                click.echo(f"  - {obj}")
    except Exception as exc:
        click.echo(f"✗ Error reading mission: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
