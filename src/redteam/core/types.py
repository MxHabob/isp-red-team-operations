"""Core type definitions for the Red Team platform.

All enumerations, dataclasses, and type aliases used across the platform
are defined here to maintain a single source of truth for the domain model.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class OperationStatus(enum.Enum):
    """Lifecycle status of a red team operation."""

    PLANNING = "planning"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"


class KillSwitchState(enum.Enum):
    """Central kill-switch states.

    Every test runner MUST respect this state before and during execution.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    STOP_REQUESTED = "stop_requested"
    STOPPED = "stopped"
    ABORTED = "aborted"


class TestLifecyclePhase(enum.Enum):
    """Ordered phases in the test runner lifecycle."""

    PRECHECK = "precheck"
    SCOPE_CHECK = "scope_check"
    SAFETY_CHECK = "safety_check"
    ENVIRONMENT_CHECK = "environment_check"
    BASELINE = "baseline"
    EXECUTION = "execution"
    TELEMETRY = "telemetry"
    EVIDENCE = "evidence"
    ANALYSIS = "analysis"
    RESULT = "result"
    CLEANUP = "cleanup"


class DataClassification(enum.Enum):
    """Data-classification levels.

    Each level defines storage, encryption, access, retention, and export
    requirements.  See docs/data-classification/classification-policy.md.
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_RESTRICTED = "highly_restricted"


class FindingStatus(enum.Enum):
    """Finding lifecycle status."""

    DRAFT = "draft"
    VALIDATED = "validated"
    REPORTED = "reported"
    REMEDIATED = "remediated"
    RETESTED = "retested"
    CLOSED = "closed"


class FindingSeverity(enum.Enum):
    """Finding severity rating."""

    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EnvironmentProfile(enum.Enum):
    """Supported environment profiles.

    ``production`` MUST NOT be the default and requires explicit
    authorization context.
    """

    LAB = "lab"
    DEVELOPMENT = "development"
    STAGING = "staging"
    AUTHORIZED_FIELD = "authorized-field"
    PRODUCTION = "production"


class EvidenceType(enum.Enum):
    """Type of evidence artifact."""

    PCAP = "pcap"
    LOG = "log"
    SCREENSHOT = "screenshot"
    MEASUREMENT = "measurement"
    CONFIGURATION = "configuration"
    EXPORT = "export"
    DERIVED = "derived"
    METADATA = "metadata"


class TelemetryEventType(enum.Enum):
    """Categories for telemetry events."""

    NETWORK = "network"
    DNS = "dns"
    TLS = "tls"
    SYSTEM = "system"
    SESSION = "session"
    ACCOUNTING = "accounting"
    TEST_EXECUTION = "test_execution"
    SECURITY = "security"


class ScenarioStatus(enum.Enum):
    """Scenario implementation status."""

    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    DEPRECATED = "deprecated"


class HypothesisConfidence(enum.Enum):
    """Confidence level for research hypotheses."""

    UNCONFIRMED = "unconfirmed"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"


# ---------------------------------------------------------------------------
# Dataclasses — Scope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuthorizedAsset:
    """An asset explicitly authorized for testing."""

    name: str
    type: str  # account, network, device, endpoint
    identifier: str


@dataclass(frozen=True)
class ScopeDefinition:
    """Parsed scope from command/scope.yaml."""

    operation_id: str
    name: str
    status: str
    authorized_assets: list[AuthorizedAsset] = field(default_factory=list)
    authorized_networks: list[str] = field(default_factory=list)
    excluded_assets: list[str] = field(default_factory=list)
    allowed_activity: list[str] = field(default_factory=list)
    prohibited_activity: list[str] = field(default_factory=list)
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    operators: list[str] = field(default_factory=list)
    approval_ref: str | None = None
    environment: EnvironmentProfile = EnvironmentProfile.LAB


# ---------------------------------------------------------------------------
# Dataclasses — Test Identity
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TestIdentity:
    """A controlled test identity for authorized testing.

    Real customer accounts MUST NEVER be used without explicit written
    authorization.
    """

    identity_id: str  # e.g. TEST-ACCOUNT-001
    role: str
    permissions: list[str] = field(default_factory=list)
    service_profile: str = ""
    quota: str = ""
    network_profile: str = ""


# ---------------------------------------------------------------------------
# Dataclasses — Evidence
# ---------------------------------------------------------------------------


@dataclass
class EvidenceRecord:
    """Metadata for a single evidence artifact.

    Raw evidence is stored externally; only metadata lives in Git.
    """

    evidence_id: str  # e.g. EV-ACC-001-0001
    test_id: str
    operation_id: str
    run_id: str
    type: EvidenceType
    captured_at: datetime | None = None
    storage_ref: str = ""
    sha256: str = ""
    classification: DataClassification = DataClassification.RESTRICTED
    collector: str = ""
    operator: str = ""
    parent_evidence_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainOfCustodyEntry:
    """A single entry in an evidence chain of custody."""

    timestamp: datetime
    action: str  # collected, transferred, verified, accessed, derived
    actor: str
    evidence_id: str
    sha256: str
    notes: str = ""


# ---------------------------------------------------------------------------
# Dataclasses — Telemetry
# ---------------------------------------------------------------------------


@dataclass
class TelemetryEvent:
    """A structured telemetry event."""

    event_id: str
    operation_id: str
    run_id: str
    test_id: str
    timestamp: datetime
    source: str
    type: TelemetryEventType
    classification: DataClassification = DataClassification.INTERNAL
    data: dict[str, Any] = field(default_factory=dict)
    data_reference: str = ""


# ---------------------------------------------------------------------------
# Dataclasses — Findings
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """A validated security/business observation."""

    finding_id: str  # e.g. F-ACC-001
    title: str
    status: FindingStatus = FindingStatus.DRAFT
    severity: FindingSeverity = FindingSeverity.INFORMATIONAL
    observation: str = ""
    analysis: str = ""
    hypothesis: str = ""
    impact: str = ""
    confidence: HypothesisConfidence = HypothesisConfidence.UNCONFIRMED
    limitations: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    test_ids: list[str] = field(default_factory=list)
    recommendation: str = ""
    retest_id: str | None = None
    retest_result: str = ""


# ---------------------------------------------------------------------------
# Dataclasses — Scenario
# ---------------------------------------------------------------------------


@dataclass
class ScenarioDefinition:
    """A structured test scenario definition."""

    scenario_id: str
    version: str = "1.0"
    objective: str = ""
    hypothesis: str = ""
    risk: str = ""
    scope_ref: str = "command/scope.yaml"
    prerequisites: list[str] = field(default_factory=list)
    test_identity: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    expected_behavior: str = ""
    measurements: list[str] = field(default_factory=list)
    telemetry: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    cleanup: list[str] = field(default_factory=list)
    success_criteria: str = ""
    failure_criteria: str = ""
    status: ScenarioStatus = ScenarioStatus.PLANNED


# ---------------------------------------------------------------------------
# Dataclasses — Operation / Run
# ---------------------------------------------------------------------------


@dataclass
class OperationRecord:
    """Top-level operation record."""

    operation_id: str  # e.g. RT-YNET-001
    name: str
    status: OperationStatus = OperationStatus.PLANNING
    phase: str = ""
    objectives: list[str] = field(default_factory=list)
    scope_ref: str = "command/scope.yaml"
    roe_ref: str = "command/roe.md"
    operators: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    ended_at: datetime | None = None


@dataclass
class RunRecord:
    """A single test execution run within an operation."""

    run_id: str  # e.g. RUN-2026-000001
    operation_id: str
    scenario_id: str
    test_id: str
    operator: str = ""
    environment: EnvironmentProfile = EnvironmentProfile.LAB
    status: str = "pending"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    phase: TestLifecyclePhase = TestLifecyclePhase.PRECHECK
    evidence_ids: list[str] = field(default_factory=list)
    telemetry_ids: list[str] = field(default_factory=list)
    finding_ids: list[str] = field(default_factory=list)
    expected_result: str = ""
    observed_result: str = ""
    conclusion: str = ""
